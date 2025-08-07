import logging
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.schemas import UserBackground, AnalysisReport, CaseAnalysis
from services.similarity_matcher import SimilarityMatcher
from services.llm_service import GeminiService

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.similarity_matcher = SimilarityMatcher()
        try:
            self.gemini_service = GeminiService()
            logger.info("Initializing Analysis Service with LLM API")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise Exception("LLM service initialization failed")
    

    
    def generate_analysis_report(self, user_background: UserBackground) -> Optional[AnalysisReport]:
        """Generate complete analysis report for user"""
        try:
            logger.info("Starting analysis report generation")
            
            # Step 1: Find similar cases
            logger.info("Finding similar cases...")
            similar_cases = self.similarity_matcher.find_similar_cases(user_background, top_n=30)
            
            if not similar_cases:
                logger.warning("No similar cases found")
                return None
            
            logger.info(f"Found {len(similar_cases)} similar cases")
            
            # Step 2: Call LLM API for analysis
            logger.info("Calling LLM API for analysis...")
            
            # Task 1: Competitiveness analysis
            competitiveness = self.gemini_service.analyze_competitiveness(user_background)
            if not competitiveness:
                logger.error("Failed to get competitiveness analysis")
                return None
            logger.info("Completed task: competitiveness")
            
            # Task 2: School recommendations
            school_recommendations = self.gemini_service.generate_school_recommendations(user_background, similar_cases)
            if not school_recommendations:
                logger.error("Failed to get school recommendations")
                return None
            logger.info("Completed task: schools")
            
            # Task 3: Case analyses (处理前5个案例)
            case_analyses = []
            for i, case in enumerate(similar_cases[:5]):
                case_data = case.get('case_data', {})
                try:
                    result = self.gemini_service.analyze_single_case(user_background, case_data)
                    if result:
                        case_analyses.append(result)
                        logger.info(f"Completed case analysis {i}")
                except Exception as e:
                    logger.warning(f"Case analysis {i} failed: {str(e)}")
                    # Continue with other cases even if one fails
            
            # Step 4: Generate background improvement suggestions
            logger.info("Generating background improvement suggestions...")
            background_improvement = None
            if competitiveness and competitiveness.weaknesses:
                try:
                    background_improvement = self.gemini_service.generate_background_improvement(
                        user_background, competitiveness.weaknesses
                    )
                except Exception as e:
                    logger.warning(f"Background improvement generation failed: {str(e)}")
            
            # Step 5: Assemble final report
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
            raise Exception(f"Analysis failed: {str(e)}")
    
    def get_case_details(self, case_ids: List[int]) -> List[Dict]:
        """Get detailed information for specific cases"""
        return self.similarity_matcher.get_case_details(case_ids)
    
    def refresh_similarity_data(self):
        """Refresh similarity matching data"""
        logger.info("Refreshing similarity matching data...")
        self.similarity_matcher._load_cases()
        logger.info("Similarity matching data refreshed")