#!/usr/bin/env python3
"""
测试前后端连接
"""
import requests
import json

def test_all_endpoints():
    """测试所有API端点"""
    base_url = "http://localhost:8000"
    
    print("=== 测试API端点连接 ===")
    
    # 1. 测试根端点
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ 根端点: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 根端点失败: {e}")
    
    # 2. 测试院校端点
    try:
        response = requests.get(f"{base_url}/api/universities")
        data = response.json()
        print(f"✅ 院校端点: {response.status_code} - 返回{len(data['universities'])}所院校")
    except Exception as e:
        print(f"❌ 院校端点失败: {e}")
    
    # 3. 测试专业端点
    try:
        response = requests.get(f"{base_url}/api/majors")
        data = response.json()
        print(f"✅ 专业端点: {response.status_code} - 返回{len(data['majors'])}个专业")
    except Exception as e:
        print(f"❌ 专业端点失败: {e}")
    
    # 4. 测试分析端点
    try:
        test_data = {
            "undergraduate_university": "北京大学",
            "undergraduate_major": "计算机科学",
            "gpa": "3.5",
            "target_countries": ["加拿大"],
            "target_majors": ["计算机科学"]
        }
        
        response = requests.post(
            f"{base_url}/api/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分析端点: {response.status_code} - 返回完整分析报告")
            print(f"   相似案例数量: {len(data.get('similar_cases', []))}")
            print(f"   推荐建议数量: {len(data.get('recommendations', []))}")
            
            # 验证雅思成绩修复
            for i, case in enumerate(data.get('similar_cases', [])):
                if case.get('language_test_type') == 'IELTS':
                    print(f"   案例{i+1}: IELTS {case.get('language_score')} (前端将显示为 {case.get('language_score')/10:.1f})")
                else:
                    print(f"   案例{i+1}: {case.get('language_test_type')} {case.get('language_score')}")
        else:
            print(f"❌ 分析端点失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 分析端点失败: {e}")
    
    print("\n=== CORS测试 ===")
    # 5. 测试CORS
    try:
        response = requests.options(f"{base_url}/api/analyze")
        print(f"✅ CORS预检: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', '未设置')}")
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")

if __name__ == "__main__":
    test_all_endpoints()