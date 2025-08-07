#!/usr/bin/env python3
"""
测试API连接和数据库状态
"""

import requests
import json
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from config.settings import settings

def test_gemini_api():
    """测试Gemini API连接"""
    print("🔍 测试Gemini API连接...")
    
    try:
        # 检查API密钥
        api_key = settings.GEMINI_API_KEY or "AIzaSyCoFTfqOUr9K8Lg4v-mSR_Ou63YqQyv-r0"
        if not api_key:
            print("❌ 未设置GEMINI_API_KEY")
            return False
        
        print(f"✅ API密钥已设置: {api_key[:10]}...")
        
        # 测试API调用
        test_data = {
            "undergraduate_university": "清华大学",
            "undergraduate_major": "计算机科学与技术",
            "gpa": 3.8,
            "gpa_scale": "4.0",
            "graduation_year": 2024,
            "target_countries": ["美国"],
            "target_majors": ["计算机科学"],
            "target_degree_type": "Master"
        }
        
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Gemini API调用成功")
            print(f"   竞争力分析: {len(data.get('competitiveness', {}).get('strengths', ''))} 字符")
            print(f"   选校建议: {len(data.get('school_recommendations', {}).get('reach', []))} 个冲刺院校")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    try:
        from models.database import get_target_db
        
        db = next(get_target_db())
        
        # 测试查询
        from models.schemas import ProcessedCase
        cases = db.query(ProcessedCase).limit(5).all()
        
        print(f"✅ 数据库连接成功，找到 {len(cases)} 个案例")
        
        if cases:
            print("   示例案例:")
            for i, case in enumerate(cases[:3]):
                print(f"   {i+1}. {case.admitted_university} - {case.admitted_program}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_backend_services():
    """测试后端服务状态"""
    print("🔍 测试后端服务状态...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端服务正常")
            print(f"   数据库状态: {data.get('database', 'unknown')}")
            print(f"   Gemini API状态: {data.get('gemini_api', 'unknown')}")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API和数据库连接测试")
    print("=" * 50)
    
    tests = [
        ("后端服务状态", test_backend_services),
        ("数据库连接", test_database_connection),
        ("Gemini API连接", test_gemini_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
        print()
    
    # 总结
    print("=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有服务正常！系统可以使用真实数据和大模型")
        return True
    else:
        print("⚠️  部分服务异常，系统将使用模拟数据")
        return False

if __name__ == "__main__":
    main() 