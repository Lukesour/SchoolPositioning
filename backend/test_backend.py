#!/usr/bin/env python3
"""
Test script for backend functionality
"""
import sys
import os
sys.path.append('.')

from models.schemas import UserBackground
from services.analysis_service import AnalysisService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_similarity_matcher():
    """Test similarity matcher functionality"""
    logger.info("Testing similarity matcher...")
    
    try:
        from services.similarity_matcher import SimilarityMatcher
        matcher = SimilarityMatcher()
        
        # Create test user background
        user_background = UserBackground(
            undergraduate_university="北京邮电大学",
            undergraduate_major="计算机科学与技术",
            gpa=3.5,
            gpa_scale="4.0",
            graduation_year=2024,
            language_test_type="TOEFL",
            language_total_score=100,
            target_countries=["美国", "英国"],
            target_majors=["计算机科学"],
            target_degree_type="Master",
            research_experiences=[
                {"name": "深度学习项目", "description": "图像识别研究"}
            ]
        )
        
        # Test similarity matching
        similar_cases = matcher.find_similar_cases(user_background, top_n=5)
        logger.info(f"Found {len(similar_cases)} similar cases")
        
        if similar_cases:
            logger.info(f"Top case similarity score: {similar_cases[0]['similarity_score']:.3f}")
            return True
        else:
            logger.warning("No similar cases found")
            return False
            
    except Exception as e:
        logger.error(f"Similarity matcher test failed: {str(e)}")
        return False

def test_gemini_service():
    """Test Gemini service functionality"""
    logger.info("Testing Gemini service...")
    
    try:
        from services.llm_service import LLMService
        llm_service = LLMService()
        
        # Create test user background
        user_background = UserBackground(
            undergraduate_university="北京邮电大学",
            undergraduate_major="计算机科学与技术",
            gpa=3.5,
            gpa_scale="4.0",
            graduation_year=2024,
            target_countries=["美国"],
            target_majors=["计算机科学"],
            target_degree_type="Master"
        )
        
        # Test competitiveness analysis
        logger.info("Testing competitiveness analysis...")
        competitiveness = llm_service.analyze_competitiveness(user_background)
        
        if competitiveness:
            logger.info("Competitiveness analysis successful")
            logger.info(f"Summary: {competitiveness.summary[:100]}...")
            return True
        else:
            logger.warning("Competitiveness analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"Gemini service test failed: {str(e)}")
        return False

def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        from models.database import get_target_db
        from models.schemas import ProcessedCase
        
        db = next(get_target_db())
        case_count = db.query(ProcessedCase).count()
        db.close()
        
        logger.info(f"Database connection successful. Found {case_count} processed cases")
        return case_count > 0
        
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting backend functionality tests...")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Similarity Matcher", test_similarity_matcher),
        ("Gemini Service", test_gemini_service),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {str(e)}")
            results[test_name] = False
    
    # Print summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"\nOverall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)