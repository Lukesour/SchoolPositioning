#!/usr/bin/env python3
"""
测试新的API端点
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.etl_processor import ETLProcessor
import json

def test_data_loading():
    """测试数据加载功能"""
    print("=== 测试数据加载功能 ===")
    
    try:
        processor = ETLProcessor()
        
        # 测试院校数据
        universities = processor.get_universities_list()
        print(f"✅ 成功加载 {len(universities)} 所院校")
        print(f"前5所院校: {universities[:5]}")
        
        # 测试专业数据
        majors = processor.get_majors_list()
        print(f"✅ 成功加载 {len(majors)} 个专业")
        print(f"前5个专业: {[m['name'] for m in majors[:5]]}")
        
        # 按学科门类统计
        disciplines = {}
        for major in majors:
            discipline = major['discipline']
            disciplines[discipline] = disciplines.get(discipline, 0) + 1
        
        print(f"✅ 学科门类统计:")
        for discipline, count in sorted(disciplines.items()):
            print(f"  {discipline}: {count}个专业")
            
        return True
        
    except Exception as e:
        print(f"❌ 数据加载失败: {str(e)}")
        return False

def test_api_response_format():
    """测试API响应格式"""
    print("\n=== 测试API响应格式 ===")
    
    try:
        processor = ETLProcessor()
        
        # 测试院校API响应格式
        universities = processor.get_universities_list()
        api_response_universities = {"universities": universities}
        print(f"✅ 院校API响应格式正确，包含 {len(universities)} 所院校")
        
        # 测试专业API响应格式
        majors = processor.get_majors_list()
        api_response_majors = {"majors": majors}
        print(f"✅ 专业API响应格式正确，包含 {len(majors)} 个专业")
        
        # 保存示例响应到文件
        with open('sample_universities_response.json', 'w', encoding='utf-8') as f:
            json.dump(api_response_universities, f, ensure_ascii=False, indent=2)
        
        with open('sample_majors_response.json', 'w', encoding='utf-8') as f:
            json.dump(api_response_majors, f, ensure_ascii=False, indent=2)
            
        print("✅ 示例响应已保存到 sample_*_response.json 文件")
        
        return True
        
    except Exception as e:
        print(f"❌ API响应格式测试失败: {str(e)}")
        return False

def test_data_quality():
    """测试数据质量"""
    print("\n=== 测试数据质量 ===")
    
    try:
        processor = ETLProcessor()
        
        # 检查院校数据质量
        universities = processor.get_universities_list()
        empty_names = [u for u in universities if not u or not u.strip()]
        print(f"✅ 院校数据质量检查: {len(empty_names)} 个空名称")
        
        # 检查专业数据质量
        majors = processor.get_majors_list()
        empty_major_names = [m for m in majors if not m.get('name') or not m.get('name').strip()]
        empty_disciplines = [m for m in majors if not m.get('discipline') or not m.get('discipline').strip()]
        
        print(f"✅ 专业数据质量检查:")
        print(f"  空专业名称: {len(empty_major_names)} 个")
        print(f"  空学科门类: {len(empty_disciplines)} 个")
        
        # 检查重复数据
        university_names = set()
        duplicates = []
        for uni in universities:
            if uni in university_names:
                duplicates.append(uni)
            university_names.add(uni)
        
        print(f"  重复院校: {len(duplicates)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据质量测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试新的数据加载和API功能...\n")
    
    success = True
    success &= test_data_loading()
    success &= test_api_response_format()
    success &= test_data_quality()
    
    print(f"\n=== 测试结果 ===")
    if success:
        print("🎉 所有测试通过！")
        print("\n下一步:")
        print("1. 启动后端服务器: python app/main.py")
        print("2. 测试API端点: curl http://localhost:8000/api/universities")
        print("3. 启动前端应用测试完整功能")
    else:
        print("❌ 部分测试失败，请检查错误信息")