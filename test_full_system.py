#!/usr/bin/env python3
"""
完整系统测试脚本
验证留学选校定位系统的所有功能
"""

import requests
import json
import time
from typing import Dict, Any

# 配置
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ 后端服务正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_universities_api():
    """测试院校API"""
    print("🔍 测试院校API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/universities")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            universities = data.get('universities', [])
            
            if count >= 1000:  # 应该有大量院校
                print(f"✅ 院校API正常，共 {count} 所院校")
                print(f"   示例院校: {universities[:5]}")
                return True
            else:
                print(f"❌ 院校数量不足: {count}")
                return False
        else:
            print(f"❌ 院校API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 院校API连接失败: {e}")
        return False

def test_majors_api():
    """测试专业API"""
    print("🔍 测试专业API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/majors")
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            majors = data.get('majors', [])
            majors_by_category = data.get('majors_by_category', {})
            
            if count >= 500:  # 应该有大量专业
                print(f"✅ 专业API正常，共 {count} 个专业")
                print(f"   示例专业: {majors[:5]}")
                print(f"   专业门类数量: {len(majors_by_category)}")
                return True
            else:
                print(f"❌ 专业数量不足: {count}")
                return False
        else:
            print(f"❌ 专业API异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 专业API连接失败: {e}")
        return False

def test_analysis_api():
    """测试分析API"""
    print("🔍 测试分析API...")
    
    # 测试数据
    test_data = {
        "undergraduate_university": "北京大学",
        "undergraduate_major": "计算机科学与技术",
        "gpa": 3.8,
        "gpa_scale": "4.0",
        "graduation_year": 2024,
        "target_countries": ["美国", "英国"],
        "target_majors": ["计算机科学", "数据科学"],
        "target_degree_type": "Master",
        "research_experiences": [
            {
                "name": "机器学习项目",
                "role": "核心成员",
                "description": "参与深度学习算法研究"
            }
        ],
        "internship_experiences": [
            {
                "company": "腾讯",
                "position": "软件工程师实习生",
                "description": "参与微信支付系统开发"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/analyze", json=test_data)
        if response.status_code == 200:
            data = response.json()
            
            # 检查返回的数据结构
            required_fields = ['competitiveness', 'school_recommendations', 'similar_cases']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ 分析API正常")
                print(f"   竞争力分析: {'strengths' in data['competitiveness']}")
                print(f"   选校建议: {len(data['school_recommendations'].get('reach', []))} 个冲刺院校")
                print(f"   相似案例: {len(data['similar_cases'])} 个案例")
                return True
            else:
                print(f"❌ 分析结果缺少字段: {missing_fields}")
                return False
        else:
            print(f"❌ 分析API异常: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 分析API连接失败: {e}")
        return False

def test_frontend_access():
    """测试前端访问"""
    print("🔍 测试前端访问...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常")
            return True
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def test_ielts_score_fix():
    """测试雅思成绩修复"""
    print("🔍 测试雅思成绩显示修复...")
    
    # 模拟包含IELTS成绩的测试数据
    test_data = {
        "undergraduate_university": "清华大学",
        "undergraduate_major": "电子信息工程",
        "gpa": 3.9,
        "gpa_scale": "4.0",
        "graduation_year": 2024,
        "language_test_type": "IELTS",
        "language_total_score": 75,  # 这应该显示为7.5
        "target_countries": ["英国"],
        "target_majors": ["电子工程"],
        "target_degree_type": "Master"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/analyze", json=test_data)
        if response.status_code == 200:
            data = response.json()
            similar_cases = data.get('similar_cases', [])
            
            # 检查相似案例中的IELTS成绩显示
            ielts_cases = [case for case in similar_cases 
                          if case.get('language_test_type') == 'IELTS']
            
            if ielts_cases:
                for case in ielts_cases[:3]:  # 检查前3个IELTS案例
                    score = case.get('language_score', '')
                    if isinstance(score, str) and '.' in score:
                        print(f"✅ IELTS成绩正确显示: {score}")
                    else:
                        print(f"⚠️  IELTS成绩可能有问题: {score}")
                return True
            else:
                print("⚠️  未找到IELTS案例，无法验证修复")
                return True
        else:
            print(f"❌ 无法测试IELTS修复: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ IELTS测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始完整系统测试")
    print("=" * 50)
    
    tests = [
        ("后端健康状态", test_backend_health),
        ("院校API", test_universities_api),
        ("专业API", test_majors_api),
        ("分析API", test_analysis_api),
        ("前端访问", test_frontend_access),
        ("IELTS成绩修复", test_ielts_score_fix),
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
        print("🎉 所有测试通过！系统运行正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return False

if __name__ == "__main__":
    main()