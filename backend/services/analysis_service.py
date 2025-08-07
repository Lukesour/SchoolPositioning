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
        self.use_mock = False  # 使用真实的Gemini API服务
        
        # 检查Gemini API是否可用
        try:
            # 测试API连接
            test_result = self.gemini_service.analyze_competitiveness(
                UserBackground(
                    undergraduate_university="测试",
                    undergraduate_major="测试",
                    gpa=3.5,
                    gpa_scale="4.0",
                    graduation_year=2024,
                    target_countries=["美国"],
                    target_majors=["计算机科学"],
                    target_degree_type="Master"
                )
            )
            if test_result:
                logger.info("✅ Gemini API is working correctly")
                self.use_mock = False
            else:
                logger.warning("⚠️ Gemini API test failed, switching to mock service")
                self.use_mock = True
        except Exception as e:
            logger.warning(f"⚠️ Gemini API initialization failed: {e}, switching to mock service")
            self.use_mock = True
    
    def generate_analysis_report(self, user_background: UserBackground) -> Optional[AnalysisReport]:
        """Generate complete analysis report for user"""
        try:
            logger.info("Starting analysis report generation")
            
            # 检测是否应该使用模拟服务（基于之前的失败经验或配置）
            if not self.use_mock:
                logger.info("Using real Gemini API service")
            else:
                logger.info("Using mock Gemini service for demonstration")
            
            # Step 1: Find similar cases
            logger.info("Finding similar cases...")
            similar_cases = self.similarity_matcher.find_similar_cases(user_background, top_n=30)
            
            if not similar_cases:
                logger.warning("No similar cases found")
                return None
            
            logger.info(f"Found {len(similar_cases)} similar cases")
            
            # Step 2: Parallel API calls to Gemini
            logger.info("Calling Gemini API for analysis...")
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all API calls
                future_to_task = {}
                
                # 选择使用真实或模拟服务
                service = self.mock_gemini_service if self.use_mock else self.gemini_service
                
                # Task 1: Competitiveness analysis
                future_competitiveness = executor.submit(
                    service.analyze_competitiveness, user_background
                )
                future_to_task[future_competitiveness] = "competitiveness"
                
                # Task 2: School recommendations
                future_schools = executor.submit(
                    service.generate_school_recommendations, 
                    user_background, similar_cases
                )
                future_to_task[future_schools] = "schools"
                
                # Task 3: Case analyses (for top 10 cases to provide more reference)
                case_futures = []
                for i, case in enumerate(similar_cases[:10]):
                    case_data = case.get('case_data', {})
                    future_case = executor.submit(
                        service.analyze_single_case,
                        user_background, case_data
                    )
                    future_to_task[future_case] = f"case_{i}"
                    case_futures.append(future_case)
                
                # Collect results
                results = {}
                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        result = future.result(timeout=60)  # 60 second timeout
                        results[task_name] = result
                        logger.info(f"Completed task: {task_name}")
                    except Exception as e:
                        logger.error(f"Task {task_name} failed: {str(e)}")
                        # 如果是API配额错误，切换到模拟服务并重试
                        if not self.use_mock and ("429" in str(e) or "quota" in str(e).lower()):
                            logger.warning("Switching to mock service due to API quota limits")
                            self.use_mock = True
                            # 重新提交失败的任务
                            if task_name == "competitiveness":
                                result = self.mock_gemini_service.analyze_competitiveness(user_background)
                            elif task_name == "schools":
                                result = self.mock_gemini_service.generate_school_recommendations(user_background, similar_cases)
                            elif task_name.startswith("case_"):
                                case_idx = int(task_name.split("_")[1])
                                case_data = similar_cases[case_idx].get('case_data', {})
                                result = self.mock_gemini_service.analyze_single_case(user_background, case_data)
                            else:
                                result = None
                        else:
                            result = None
                        results[task_name] = result
            
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