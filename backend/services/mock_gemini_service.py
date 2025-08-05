import logging
from typing import Dict, List, Optional
from models.schemas import UserBackground, CompetitivenessAnalysis, SchoolRecommendations, CaseAnalysis, BackgroundImprovement, ActionPlan, SchoolRecommendation, CaseComparison

logger = logging.getLogger(__name__)

class MockGeminiService:
    """模拟Gemini服务，用于演示和测试"""
    
    def __init__(self):
        logger.info("Using Mock Gemini Service for demonstration")
    
    def analyze_competitiveness(self, user_background: UserBackground) -> Optional[CompetitivenessAnalysis]:
        """模拟竞争力分析"""
        try:
            # 基于用户背景生成模拟分析
            gpa_score = user_background.gpa if user_background.gpa_scale == "4.0" else user_background.gpa / 25
            
            if gpa_score >= 3.7:
                gpa_level = "优秀"
            elif gpa_score >= 3.3:
                gpa_level = "良好"
            elif gpa_score >= 3.0:
                gpa_level = "中等"
            else:
                gpa_level = "偏低"
            
            # 判断院校层级
            university_tier = "211" if "211" in user_background.undergraduate_university else "普通本科"
            if any(uni in user_background.undergraduate_university for uni in ["北京大学", "清华大学", "复旦大学", "上海交通大学"]):
                university_tier = "顶尖985"
            elif "985" in user_background.undergraduate_university or any(uni in user_background.undergraduate_university for uni in ["北京邮电", "华中科技", "中山大学"]):
                university_tier = "985"
            
            strengths = f"您的主要优势包括：1) 来自{university_tier}院校，具有良好的学术背景；2) GPA为{user_background.gpa}({user_background.gpa_scale}制)，属于{gpa_level}水平；3) 目标明确，申请{user_background.target_degree_type}学位的{', '.join(user_background.target_majors)}专业。"
            
            weaknesses = "主要短板包括：1) "
            if not user_background.language_total_score:
                weaknesses += "缺乏语言考试成绩(TOEFL/IELTS)；"
            if not user_background.gre_total and not user_background.gmat_total:
                weaknesses += "缺乏标准化考试成绩(GRE/GMAT)；"
            if not user_background.research_experiences:
                weaknesses += "科研经历相对薄弱；"
            if not user_background.internship_experiences:
                weaknesses += "实习经历不足；"
            
            if weaknesses.endswith("1) "):
                weaknesses = "目前背景较为完整，建议进一步提升软实力背景。"
            
            summary = f"综合来看，您作为{university_tier}院校{user_background.undergraduate_major}专业的学生，具备申请{', '.join(user_background.target_countries)}地区{user_background.target_degree_type}项目的基础条件。建议重点关注语言考试和标准化考试的准备，同时丰富相关实践经历，以提升整体竞争力。"
            
            return CompetitivenessAnalysis(
                strengths=strengths,
                weaknesses=weaknesses,
                summary=summary
            )
        except Exception as e:
            logger.error(f"Error in mock competitiveness analysis: {str(e)}")
            return None
    
    def generate_school_recommendations(self, user_background: UserBackground, similar_cases: List[Dict]) -> Optional[SchoolRecommendations]:
        """模拟选校建议"""
        try:
            target_countries = user_background.target_countries
            target_majors = user_background.target_majors
            
            # 根据目标国家和专业生成推荐
            reach_schools = []
            target_schools = []
            safety_schools = []
            
            if "美国" in target_countries:
                if "计算机科学" in target_majors:
                    reach_schools.append(SchoolRecommendation(
                        university="斯坦福大学",
                        program="MS in Computer Science",
                        reason="顶尖CS项目，适合有强背景的申请者冲刺"
                    ))
                    target_schools.append(SchoolRecommendation(
                        university="卡内基梅隆大学",
                        program="MS in Computer Science",
                        reason="CS专业排名顶尖，与您的背景匹配度较高"
                    ))
                    safety_schools.append(SchoolRecommendation(
                        university="东北大学",
                        program="MS in Computer Science",
                        reason="录取相对友好，可作为保底选择"
                    ))
            
            if "英国" in target_countries:
                reach_schools.append(SchoolRecommendation(
                    university="剑桥大学",
                    program="MPhil in Advanced Computer Science",
                    reason="世界顶尖大学，值得冲刺"
                ))
                target_schools.append(SchoolRecommendation(
                    university="帝国理工学院",
                    program="MSc Computing",
                    reason="理工科强校，与您的背景匹配"
                ))
                safety_schools.append(SchoolRecommendation(
                    university="曼彻斯特大学",
                    program="MSc Computer Science",
                    reason="综合实力强，录取相对稳妥"
                ))
            
            case_insights = f"根据与您背景相似的{len(similar_cases)}个成功案例分析，来自{user_background.undergraduate_university}的学生主要被录取到英美地区的知名院校。建议您在保持学术成绩的同时，重点提升标准化考试成绩和实践经历。"
            
            return SchoolRecommendations(
                reach=reach_schools,
                target=target_schools,
                safety=safety_schools,
                case_insights=case_insights
            )
        except Exception as e:
            logger.error(f"Error in mock school recommendations: {str(e)}")
            return None
    
    def analyze_single_case(self, user_background: UserBackground, case_data: Dict) -> Optional[CaseAnalysis]:
        """模拟单个案例分析"""
        try:
            comparison = CaseComparison(
                gpa=f"您的GPA为{user_background.gpa}，该案例为{case_data.get('gpa_4_scale', 'N/A')}，相近水平有利于参考",
                university=f"您来自{user_background.undergraduate_university}，该案例来自{case_data.get('undergraduate_university', 'N/A')}，院校层级相似",
                experience="双方在实践经历方面都有一定积累，可以相互借鉴经验"
            )
            
            return CaseAnalysis(
                case_id=case_data.get('id', 0),
                admitted_university=case_data.get('admitted_university', ''),
                admitted_program=case_data.get('admitted_program', ''),
                gpa=str(case_data.get('gpa_4_scale', 0)),
                language_score=str(case_data.get('language_total_score', 0)),
                undergraduate_info=f"{case_data.get('undergraduate_university', '')} {case_data.get('undergraduate_major', '')}",
                comparison=comparison,
                success_factors="该案例成功的关键在于扎实的学术基础和丰富的实践经历",
                takeaways="建议您重点关注标准化考试准备和相关实习经历的积累"
            )
        except Exception as e:
            logger.error(f"Error in mock case analysis: {str(e)}")
            return None
    
    def generate_background_improvement(self, user_background: UserBackground, weaknesses: str) -> Optional[BackgroundImprovement]:
        """模拟背景提升建议"""
        try:
            action_plan = []
            
            # 根据短板生成建议
            if "语言考试" in weaknesses:
                action_plan.append(ActionPlan(
                    timeframe="未来1-3个月",
                    action="准备并参加TOEFL/IELTS考试，目标分数TOEFL 100+或IELTS 7.0+",
                    goal="获得符合目标院校要求的语言成绩"
                ))
            
            if "标准化考试" in weaknesses:
                action_plan.append(ActionPlan(
                    timeframe="未来2-4个月",
                    action="准备GRE考试，重点提升数学和写作部分，目标总分320+",
                    goal="获得有竞争力的GRE成绩"
                ))
            
            if "科研经历" in weaknesses:
                action_plan.append(ActionPlan(
                    timeframe="未来3-6个月",
                    action="联系导师参与科研项目，或申请暑期科研实习项目",
                    goal="获得1-2段有意义的科研经历"
                ))
            
            if "实习经历" in weaknesses:
                action_plan.append(ActionPlan(
                    timeframe="未来4-8个月",
                    action="申请相关领域的实习岗位，重点关注知名企业或初创公司",
                    goal="积累实际工作经验，提升实践能力"
                ))
            
            # 如果没有明显短板，给出通用建议
            if not action_plan:
                action_plan.append(ActionPlan(
                    timeframe="未来3-6个月",
                    action="继续保持学术成绩，参与更多项目实践，准备申请材料",
                    goal="全面提升申请竞争力"
                ))
            
            strategy_summary = f"基于您当前的背景和目标，建议采用循序渐进的提升策略。优先解决硬性条件（语言、标准化考试），然后丰富软性背景（科研、实习）。同时，建议您提前了解目标院校的具体要求，制定个性化的申请策略。"
            
            return BackgroundImprovement(
                action_plan=action_plan,
                strategy_summary=strategy_summary
            )
        except Exception as e:
            logger.error(f"Error in mock background improvement: {str(e)}")
            return None