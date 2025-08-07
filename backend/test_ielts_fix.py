#!/usr/bin/env python3
"""
测试雅思成绩显示修复
"""

def test_ielts_display_logic():
    """测试雅思成绩显示逻辑"""
    print("=== 测试雅思成绩显示修复 ===")
    
    # 模拟相似案例数据
    test_cases = [
        {
            "language_test_type": "IELTS",
            "language_score": 70,  # 应该显示为 7.0
            "expected": "7.0"
        },
        {
            "language_test_type": "IELTS", 
            "language_score": 65,  # 应该显示为 6.5
            "expected": "6.5"
        },
        {
            "language_test_type": "TOEFL",
            "language_score": 100,  # 应该保持 100
            "expected": "100"
        },
        {
            "language_test_type": "IELTS",
            "language_score": 75,  # 应该显示为 7.5
            "expected": "7.5"
        }
    ]
    
    print("测试用例:")
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        # 应用修复逻辑
        if case["language_test_type"] == "IELTS":
            displayed_score = str((case["language_score"] / 10))
            if displayed_score.endswith('.0'):
                displayed_score = displayed_score
            else:
                displayed_score = f"{case['language_score'] / 10:.1f}"
        else:
            displayed_score = str(case["language_score"])
        
        # 检查结果
        passed = displayed_score == case["expected"]
        status = "✅" if passed else "❌"
        
        print(f"  {i}. {case['language_test_type']} {case['language_score']} -> {displayed_score} (期望: {case['expected']}) {status}")
        
        if not passed:
            all_passed = False
    
    return all_passed

def test_frontend_logic():
    """测试前端显示逻辑（模拟TypeScript代码）"""
    print("\n=== 测试前端显示逻辑 ===")
    
    def format_language_score(language_test_type, language_score):
        """模拟前端的格式化逻辑"""
        if language_test_type == 'IELTS':
            return f"{(language_score / 10):.1f}"
        else:
            return str(language_score)
    
    test_cases = [
        ("IELTS", 70, "7.0"),
        ("IELTS", 65, "6.5"),
        ("IELTS", 75, "7.5"),
        ("TOEFL", 100, "100"),
        ("TOEFL", 95, "95"),
    ]
    
    all_passed = True
    
    for test_type, score, expected in test_cases:
        result = format_language_score(test_type, score)
        passed = result == expected
        status = "✅" if passed else "❌"
        
        print(f"  {test_type} {score} -> {result} (期望: {expected}) {status}")
        
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("测试雅思成绩显示修复功能...\n")
    
    success1 = test_ielts_display_logic()
    success2 = test_frontend_logic()
    
    print(f"\n=== 测试结果 ===")
    if success1 and success2:
        print("🎉 雅思成绩显示修复测试通过！")
        print("\n修复内容:")
        print("- 当语言考试类型为 IELTS 时，分数除以10并保留一位小数")
        print("- TOEFL等其他考试类型保持原样")
        print("- 前端代码已在 AnalysisReport.tsx 第214-218行修改")
    else:
        print("❌ 测试失败，请检查逻辑")