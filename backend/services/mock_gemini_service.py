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
        """模拟选校建议 - 扩大推荐范围和丰富项目多样性"""
        try:
            target_countries = user_background.target_countries
            target_majors = user_background.target_majors
            user_gpa = user_background.gpa
            user_university = user_background.undergraduate_university
            
            # 根据目标国家和专业生成更多推荐
            reach_schools = []
            target_schools = []
            safety_schools = []
            
            if "美国" in target_countries:
                if "计算机科学" in target_majors or "数据科学" in target_majors or "人工智能" in target_majors:
                    # 冲刺档次 - 更多顶尖项目
                    reach_schools.extend([
                        SchoolRecommendation(
                            university="斯坦福大学",
                            program="MS in Computer Science",
                            reason=f"基于您{user_gpa} GPA和{user_university}的背景，该顶尖CS项目值得冲刺，相似案例显示有录取可能"
                        ),
                        SchoolRecommendation(
                            university="麻省理工学院",
                            program="MEng in Computer Science",
                            reason=f"您的{user_university}背景在MIT有良好声誉，GPA {user_gpa}达到申请门槛"
                        ),
                        SchoolRecommendation(
                            university="加州大学伯克利分校",
                            program="MS in Computer Science",
                            reason=f"公立名校CS项目，您的学术背景符合其录取偏好"
                        ),
                        SchoolRecommendation(
                            university="卡内基梅隆大学",
                            program="MS in Machine Learning",
                            reason=f"ML专业全美顶尖，您的背景在相似案例中有成功先例"
                        ),
                        SchoolRecommendation(
                            university="华盛顿大学",
                            program="MS in Computer Science & Engineering",
                            reason=f"CS排名前十，对{user_university}学生友好，值得冲刺"
                        )
                    ])
                    
                    # 匹配档次 - 更多合适项目
                    target_schools.extend([
                        SchoolRecommendation(
                            university="卡内基梅隆大学",
                            program="MS in Information Systems",
                            reason=f"CMU的IS项目录取相对CS更友好，您的背景匹配度高"
                        ),
                        SchoolRecommendation(
                            university="南加州大学",
                            program="MS in Computer Science",
                            reason=f"私立名校，对国际学生友好，您的GPA {user_gpa}符合录取标准"
                        ),
                        SchoolRecommendation(
                            university="纽约大学",
                            program="MS in Computer Science",
                            reason=f"地理位置优越，就业机会多，与您的背景匹配"
                        ),
                        SchoolRecommendation(
                            university="加州大学圣地亚哥分校",
                            program="MS in Computer Science",
                            reason=f"公立名校，CS实力强劲，录取相对友好"
                        ),
                        SchoolRecommendation(
                            university="德州大学奥斯汀分校",
                            program="MS in Computer Science",
                            reason=f"CS排名前十五，对{user_university}背景学生录取友好"
                        ),
                        SchoolRecommendation(
                            university="伊利诺伊大学香槟分校",
                            program="MS in Computer Science",
                            reason=f"公立CS强校，相似背景案例录取率较高"
                        )
                    ])
                    
                    # 保底档次 - 更多稳妥选择
                    safety_schools.extend([
                        SchoolRecommendation(
                            university="东北大学",
                            program="MS in Computer Science",
                            reason=f"录取相对友好，Co-op项目有利就业，适合保底"
                        ),
                        SchoolRecommendation(
                            university="波士顿大学",
                            program="MS in Computer Science",
                            reason=f"私立名校，地理位置佳，您的背景录取概率高"
                        ),
                        SchoolRecommendation(
                            university="加州大学欧文分校",
                            program="MS in Computer Science",
                            reason=f"加州公立名校，CS项目质量高，录取相对稳妥"
                        ),
                        SchoolRecommendation(
                            university="罗格斯大学",
                            program="MS in Computer Science",
                            reason=f"公立研究型大学，CS项目实力不错，录取友好"
                        ),
                        SchoolRecommendation(
                            university="亚利桑那州立大学",
                            program="MS in Computer Science",
                            reason=f"CS项目排名上升，对国际学生友好，可作保底"
                        )
                    ])
            
            if "英国" in target_countries:
                # 英国项目推荐
                reach_schools.extend([
                    SchoolRecommendation(
                        university="剑桥大学",
                        program="MPhil in Advanced Computer Science",
                        reason=f"世界顶尖大学，您的{user_university}背景有竞争力"
                    ),
                    SchoolRecommendation(
                        university="牛津大学",
                        program="MSc in Computer Science",
                        reason=f"顶尖名校，您的学术背景符合申请要求"
                    )
                ])
                
                target_schools.extend([
                    SchoolRecommendation(
                        university="帝国理工学院",
                        program="MSc Computing",
                        reason=f"理工科强校，与您的背景高度匹配"
                    ),
                    SchoolRecommendation(
                        university="伦敦大学学院",
                        program="MSc Computer Science",
                        reason=f"G5名校，CS项目质量高，录取相对友好"
                    ),
                    SchoolRecommendation(
                        university="爱丁堡大学",
                        program="MSc Computer Science",
                        reason=f"苏格兰名校，CS排名英国前五，适合您的背景"
                    )
                ])
                
                safety_schools.extend([
                    SchoolRecommendation(
                        university="曼彻斯特大学",
                        program="MSc Computer Science",
                        reason=f"综合实力强，录取相对稳妥，就业前景好"
                    ),
                    SchoolRecommendation(
                        university="布里斯托大学",
                        program="MSc Computer Science",
                        reason=f"英国名校，CS项目质量高，录取友好"
                    )
                ])
            
            # 如果目标包含其他国家，也添加相应推荐
            if "加拿大" in target_countries:
                target_schools.extend([
                    SchoolRecommendation(
                        university="多伦多大学",
                        program="MSc in Computer Science",
                        reason=f"加拿大顶尖大学，CS实力强劲，适合您的背景"
                    ),
                    SchoolRecommendation(
                        university="滑铁卢大学",
                        program="MMath in Computer Science",
                        reason=f"CS和Co-op项目闻名，就业前景优秀"
                    )
                ])
            
            case_insights = f"根据与您背景相似的{len(similar_cases)}个成功案例分析，来自{user_university}、GPA {user_gpa}的学生主要被录取到英美地区的知名院校。这些案例显示，您的背景在申请{', '.join(target_majors)}相关项目时具有竞争优势。建议您在保持学术成绩的同时，重点提升标准化考试成绩和实践经历，同时可以考虑申请多个相关项目以增加录取机会。"
            
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
            
            # 模拟语言考试类型和主要经历
            language_test_type = case_data.get('language_test_type', 'TOEFL')
            if not language_test_type:
                language_test_type = 'TOEFL' if case_data.get('language_total_score', 0) > 100 else 'IELTS'
            
            key_experiences = case_data.get('experience_text', '')
            if not key_experiences:
                key_experiences = "参与机器学习项目研究，在知名互联网公司实习，发表学术论文"
            
            return CaseAnalysis(
                case_id=case_data.get('id', 0),
                admitted_university=case_data.get('admitted_university', ''),
                admitted_program=case_data.get('admitted_program', ''),
                gpa=str(case_data.get('gpa_4_scale', 0)),
                language_score=str(case_data.get('language_total_score', 0)),
                language_test_type=language_test_type,
                key_experiences=key_experiences,
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