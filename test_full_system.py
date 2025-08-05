#!/usr/bin/env python3
"""
完整系统测试脚本
"""
import sys
import os
import time
import requests
import json

# 测试数据
test_user_data = {
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

def test_backend_health():
    """测试后端健康检查"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ 后端健康检查通过")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {str(e)}")
        return False

def test_backend_stats():
    """测试后端统计接口"""
    try:
        response = requests.get("http://localhost:8000/api/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端统计接口通过")
            print(f"   总案例数: {data.get('total_cases', 0)}")
            return True
        else:
            print(f"❌ 后端统计接口失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端统计接口连接失败: {str(e)}")
        return False

def test_backend_analysis():
    """测试后端分析接口"""
    try:
        print("🔄 开始测试分析接口（这可能需要几分钟）...")
        response = requests.post(
            "http://localhost:8000/api/analyze",
            json=test_user_data,
            timeout=300  # 5分钟超时
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端分析接口通过")
            print(f"   竞争力评估: {data['competitiveness']['summary'][:100]}...")
            print(f"   推荐学校数量: {len(data['school_recommendations']['reach']) + len(data['school_recommendations']['target']) + len(data['school_recommendations']['safety'])}")
            print(f"   相似案例数量: {len(data['similar_cases'])}")
            return True
        else:
            print(f"❌ 后端分析接口失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 后端分析接口连接失败: {str(e)}")
        return False

def test_frontend():
    """测试前端"""
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ 前端服务正常")
            return True
        else:
            print(f"❌ 前端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {str(e)}")
        return False

def main():
    """运行完整系统测试"""
    print("🚀 开始完整系统测试...")
    print("=" * 50)
    
    tests = [
        ("后端健康检查", test_backend_health),
        ("后端统计接口", test_backend_stats),
        ("前端服务", test_frontend),
        ("后端分析接口", test_backend_analysis),  # 最后测试，因为耗时最长
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试 {test_name} 崩溃: {str(e)}")
            results[test_name] = False
        
        time.sleep(1)  # 短暂延迟
    
    # 打印总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 总体结果: {'🎉 所有测试通过' if all_passed else '⚠️  部分测试失败'}")
    
    if all_passed:
        print("\n🌟 系统已准备就绪！")
        print("   前端地址: http://localhost:3000")
        print("   后端地址: http://localhost:8000")
        print("   API文档: http://localhost:8000/docs")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)