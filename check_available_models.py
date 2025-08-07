#!/usr/bin/env python3
"""
检查Google Generative AI API中可用的模型
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import logging
import google.generativeai as genai
from config.settings import settings

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_available_models():
    """检查可用的模型"""
    logger.info("检查Google Generative AI API中可用的模型...")
    
    # 配置API密钥
    api_key = settings.GEMINI_API_KEY or "AIzaSyCoFTfqOUr9K8Lg4v-mSR_Ou63YqQyv-r0"
    genai.configure(api_key=api_key)
    
    try:
        # 获取可用模型列表
        models = genai.list_models()
        logger.info("可用的模型列表:")
        
        available_models = []
        for model in models:
            model_name = model.name
            if 'generateContent' in model.supported_generation_methods:
                logger.info(f"✅ {model_name} - 支持内容生成")
                available_models.append(model_name)
            else:
                logger.info(f"❌ {model_name} - 不支持内容生成")
        
        return available_models
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return []

def test_specific_models():
    """测试特定的模型"""
    logger.info("测试特定模型...")
    
    # 可能的模型名称
    models_to_test = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'gemma-2b',
        'gemma-7b',
        'gemma-27b',
        'gemma-3b',
        'gemma-9b',
        'gemma-2-27b',
        'gemma-2-9b',
        'gemma-2-2b'
    ]
    
    api_key = settings.GEMINI_API_KEY or "AIzaSyCoFTfqOUr9K8Lg4v-mSR_Ou63YqQyv-r0"
    genai.configure(api_key=api_key)
    
    working_models = []
    
    for model_name in models_to_test:
        logger.info(f"测试模型: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            # 简单测试
            response = model.generate_content("测试")
            if response and response.text:
                logger.info(f"✅ {model_name} 可用!")
                working_models.append(model_name)
            else:
                logger.warning(f"⚠️ {model_name} 响应为空")
        except Exception as e:
            logger.error(f"❌ {model_name} 不可用: {str(e)}")
    
    return working_models

if __name__ == "__main__":
    logger.info("=== 检查可用模型 ===")
    available_models = check_available_models()
    
    logger.info("\n=== 测试特定模型 ===")
    working_models = test_specific_models()
    
    if working_models:
        logger.info(f"\n🎉 找到可用的模型: {working_models}")
        sys.exit(0)
    else:
        logger.error("\n💥 没有找到可用的模型")
        sys.exit(1) 