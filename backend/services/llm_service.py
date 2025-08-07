import requests
import json
import logging
from typing import Dict, List, Optional
from config.settings import settings
from models.schemas import UserBackground, CompetitivenessAnalysis, SchoolRecommendations, CaseAnalysis, BackgroundImprovement

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """Initialize LLM Service with SiliconFlow configuration"""
        self.api_key = settings.SILICONFLOW_API_KEY
        self.models_pipeline = settings.SILICONFLOW_MODELS_PIPELINE
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
        if not self.api_key:
            raise Exception("SILICONFLOW_API_KEY is not configured")
        
        if not self.models_pipeline:
            raise Exception("SILICONFLOW_MODELS_PIPELINE is not configured")
        
        logger.info(f"Initialized LLM Service with {len(self.models_pipeline)} models in pipeline")
        logger.info(f"Models pipeline: {', '.join(self.models_pipeline)}")
    
    def _call_siliconflow_api(self, prompt: str) -> Optional[str]:
        """Call SiliconFlow API with sequential model fallback"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for model_name in self.models_pipeline:
            logger.info(f"Attempting to call model: {model_name}...")
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                # Check for successful response
                if response.status_code == 200:
                    result = response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        content = result["choices"][0].get("message", {}).get("content", "")
                        if content:
                            logger.info(f"Successfully received response from model: {model_name}")
                            return content
                        else:
                            logger.warning(f"Model {model_name} returned empty content")
                else:
                    # Handle API errors
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f": {error_detail}"
                    except:
                        error_msg += f": {response.text}"
                    
                    logger.warning(f"Model {model_name} failed. Reason: {error_msg}. Trying next model...")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Model {model_name} failed. Reason: {str(e)}. Trying next model...")
            except Exception as e:
                logger.warning(f"Model {model_name} failed. Reason: {str(e)}. Trying next model...")
        
        # All models failed
        logger.error("All configured LLM models failed. The service is unavailable.")
        return None
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """Extract JSON from LLM response"""
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
            logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            return None
    
    def analyze_competitiveness(self, user_background: UserBackground) -> Optional[CompetitivenessAnalysis]:
        """Analyze user's competitiveness using SiliconFlow API"""
        
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

        response_text = self._call_siliconflow_api(prompt)
        if not response_text:
            # 如果API调用失败，抛出异常以便被上层捕获
            raise Exception("LLM API call failed")
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            raise Exception("Failed to parse JSON response from LLM API")
        
        try:
            return CompetitivenessAnalysis(
                strengths=result_json.get("strengths", ""),
                weaknesses=result_json.get("weaknesses", ""),
                summary=result_json.get("summary", "")
            )
        except Exception as e:
            logger.error(f"Error creating CompetitivenessAnalysis: {str(e)}")
            raise Exception(f"Failed to create CompetitivenessAnalysis: {str(e)}")
    
    def generate_school_recommendations(self, user_background: UserBackground, 
                                      similar_cases: List[Dict]) -> Optional[SchoolRecommendations]:
        """Generate school recommendations using SiliconFlow API"""
        
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
        
        prompt = f"""你是一位熟悉全球名校招生偏好的AI选校助手。基于用户背景和一系列相似背景的成功案例，为用户生成一个包含'冲刺(Reach)', '匹配(Target)', '保底(Safety)'三个档次的选校列表。

核心要求：
1. 尽可能多地返回与用户背景和目标相关的学校与项目，不要局限于少量固定的学校
2. 允许并鼓励为同一个学校推荐多个相关的硕士或博士项目
3. 确保每个推荐理由都是高度个性化的，能紧密结合用户的具体背景（如GPA、院校、经历）和相似案例进行分析
4. 每个档次至少推荐5-8个项目，总数应该在15-25个项目之间

用户资料：
```json
{json.dumps(user_data, ensure_ascii=False, indent=2)}
```

相似成功案例参考：
```json
{json.dumps(cases_data, ensure_ascii=False, indent=2)}
```

请输出JSON格式，每个档次包含更多项目：
{{
  "reach": [
    {{"university": "院校名", "program": "项目名", "reason": "基于用户GPA X.X、来自XX大学XX专业的背景，结合相似案例分析的详细推荐理由..."}},
    // 至少5-8个冲刺项目
  ],
  "target": [
    {{"university": "院校名", "program": "项目名", "reason": "基于用户具体背景和相似案例的详细推荐理由..."}},
    // 至少5-8个匹配项目
  ],
  "safety": [
    {{"university": "院校名", "program": "项目名", "reason": "基于用户具体背景和相似案例的详细推荐理由..."}},
    // 至少5-8个保底项目
  ],
  "case_insights": "与你背景相似的同学主要录取到了...这些案例显示..."
}}"""

        response_text = self._call_siliconflow_api(prompt)
        if not response_text:
            raise Exception("LLM API call failed")
        
        result_json = self._extract_json_from_response(response_text)
        if not result_json:
            raise Exception("Failed to parse JSON response from LLM API")
        
        try:
            return SchoolRecommendations(
                reach=result_json.get("reach", []),
                target=result_json.get("target", []),
                safety=result_json.get("safety", []),
                case_insights=result_json.get("case_insights", "")
            )
        except Exception as e:
            logger.error(f"Error creating SchoolRecommendations: {str(e)}")
            raise Exception(f"Failed to create SchoolRecommendations: {str(e)}")
    
    def analyze_single_case(self, user_background: UserBackground, 
                           case_data: Dict) -> Optional[CaseAnalysis]:
        """Analyze a single similar case using SiliconFlow API"""
        
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

请输出JSON格式，必须包含以下字段：
{{
  "language_test_type": "从案例数据中提取语言考试类型，如TOEFL或IELTS，如果没有则为null",
  "key_experiences": "对案例中的科研、实习等经历进行总结，形成一段摘要文字，例如：xx公司xx岗位实习，参与xx深度学习项目等",
  "comparison": {{
    "gpa": "用户GPA为X，案例为Y，[分析]",
    "university": "用户本科为X，案例为Y，[分析]",
    "experience": "双方在科研/实习上的异同点是...[分析]"
  }},
  "success_factors": "该案例成功的关键在于...",
  "takeaways": "用户可以从中学习到..."
}}"""

        response_text = self._call_siliconflow_api(prompt)
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
                language_test_type=result_json.get("language_test_type"),
                key_experiences=result_json.get("key_experiences"),
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
        """Generate background improvement suggestions using SiliconFlow API"""
        
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

        response_text = self._call_siliconflow_api(prompt)
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

# 为了保持向后兼容性，创建一个别名
GeminiService = LLMService