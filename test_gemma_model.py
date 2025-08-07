#!/usr/bin/env python3
"""
测试gemma-3-27b模型是否可用的脚本
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

def test_gemma_model():
    """测试gemma-3-27b模型是否可用"""
    logger.info("开始测试gemma-3-27b模型...")
    
    # 配置API密钥
    api_key = settings.GEMINI_API_KEY or "AIzaSyCoFTfqOUr9K8Lg4v-mSR_Ou63YqQyv-r0"
    genai.configure(api_key=api_key)
    
    # 测试不同的模型
    models_to_test = [
        'gemma-3-27b-it',
        'gemma-3-12b-it',
        'gemma-3-4b-it',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    for model_name in models_to_test:
        logger.info(f"测试模型: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            # 测试简单调用
            response = model.generate_content("Hello, 测试")
            if response and response.text:
                logger.info(f"✅ {model_name} 模型可用!")
                logger.info(f"响应示例: {response.text[:100]}...")
                return model_name
            else:
                logger.warning(f"⚠️ {model_name} 模型响应为空")
        except Exception as e:
            logger.error(f"❌ {model_name} 模型不可用: {str(e)}")
    
    logger.error("所有模型都不可用")
    return None

if __name__ == "__main__":
    available_model = test_gemma_model()
    if available_model:
        logger.info(f"🎉 找到可用模型: {available_model}")
        sys.exit(0)
    else:
        logger.error("💥 没有找到可用的模型")
        sys.exit(1) 