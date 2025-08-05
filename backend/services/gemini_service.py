import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Any
from config.settings import settings
from models.schemas import UserBackground, CompetitivenessAnalysis, SchoolRecommendations, CaseAnalysis, BackgroundImprovement

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
    
    def _call_gemini_api(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Gemini API with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Gemini API call attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All Gemini API attempts failed: {str(e)}")
                    return None
        return None
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """Extract JSON from Gemini response"""
        if not response_text:
            return None
        
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON found, try to parse the entire response
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            return None
    
    def analyze_competitiveness(self, user_background: UserBackground) -> Optional[CompetitivenessAnalysis]:
        """Analyze user's competitiveness using Gemini API"""
        
        # Prepare user data for the prompt
        user_data = {
            "gpa": user_background.gpa,
            "gpa_scale": user_background.gpa_scale,
            "university": user_background.undergraduate_university,
            "major": user_background.undergraduate_major,
            "graduation_year": user_background.graduation_year,
            "language_test": user_background.language_test_type,
            "language_score": user_background.language_total_score,
            "gre_score": user_background.gre_total,
            "gmat_score": user_background.gmat_total,
            "target_countries": user_background.target_countries,
            "target_majors": user_background.target_majors,
            "target_degree": user_background.target_degree_type,
            "research_experiences": user_background.research_experiences,
            "internship_experiences": user_background.internship_experiences,
            "other_experiences": user_background.other_experiences
        }
        
        prompt = f"""你是一位顶级的留学申请策略规划专家。你的任务是根据用户提供的背景资料，给出一个客观、精炼的综合竞争力评估，并明确指出其核心优势和主要短板。

请为以下申请者进行竞争力评估。他/她计划申请{user_background.target_majors}专业的{user_background.target_degree_type}学位，目标国家/地区：{', '.join(user_background.target_countries)}。

用户资料：
```json
{json.dumps(user_data, ensure_ascii=False, indent=2)}
```

请输出JSON格式：
{{
  "strengths": "[核心优势分析，具体分析用户在学术背景、实践经历、语言能力等方面的突出表现]",
  "weaknesses": "[主要短板分析，客观指出用户需要改进的方面，如GPA偏低、缺乏相关实习经历等]",
  "summary": "[一段总结性文字，综合评价用户的整体竞争力水平，并给出申请成功概率的大致判断]"
}}"""

        response_text = self._call_gemini_api(prompt)
        if not response_text:
            return None
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            return None
        
        try:
            return CompetitivenessAnalysis(
                strengths=result_json.get("strengths", ""),
                weaknesses=result_json.get("weaknesses", ""),
                summary=result_json.get("summary", "")
            )
        except Exception as e:
            logger.error(f"Error creating CompetitivenessAnalysis: {str(e)}")
            return None
    
    def generate_school_recommendations(self, user_background: UserBackground, 
                                      similar_cases: List[Dict]) -> Optional[SchoolRecommendations]:
        """Generate school recommendations using Gemini API"""
        
        # Prepare similar cases data
        cases_data = []
        for case in similar_cases[:10]:  # Use top 10 most similar cases
            case_info = case.get('case_data', {})
            cases_data.append({
                "admitted_university": case_info.get('admitted_university', ''),
                "admitted_program": case_info.get('admitted_program', ''),
                "gpa_4_scale": case_info.get('gpa_4_scale', 0),
                "undergraduate_university": case_info.get('undergraduate_university', ''),
                "undergraduate_university_tier": case_info.get('undergraduate_university_tier', ''),
                "language_score": case_info.get('language_total_score', 0),
                "similarity_score": case.get('similarity_score', 0)
            })
        
        user_data = {
            "gpa": user_background.gpa,
            "gpa_scale": user_background.gpa_scale,
            "university": user_background.undergraduate_university,
            "major": user_background.undergraduate_major,
            "target_countries": user_background.target_countries,
            "target_majors": user_background.target_majors,
            "target_degree": user_background.target_degree_type,
            "language_test": user_background.language_test_type,
            "language_score": user_background.language_total_score,
            "gre_score": user_background.gre_total
        }
        
        prompt = f"""你是一位熟悉全球名校招生偏好的AI选校助手。基于用户背景和一系列相似背景的成功案例，为用户生成一个包含'冲刺(Reach)', '匹配(Target)', '保底(Safety)'三个档次的选校列表。每个推荐的院校项目，都必须附上针对该用户的、高度个性化的推荐理由。最后，总结这些案例的规律，给出一个'案例透视'。

用户资料：
```json
{json.dumps(user_data, ensure_ascii=False, indent=2)}
```

相似成功案例参考：
```json
{json.dumps(cases_data, ensure_ascii=False, indent=2)}
```

请输出JSON格式：
{{
  "reach": [
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}},
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}}
  ],
  "target": [
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}},
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}}
  ],
  "safety": [
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}},
    {{"university": "院校名", "program": "项目名", "reason": "推荐理由..."}}
  ],
  "case_insights": "与你背景相似的同学主要录取到了...这些案例显示..."
}}"""

        response_text = self._call_gemini_api(prompt)
        if not response_text:
            return None
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            return None
        
        try:
            return SchoolRecommendations(
                reach=result_json.get("reach", []),
                target=result_json.get("target", []),
                safety=result_json.get("safety", []),
                case_insights=result_json.get("case_insights", "")
            )
        except Exception as e:
            logger.error(f"Error creating SchoolRecommendations: {str(e)}")
            return None
    
    def analyze_single_case(self, user_background: UserBackground, 
                           case_data: Dict) -> Optional[CaseAnalysis]:
        """Analyze a single similar case using Gemini API"""
        
        user_data = {
            "gpa": user_background.gpa,
            "gpa_scale": user_background.gpa_scale,
            "university": user_background.undergraduate_university,
            "major": user_background.undergraduate_major,
            "language_test": user_background.language_test_type,
            "language_score": user_background.language_total_score,
            "gre_score": user_background.gre_total,
            "research_experiences": user_background.research_experiences,
            "internship_experiences": user_background.internship_experiences
        }
        
        case_info = {
            "admitted_university": case_data.get('admitted_university', ''),
            "admitted_program": case_data.get('admitted_program', ''),
            "gpa_4_scale": case_data.get('gpa_4_scale', 0),
            "undergraduate_university": case_data.get('undergraduate_university', ''),
            "undergraduate_major": case_data.get('undergraduate_major', ''),
            "language_score": case_data.get('language_total_score', 0),
            "language_test_type": case_data.get('language_test_type', ''),
            "experience_text": case_data.get('experience_text', ''),
            "background_summary": case_data.get('background_summary', '')
        }
        
        prompt = f"""你是一位数据分析师，擅长对比申请者背景。请详细对比用户与以下成功案例的异同点，并深入分析该案例成功的关键因素，为用户提供可借鉴的经验。

用户资料：
```json
{json.dumps(user_data, ensure_ascii=False, indent=2)}
```

成功案例：
```json
{json.dumps(case_info, ensure_ascii=False, indent=2)}
```

请输出JSON格式：
{{
  "comparison": {{
    "gpa": "用户GPA为X，案例为Y，[分析]",
    "university": "用户本科为X，案例为Y，[分析]",
    "experience": "双方在科研/实习上的异同点是...[分析]"
  }},
  "success_factors": "该案例成功的关键在于...",
  "takeaways": "用户可以从中学习到..."
}}"""

        response_text = self._call_gemini_api(prompt)
        if not response_text:
            return None
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            return None
        
        try:
            comparison_data = result_json.get("comparison", {})
            return CaseAnalysis(
                case_id=case_data.get('id', 0),
                admitted_university=case_data.get('admitted_university', ''),
                admitted_program=case_data.get('admitted_program', ''),
                gpa=str(case_data.get('gpa_4_scale', 0)),
                language_score=str(case_data.get('language_total_score', 0)),
                undergraduate_info=f"{case_data.get('undergraduate_university', '')} {case_data.get('undergraduate_major', '')}",
                comparison={
                    "gpa": comparison_data.get("gpa", ""),
                    "university": comparison_data.get("university", ""),
                    "experience": comparison_data.get("experience", "")
                },
                success_factors=result_json.get("success_factors", ""),
                takeaways=result_json.get("takeaways", "")
            )
        except Exception as e:
            logger.error(f"Error creating CaseAnalysis: {str(e)}")
            return None
    
    def generate_background_improvement(self, user_background: UserBackground, 
                                      weaknesses: str) -> Optional[BackgroundImprovement]:
        """Generate background improvement suggestions using Gemini API"""
        
        user_data = {
            "gpa": user_background.gpa,
            "gpa_scale": user_background.gpa_scale,
            "university": user_background.undergraduate_university,
            "major": user_background.undergraduate_major,
            "target_countries": user_background.target_countries,
            "target_majors": user_background.target_majors,
            "target_degree": user_background.target_degree_type,
            "current_experiences": {
                "research": user_background.research_experiences,
                "internship": user_background.internship_experiences,
                "other": user_background.other_experiences
            }
        }
        
        prompt = f"""你是一位经验丰富的留学申请导师。基于用户的完整背景和目标，请为其量身定制一套在未来6-12个月内具体、可行的背景提升行动计划。

用户资料：
```json
{json.dumps(user_data, ensure_ascii=False, indent=2)}
```

已识别的短板：
{weaknesses}

目标专业：{', '.join(user_background.target_majors)}

请输出JSON格式：
{{
  "action_plan": [
    {{"timeframe": "未来1-3个月", "action": "建议1...", "goal": "目标1..."}},
    {{"timeframe": "未来4-6个月", "action": "建议2...", "goal": "目标2..."}},
    {{"timeframe": "未来7-12个月", "action": "建议3...", "goal": "目标3..."}}
  ],
  "strategy_summary": "总体申请策略建议..."
}}"""

        response_text = self._call_gemini_api(prompt)
        if not response_text:
            return None
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            return None
        
        try:
            return BackgroundImprovement(
                action_plan=result_json.get("action_plan", []),
                strategy_summary=result_json.get("strategy_summary", "")
            )
        except Exception as e:
            logger.error(f"Error creating BackgroundImprovement: {str(e)}")
            return None