#!/usr/bin/env python3
"""
测试真实的 SiliconFlow API 调用
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_real_api_call():
    """测试真实的 API 调用"""
    logger.info("Testing real SiliconFlow API call...")
    
    try:
        from services.llm_service import LLMService
        from models.schemas import UserBackground
        
        # 创建 LLM 服务
        llm_service = LLMService()
        
        # 创建测试用户背景
        user_background = UserBackground(
            undergraduate_university="北京邮电大学",
            undergraduate_major="计算机科学与技术",
            gpa=3.5,
            gpa_scale="4.0",
            graduation_year=2024,
            language_test_type="TOEFL",
            language_total_score=100,
            gre_total=320,
            gmat_total=None,
            target_countries=["美国"],
            target_majors=["计算机科学"],
            target_degree_type="Master",
            research_experiences=[{"title": "机器学习项目研究", "description": "参与过机器学习项目研究"}],
            internship_experiences=[{"company": "科技公司", "description": "在科技公司实习过"}],
            other_experiences=[{"activity": "编程竞赛", "description": "参加过编程竞赛"}]
        )
        
        logger.info("Testing competitiveness analysis...")
        
        # 测试竞争力分析
        competitiveness = llm_service.analyze_competitiveness(user_background)
        
        if competitiveness:
            logger.info("✅ API call successful!")
            logger.info(f"Strengths: {competitiveness.strengths[:100]}...")
            logger.info(f"Weaknesses: {competitiveness.weaknesses[:100]}...")
            logger.info(f"Summary: {competitiveness.summary[:100]}...")
            return True
        else:
            logger.error("❌ API call returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ API test failed: {str(e)}")
        return False

def test_model_fallback():
    """测试模型回退机制"""
    logger.info("Testing model fallback mechanism...")
    
    try:
        from services.llm_service import LLMService
        from config.settings import settings
        
        # 临时修改模型列表，添加一个不存在的模型来测试回退
        original_models = settings.SILICONFLOW_MODELS_PIPELINE.copy()
        
        # 在列表前面添加一个不存在的模型
        test_models = ["non-existent-model"] + original_models
        
        # 创建一个临时的 LLM 服务实例
        llm_service = LLMService()
        llm_service.models_pipeline = test_models
        
        logger.info(f"Testing with models: {test_models}")
        
        # 测试简单的 API 调用
        response = llm_service._call_siliconflow_api("Hello, this is a test.")
        
        if response:
            logger.info("✅ Model fallback mechanism works!")
            logger.info(f"Response: {response[:100]}...")
            return True
        else:
            logger.error("❌ All models failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Fallback test failed: {str(e)}")
        return False

def main():
    """运行 API 测试"""
    logger.info("Starting real API tests...")
    
    tests = [
        ("Real API Call", test_real_api_call),
        ("Model Fallback", test_model_fallback),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # 总结结果
    logger.info(f"\n{'='*50}")
    logger.info("API TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All API tests passed! SiliconFlow integration is working.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Please check the API configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)