#!/usr/bin/env python3
"""
Test API endpoints directly without network
"""
import sys
import os
sys.path.append('.')

from fastapi.testclient import TestClient
from app.main import app
from models.schemas import UserBackground
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_health_endpoint():
    """Test health check endpoint"""
    logger.info("Testing health endpoint...")
    
    with TestClient(app) as client:
        response = client.get("/health")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check successful: {data}")
            return True
        else:
            logger.error(f"Health check failed: {response.status_code} - {response.text}")
            return False

def test_analyze_endpoint():
    """Test analyze endpoint"""
    logger.info("Testing analyze endpoint...")
    
    # Create test user data
    user_data = {
        "undergraduate_university": "北京邮电大学",
        "undergraduate_major": "计算机科学与技术",
        "gpa": 3.5,
        "gpa_scale": "4.0",
        "graduation_year": 2024,
        "language_test_type": "TOEFL",
        "language_total_score": 100,
        "target_countries": ["美国", "英国"],
        "target_majors": ["计算机科学"],
        "target_degree_type": "Master",
        "research_experiences": [
            {"name": "深度学习项目", "description": "图像识别研究"}
        ],
        "internship_experiences": [
            {"company": "腾讯", "position": "算法实习生", "description": "推荐系统开发"}
        ],
        "other_experiences": []
    }
    
    with TestClient(app) as client:
        response = client.post("/api/analyze", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Analysis successful!")
            logger.info(f"Competitiveness summary: {data['competitiveness']['summary'][:100]}...")
            logger.info(f"School recommendations - Reach: {len(data['school_recommendations']['reach'])}")
            logger.info(f"Similar cases found: {len(data['similar_cases'])}")
            return True
        else:
            logger.error(f"Analysis failed: {response.status_code} - {response.text}")
            return False

def test_stats_endpoint():
    """Test stats endpoint"""
    logger.info("Testing stats endpoint...")
    
    with TestClient(app) as client:
        response = client.get("/api/stats")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Stats successful: {data['total_cases']} total cases")
            return True
        else:
            logger.error(f"Stats failed: {response.status_code} - {response.text}")
            return False

def main():
    """Run all API tests"""
    logger.info("Starting API endpoint tests...")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Stats", test_stats_endpoint),
        ("Analysis", test_analyze_endpoint),
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
    logger.info("API TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"\nOverall result: {'ALL API TESTS PASSED' if all_passed else 'SOME API TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)