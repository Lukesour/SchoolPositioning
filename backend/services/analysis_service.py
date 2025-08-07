import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.schemas import UserBackground, AnalysisReport, CaseAnalysis
from services.similarity_matcher import SimilarityMatcher
from services.gemini_service import GeminiService
from services.mock_gemini_service import MockGeminiService

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.similarity_matcher = SimilarityMatcher()
        self.gemini_service = GeminiService()
        self.mock_gemini_service = MockGeminiService()
        self.use_mock = False  # 默认使用真实的Gemini API服务
        self.api_failure_count = 0  # 记录API失败次数
        self.max_failures_before_mock = 3  # 连续失败3次才切换到mock
        
        # 简化API可用性检测，减少误判
        logger.info("Initializing Analysis Service with real Gemini API")
    
    def _should_use_mock(self) -> bool:
        """判断是否应该使用mock服务"""
        # 只有在连续失败多次后才使用mock
        return self.api_failure_count >= self.max_failures_before_mock
    
    def _handle_api_failure(self, error: Exception):
        """处理API失败"""
        error_msg = str(error).lower()
        # 检查是否是配额错误（包括API调用失败的情况）
        if ("quota" in error_msg or "rate limit" in error_msg or "429" in error_msg or 
            "gemini api call failed" in error_msg):
            # 配额错误直接切换到mock服务
            logger.warning("API quota exceeded or API call failed, switching to mock service")
            self.api_failure_count = self.max_failures_before_mock
        elif "network" in error_msg or "timeout" in error_msg:
            # 网络错误不增加失败计数，因为可能是临时问题
            logger.warning(f"Network/timeout error: {error}")
        else:
            # 其他错误增加失败计数
            self.api_failure_count += 1
            logger.warning(f"API error, failure count: {self.api_failure_count}")
    
    def _reset_failure_count(self):
        """重置失败计数"""
        if self.api_failure_count > 0:
            logger.info(f"Resetting API failure count from {self.api_failure_count} to 0")
            self.api_failure_count = 0
    
    def generate_analysis_report(self, user_background: UserBackground) -> Optional[AnalysisReport]:
        """Generate complete analysis report for user"""
        try:
            logger.info("Starting analysis report generation")
            
            # 检查是否应该使用mock服务
            if self._should_use_mock():
                logger.info("Using mock Gemini service due to previous API failures")
                service = self.mock_gemini_service
            else:
                logger.info("Using real Gemini API service")
                service = self.gemini_service
            
            # Step 1: Find similar cases
            logger.info("Finding similar cases...")
            similar_cases = self.similarity_matcher.find_similar_cases(user_background, top_n=30)
            
            if not similar_cases:
                logger.warning("No similar cases found")
                return None
            
            logger.info(f"Found {len(similar_cases)} similar cases")
            
            # Step 2: Try real API first, fallback to mock if needed
            logger.info("Calling Gemini API for analysis...")
            
            # 先尝试使用真实API
            results = {}
            
            # Task 1: Competitiveness analysis
            try:
                result = service.analyze_competitiveness(user_background)
                results["competitiveness"] = result
                logger.info("Completed task: competitiveness")
                if not self._should_use_mock():
                    self._reset_failure_count()
            except Exception as e:
                logger.error(f"Task competitiveness failed: {str(e)}")
                self._handle_api_failure(e)
                results["competitiveness"] = None
            
            # Task 2: School recommendations
            try:
                result = service.generate_school_recommendations(user_background, similar_cases)
                results["schools"] = result
                logger.info("Completed task: schools")
                if not self._should_use_mock():
                    self._reset_failure_count()
            except Exception as e:
                logger.error(f"Task schools failed: {str(e)}")
                self._handle_api_failure(e)
                results["schools"] = None
            
            # 如果检测到配额错误，切换到mock服务并重试失败的任务
            if self._should_use_mock():
                logger.info("Switching to mock service and retrying failed tasks...")
                
                # 重试失败的任务
                if not results.get("competitiveness"):
                    try:
                        result = self.mock_gemini_service.analyze_competitiveness(user_background)
                        results["competitiveness"] = result
                        logger.info("Retried competitiveness with mock service")
                    except Exception as e:
                        logger.error(f"Mock competitiveness failed: {str(e)}")
                
                if not results.get("schools"):
                    try:
                        result = self.mock_gemini_service.generate_school_recommendations(user_background, similar_cases)
                        results["schools"] = result
                        logger.info("Retried schools with mock service")
                    except Exception as e:
                        logger.error(f"Mock schools failed: {str(e)}")
            
            # Task 3: Case analyses (简化版本，只处理前3个案例)
            case_analyses = []
            for i, case in enumerate(similar_cases[:3]):
                case_data = case.get('case_data', {})
                try:
                    result = service.analyze_single_case(user_background, case_data)
                    if result:
                        case_analyses.append(result)
                        logger.info(f"Completed case analysis {i}")
                except Exception as e:
                    logger.error(f"Case analysis {i} failed: {str(e)}")
                    self._handle_api_failure(e)
                    
                    # 如果使用mock服务，重试
                    if self._should_use_mock():
                        try:
                            result = self.mock_gemini_service.analyze_single_case(user_background, case_data)
                            if result:
                                case_analyses.append(result)
                                logger.info(f"Retried case analysis {i} with mock service")
                        except Exception as e:
                            logger.error(f"Mock case analysis {i} failed: {str(e)}")
            
            # Extract results
            competitiveness = results.get("competitiveness")
            school_recommendations = results.get("schools")
            
            # Collect case analyses
            case_analyses = []
            for i in range(10):
                case_analysis = results.get(f"case_{i}")
                if case_analysis:
                    case_analyses.append(case_analysis)
            
            # Step 4: Generate background improvement suggestions
            logger.info("Generating background improvement suggestions...")
            background_improvement = None
            if competitiveness and competitiveness.weaknesses:
                background_improvement = service.generate_background_improvement(
                    user_background, competitiveness.weaknesses
                )
            
            # Step 5: Assemble final report
            if not competitiveness or not school_recommendations:
                logger.error("Failed to get essential analysis components")
                return None
            
            report = AnalysisReport(
                competitiveness=competitiveness,
                school_recommendations=school_recommendations,
                similar_cases=case_analyses,
                background_improvement=background_improvement
            )
            
            logger.info("Analysis report generation completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}")
            return None
    
    def get_case_details(self, case_ids: List[int]) -> List[Dict]:
        """Get detailed information for specific cases"""
        return self.similarity_matcher.get_case_details(case_ids)
    
    def refresh_similarity_data(self):
        """Refresh similarity matching data"""
        logger.info("Refreshing similarity matching data...")
        self.similarity_matcher._load_cases()
        logger.info("Similarity matching data refreshed")