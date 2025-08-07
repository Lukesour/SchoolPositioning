#!/usr/bin/env python3
"""
测试 SiliconFlow 迁移的功能完整性
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

def test_configuration():
    """测试配置加载"""
    logger.info("Testing configuration loading...")
    
    try:
        from config.settings import settings
        
        # 检查 SiliconFlow 配置
        if not settings.SILICONFLOW_API_KEY:
            logger.error("SILICONFLOW_API_KEY is not configured")
            return False
        
        if not settings.SILICONFLOW_MODELS_PIPELINE:
            logger.error("SILICONFLOW_MODELS_PIPELINE is not configured")
            return False
        
        logger.info(f"API Key configured: {settings.SILICONFLOW_API_KEY[:10]}...")
        logger.info(f"Models pipeline: {settings.SILICONFLOW_MODELS_PIPELINE}")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {str(e)}")
        return False

def test_llm_service_initialization():
    """测试 LLM 服务初始化"""
    logger.info("Testing LLM service initialization...")
    
    try:
        from services.llm_service import LLMService
        
        llm_service = LLMService()
        logger.info("LLM service initialized successfully")
        
        # 检查配置
        if not llm_service.api_key:
            logger.error("LLM service API key not configured")
            return False
        
        if not llm_service.models_pipeline:
            logger.error("LLM service models pipeline not configured")
            return False
        
        logger.info(f"Service configured with {len(llm_service.models_pipeline)} models")
        return True
        
    except Exception as e:
        logger.error(f"LLM service initialization failed: {str(e)}")
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    logger.info("Testing backward compatibility...")
    
    try:
        # 测试 GeminiService 别名是否工作
        from services.llm_service import GeminiService
        
        service = GeminiService()
        logger.info("GeminiService alias works correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Backward compatibility test failed: {str(e)}")
        return False

def test_analysis_service_integration():
    """测试分析服务集成"""
    logger.info("Testing analysis service integration...")
    
    try:
        from services.analysis_service import AnalysisService
        
        analysis_service = AnalysisService()
        logger.info("Analysis service initialized successfully")
        
        # 检查 LLM 服务是否正确集成
        if not hasattr(analysis_service, 'llm_service'):
            logger.error("Analysis service does not have llm_service attribute")
            return False
        
        logger.info("Analysis service integration successful")
        return True
        
    except Exception as e:
        logger.error(f"Analysis service integration test failed: {str(e)}")
        return False

def main():
    """运行所有测试"""
    logger.info("Starting SiliconFlow migration tests...")
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("LLM Service Initialization", test_llm_service_initialization),
        ("Backward Compatibility", test_backward_compatibility),
        ("Analysis Service Integration", test_analysis_service_integration),
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
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Migration appears successful.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)