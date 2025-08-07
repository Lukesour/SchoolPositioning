import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.schemas import SourceCaseDetail, ProcessedCase, Base
from config.settings import settings
import logging
from typing import Dict, Optional, Tuple, List
import PyPDF2
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLProcessor:
    def __init__(self):
        # Source database connection
        self.source_engine = create_engine(settings.source_database_url)
        self.source_session = sessionmaker(bind=self.source_engine)()
        
        # Target database connection
        self.target_engine = create_engine(settings.target_database_url)
        self.target_session = sessionmaker(bind=self.target_engine)()
        
        # University tier mapping
        self.university_tiers = self._load_university_tiers()
        
        # Major category mapping
        self.major_categories = self._load_major_categories()
        
        # Load expanded data from files
        self.expanded_universities = self._load_universities_from_excel()
        self.expanded_majors = self._load_majors_from_pdf()
    
    def _load_university_tiers(self) -> Dict[str, str]:
        """Load university tier mapping"""
        # This should be expanded with a comprehensive university database
        tiers = {
            # C9 Universities
            "北京大学": "C9", "清华大学": "C9", "复旦大学": "C9", "上海交通大学": "C9",
            "南京大学": "C9", "浙江大学": "C9", "中国科学技术大学": "C9", "哈尔滨工业大学": "C9",
            "西安交通大学": "C9",
            
            # 985 Universities (partial list)
            "中国人民大学": "985", "北京理工大学": "985", "北京航空航天大学": "985",
            "北京师范大学": "985", "中央民族大学": "985", "南开大学": "985", "天津大学": "985",
            "大连理工大学": "985", "东北大学": "985", "吉林大学": "985", "同济大学": "985",
            "华东师范大学": "985", "华东理工大学": "985", "东南大学": "985", "南京理工大学": "985",
            "南京航空航天大学": "985", "山东大学": "985", "中国海洋大学": "985", "武汉大学": "985",
            "华中科技大学": "985", "湖南大学": "985", "中南大学": "985", "中山大学": "985",
            "华南理工大学": "985", "四川大学": "985", "重庆大学": "985", "电子科技大学": "985",
            "西北工业大学": "985", "西北农林科技大学": "985", "兰州大学": "985",
            
            # 211 Universities (partial list)
            "北京邮电大学": "211", "北京科技大学": "211", "北京化工大学": "211", "北京林业大学": "211",
            "中国传媒大学": "211", "中央财经大学": "211", "对外经济贸易大学": "211",
            "华北电力大学": "211", "中国石油大学": "211", "河北工业大学": "211",
            "太原理工大学": "211", "内蒙古大学": "211", "辽宁大学": "211", "大连海事大学": "211",
            "延边大学": "211", "东北师范大学": "211", "东北林业大学": "211", "东北农业大学": "211",
            "华东理工大学": "211", "东华大学": "211", "上海财经大学": "211", "上海大学": "211",
            "苏州大学": "211", "南京师范大学": "211", "中国矿业大学": "211", "河海大学": "211",
            "江南大学": "211", "南京农业大学": "211", "中国药科大学": "211", "南京理工大学": "211",
            "浙江工业大学": "211", "安徽大学": "211", "合肥工业大学": "211", "福州大学": "211",
            "南昌大学": "211", "郑州大学": "211", "华中师范大学": "211", "中南财经政法大学": "211",
            "华中农业大学": "211", "湖南师范大学": "211", "暨南大学": "211", "华南师范大学": "211",
            "广西大学": "211", "海南大学": "211", "西南大学": "211", "西南交通大学": "211",
            "四川农业大学": "211", "贵州大学": "211", "云南大学": "211", "西北大学": "211",
            "西安电子科技大学": "211", "长安大学": "211", "陕西师范大学": "211", "青海大学": "211",
            "宁夏大学": "211", "新疆大学": "211", "石河子大学": "211", "西藏大学": "211",
            
            # Add more universities as needed
            "深圳大学": "普通本科",
        }
        return tiers
    
    def _load_major_categories(self) -> Dict[str, str]:
        """Load major category mapping"""
        categories = {
            # Computer Science & Technology
            "计算机科学与技术": "CS", "软件工程": "CS", "网络工程": "CS", "信息安全": "CS",
            "数据科学与大数据技术": "CS", "人工智能": "CS", "物联网工程": "CS",
            "数字媒体技术": "CS", "智能科学与技术": "CS",
            
            # Electrical Engineering
            "电子信息工程": "EE", "通信工程": "EE", "电气工程及其自动化": "EE",
            "电子科学与技术": "EE", "微电子科学与工程": "EE", "光电信息科学与工程": "EE",
            "信息工程": "EE", "电子信息科学与技术": "EE", "自动化": "EE",
            
            # Mechanical Engineering
            "机械工程": "ME", "机械设计制造及其自动化": "ME", "材料成型及控制工程": "ME",
            "机械电子工程": "ME", "工业设计": "ME", "过程装备与控制工程": "ME",
            
            # Finance & Economics
            "金融学": "Finance", "经济学": "Finance", "国际经济与贸易": "Finance",
            "财政学": "Finance", "金融工程": "Finance", "保险学": "Finance",
            "投资学": "Finance", "经济统计学": "Finance",
            
            # Business & Management
            "工商管理": "Business", "市场营销": "Business", "会计学": "Business",
            "财务管理": "Business", "人力资源管理": "Business", "信息管理与信息系统": "Business",
            "物流管理": "Business", "电子商务": "Business",
            
            # Add more categories as needed
        }
        return categories
    
    def _load_universities_from_excel(self) -> List[Dict[str, str]]:
        """Load universities from Excel file"""
        try:
            # Get the path to the Excel file
            excel_path = os.path.join(os.path.dirname(__file__), '../../data/院校列表.xls')
            
            if not os.path.exists(excel_path):
                logger.warning(f"University Excel file not found at {excel_path}")
                return []
            
            # Read Excel file, skip first 2 rows
            df = pd.read_excel(excel_path, skiprows=2)
            
            # Clean data and filter undergraduate universities
            df_clean = df.dropna(subset=['学校名称', '办学层次'])
            undergraduate_unis = df_clean[df_clean['办学层次'] == '本科']
            
            universities = []
            for _, row in undergraduate_unis.iterrows():
                university = {
                    'name': str(row['学校名称']).strip(),
                    'location': str(row['所在地']).strip() if pd.notna(row['所在地']) else '',
                    'authority': str(row['主管部门']).strip() if pd.notna(row['主管部门']) else '',
                    'code': str(row['学校标识码']).strip() if pd.notna(row['学校标识码']) else ''
                }
                universities.append(university)
            
            logger.info(f"Loaded {len(universities)} undergraduate universities from Excel")
            return universities
            
        except Exception as e:
            logger.error(f"Error loading universities from Excel: {str(e)}")
            return []
    
    def _load_majors_from_pdf(self) -> List[Dict[str, str]]:
        """Load majors from PDF file"""
        try:
            # Get the path to the PDF file
            pdf_path = os.path.join(os.path.dirname(__file__), '../../data/专业列表.pdf')
            
            if not os.path.exists(pdf_path):
                logger.warning(f"Major PDF file not found at {pdf_path}")
                return []
            
            majors = []
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                
                # Extract text from all pages
                for page in reader.pages:
                    text += page.extract_text()
                
                # Parse major information using regex
                # Pattern to match major codes and names like "020101  经济学"
                major_pattern = r'(\d{6}[TK]?)\s+([^\n\r]+?)(?=\s*\(|$|\n|\r)'
                matches = re.findall(major_pattern, text)
                
                # Pattern to match discipline categories like "01  学科门类：哲学"
                category_pattern = r'(\d{2})\s+学科门类：([^\n\r]+)'
                category_matches = re.findall(category_pattern, text)
                
                # Create category mapping
                category_map = {}
                for code, name in category_matches:
                    category_map[code] = name.strip()
                
                for code, name in matches:
                    # Extract discipline category from major code (first 2 digits)
                    discipline_code = code[:2]
                    discipline_name = category_map.get(discipline_code, '其他')
                    
                    major = {
                        'code': code.strip(),
                        'name': name.strip(),
                        'discipline': discipline_name,
                        'is_special': 'T' in code,  # Special major
                        'is_controlled': 'K' in code  # Controlled major
                    }
                    majors.append(major)
                
            logger.info(f"Loaded {len(majors)} majors from PDF")
            return majors
            
        except Exception as e:
            logger.error(f"Error loading majors from PDF: {str(e)}")
            return []
    
    def extract_gpa_info(self, gpa_str: str, background_text: str) -> Tuple[Optional[float], str, str]:
        """Extract and standardize GPA information"""
        if not gpa_str:
            return None, "", ""
        
        gpa_str = str(gpa_str).strip()
        
        # Try to extract GPA and scale
        gpa_patterns = [
            r'(\d+\.?\d*)\s*[/（(]\s*(\d+\.?\d*)\s*[制)）]',  # 3.8/4.0制 or 3.8(4.0制)
            r'(\d+\.?\d*)\s*[/（(]\s*(\d+\.?\d*)\s*[)）]',    # 3.8/4.0 or 3.8(4.0)
            r'GPA\s*[：:]\s*(\d+\.?\d*)',                    # GPA: 3.8
            r'(\d+\.?\d*)',                                  # Just a number
        ]
        
        gpa_value = None
        scale_type = ""
        
        for pattern in gpa_patterns:
            match = re.search(pattern, gpa_str)
            if match:
                if len(match.groups()) == 2:
                    gpa_value = float(match.group(1))
                    scale = float(match.group(2))
                    if scale <= 5:
                        scale_type = f"{scale}"
                    else:
                        scale_type = "100"
                else:
                    gpa_value = float(match.group(1))
                    # Infer scale based on value
                    if gpa_value <= 5:
                        scale_type = "4.0"
                    else:
                        scale_type = "100"
                break
        
        # Convert to 4.0 scale
        gpa_4_scale = None
        if gpa_value is not None:
            if scale_type == "100":
                # Convert 100-point scale to 4.0 scale
                if gpa_value >= 90:
                    gpa_4_scale = 4.0
                elif gpa_value >= 85:
                    gpa_4_scale = 3.7
                elif gpa_value >= 82:
                    gpa_4_scale = 3.3
                elif gpa_value >= 78:
                    gpa_4_scale = 3.0
                elif gpa_value >= 75:
                    gpa_4_scale = 2.7
                elif gpa_value >= 72:
                    gpa_4_scale = 2.3
                elif gpa_value >= 68:
                    gpa_4_scale = 2.0
                elif gpa_value >= 64:
                    gpa_4_scale = 1.7
                elif gpa_value >= 60:
                    gpa_4_scale = 1.0
                else:
                    gpa_4_scale = 0.0
            else:
                gpa_4_scale = min(gpa_value, 4.0)
        
        return gpa_4_scale, gpa_str, scale_type
    
    def extract_language_scores(self, language_str: str, background_text: str) -> Dict[str, Optional[int]]:
        """Extract language test scores"""
        result = {
            "test_type": None,
            "total_score": None,
            "reading": None,
            "listening": None,
            "speaking": None,
            "writing": None
        }
        
        if not language_str:
            return result
        
        text = f"{language_str} {background_text}".lower()
        
        # TOEFL patterns
        toefl_patterns = [
            r'toefl[：:\s]*(\d+)',
            r'托福[：:\s]*(\d+)',
            r'toefl.*?(\d+)',
        ]
        
        # IELTS patterns
        ielts_patterns = [
            r'ielts[：:\s]*(\d+\.?\d*)',
            r'雅思[：:\s]*(\d+\.?\d*)',
            r'ielts.*?(\d+\.?\d*)',
        ]
        
        # Check for TOEFL
        for pattern in toefl_patterns:
            match = re.search(pattern, text)
            if match:
                result["test_type"] = "TOEFL"
                result["total_score"] = int(float(match.group(1)))
                break
        
        # Check for IELTS
        if not result["test_type"]:
            for pattern in ielts_patterns:
                match = re.search(pattern, text)
                if match:
                    result["test_type"] = "IELTS"
                    result["total_score"] = int(float(match.group(1)) * 10)  # Convert to comparable scale
                    break
        
        return result
    
    def extract_gre_gmat_scores(self, background_text: str) -> Dict[str, Optional[int]]:
        """Extract GRE/GMAT scores"""
        result = {
            "gre_total": None,
            "gre_verbal": None,
            "gre_quantitative": None,
            "gre_writing": None,
            "gmat_total": None
        }
        
        if not background_text:
            return result
        
        text = background_text.lower()
        
        # GRE patterns
        gre_pattern = r'gre[：:\s]*(\d+)'
        match = re.search(gre_pattern, text)
        if match:
            result["gre_total"] = int(match.group(1))
        
        # GMAT patterns
        gmat_pattern = r'gmat[：:\s]*(\d+)'
        match = re.search(gmat_pattern, text)
        if match:
            result["gmat_total"] = int(match.group(1))
        
        return result
    
    def get_university_tier(self, university_name: str) -> str:
        """Get university tier"""
        if not university_name:
            return "未知"
        
        # Clean university name
        cleaned_name = university_name.strip()
        
        # Direct lookup in predefined tiers
        if cleaned_name in self.university_tiers:
            return self.university_tiers[cleaned_name]
        
        # Fuzzy matching for partial names in predefined tiers
        for uni_name, tier in self.university_tiers.items():
            if uni_name in cleaned_name or cleaned_name in uni_name:
                return tier
        
        # Check if university exists in expanded university list
        for uni in self.expanded_universities:
            if uni['name'] == cleaned_name or uni['name'] in cleaned_name or cleaned_name in uni['name']:
                # Classify based on authority (主管部门)
                authority = uni.get('authority', '')
                if authority == '教育部':
                    return "211"  # Most education ministry universities are at least 211
                elif authority in ['工业和信息化部', '国防科技工业局']:
                    return "211"
                else:
                    return "普通本科"
        
        # Default classification based on keywords
        if any(keyword in cleaned_name for keyword in ["大学", "学院", "University", "College"]):
            return "普通本科"
        
        return "未知"
    
    def get_major_category(self, major_name: str) -> str:
        """Get major category"""
        if not major_name:
            return "Other"
        
        cleaned_name = major_name.strip()
        
        # First check predefined categories
        if cleaned_name in self.major_categories:
            return self.major_categories[cleaned_name]
        
        # Fuzzy matching in predefined categories
        for major, category in self.major_categories.items():
            if major in cleaned_name or cleaned_name in major:
                return category
        
        # Check in expanded majors list
        for major in self.expanded_majors:
            if major['name'] == cleaned_name or major['name'] in cleaned_name or cleaned_name in major['name']:
                return major['discipline']
        
        return "Other"
    
    def extract_experience_info(self, key_experience: str) -> Tuple[int, int, float, str]:
        """Extract experience information"""
        research_count = 0
        internship_count = 0
        work_years = 0.0
        cleaned_text = ""
        
        if not key_experience:
            return research_count, internship_count, work_years, cleaned_text
        
        text = key_experience.lower()
        cleaned_text = key_experience
        
        # Count research experiences
        research_keywords = ["研究", "项目", "论文", "专利", "科研", "实验"]
        for keyword in research_keywords:
            research_count += len(re.findall(keyword, text))
        
        # Count internship experiences
        internship_keywords = ["实习", "intern", "实践"]
        for keyword in internship_keywords:
            internship_count += len(re.findall(keyword, text))
        
        # Extract work experience years
        work_patterns = [
            r'(\d+)\s*年.*?经验',
            r'(\d+)\s*年.*?工作',
            r'工作.*?(\d+)\s*年',
        ]
        
        for pattern in work_patterns:
            matches = re.findall(pattern, text)
            if matches:
                work_years = max(work_years, float(matches[0]))
        
        return min(research_count, 10), min(internship_count, 10), work_years, cleaned_text
    
    def extract_country_from_university(self, university_name: str) -> str:
        """Extract country from university name"""
        if not university_name:
            return "未知"
        
        # Country mapping based on university names
        country_keywords = {
            "美国": ["美国", "美", "stanford", "mit", "harvard", "berkeley", "carnegie", "columbia", "cornell", "yale", "princeton"],
            "英国": ["英国", "英", "oxford", "cambridge", "imperial", "ucl", "lse", "edinburgh", "manchester", "warwick"],
            "加拿大": ["加拿大", "toronto", "mcgill", "ubc", "waterloo", "alberta"],
            "澳大利亚": ["澳大利亚", "澳洲", "melbourne", "sydney", "anu", "unsw", "monash"],
            "新加坡": ["新加坡", "nus", "ntu", "南洋理工", "新加坡国立"],
            "香港": ["香港", "hku", "hkust", "cuhk", "cityu", "polyu", "香港大学", "香港科技", "香港中文", "香港城市", "香港理工"],
            "德国": ["德国", "慕尼黑", "柏林", "亚琛"],
            "法国": ["法国", "巴黎"],
            "日本": ["日本", "东京", "京都", "大阪"],
            "韩国": ["韩国", "首尔", "延世", "高丽"],
        }
        
        university_lower = university_name.lower()
        
        for country, keywords in country_keywords.items():
            for keyword in keywords:
                if keyword in university_lower:
                    return country
        
        return "其他"
    
    def process_single_case(self, case: SourceCaseDetail) -> Optional[ProcessedCase]:
        """Process a single case"""
        try:
            # Extract GPA information
            gpa_4_scale, gpa_original, gpa_scale_type = self.extract_gpa_info(
                case.gpa, case.student_background or ""
            )
            
            # Extract language scores
            language_info = self.extract_language_scores(
                case.language_score or "", case.student_background or ""
            )
            
            # Extract GRE/GMAT scores
            test_scores = self.extract_gre_gmat_scores(case.student_background or "")
            
            # Get university tier
            university_tier = self.get_university_tier(case.undergraduate_university or "")
            
            # Get major category
            major_category = self.get_major_category(case.undergraduate_major or "")
            
            # Extract experience information
            research_count, internship_count, work_years, experience_text = self.extract_experience_info(
                case.key_experience or ""
            )
            
            # Extract country
            admitted_country = self.extract_country_from_university(case.admitted_university or "")
            
            # Determine degree type
            degree_type = "Master"
            if case.admitted_program and any(keyword in case.admitted_program.lower() 
                                           for keyword in ["phd", "博士", "doctorate"]):
                degree_type = "PhD"
            
            # Create processed case
            processed_case = ProcessedCase(
                original_id=case.id,
                gpa_4_scale=gpa_4_scale,
                gpa_original=gpa_original,
                gpa_scale_type=gpa_scale_type,
                undergraduate_university=case.undergraduate_university,
                undergraduate_university_tier=university_tier,
                undergraduate_major=case.undergraduate_major,
                undergraduate_major_category=major_category,
                language_test_type=language_info["test_type"],
                language_total_score=language_info["total_score"],
                language_reading=language_info["reading"],
                language_listening=language_info["listening"],
                language_speaking=language_info["speaking"],
                language_writing=language_info["writing"],
                gre_total=test_scores["gre_total"],
                gre_verbal=test_scores["gre_verbal"],
                gre_quantitative=test_scores["gre_quantitative"],
                gre_writing=test_scores["gre_writing"],
                gmat_total=test_scores["gmat_total"],
                admitted_university=case.admitted_university,
                admitted_program=case.admitted_program,
                admitted_country=admitted_country,
                admitted_degree_type=degree_type,
                research_experience_count=research_count,
                internship_experience_count=internship_count,
                work_experience_years=work_years,
                experience_text=experience_text,
                background_summary=case.basic_background or ""
            )
            
            return processed_case
            
        except Exception as e:
            logger.error(f"Error processing case {case.id}: {str(e)}")
            return None
    
    def create_target_database(self):
        """Create target database and tables"""
        try:
            # Create database if it doesn't exist
            engine = create_engine(f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres")
            with engine.connect() as conn:
                conn.execute(text("COMMIT"))  # End any existing transaction
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.DB_NAME_TARGET}'"))
                if not result.fetchone():
                    conn.execute(text(f"CREATE DATABASE {settings.DB_NAME_TARGET}"))
                    logger.info(f"Created database: {settings.DB_NAME_TARGET}")
            
            # Create tables
            Base.metadata.create_all(bind=self.target_engine)
            logger.info("Created tables in target database")
            
        except Exception as e:
            logger.error(f"Error creating target database: {str(e)}")
            raise
    
    def run_etl(self):
        """Run the complete ETL process"""
        logger.info("Starting ETL process...")
        
        # Create target database and tables
        self.create_target_database()
        
        # Clear existing processed data
        self.target_session.query(ProcessedCase).delete()
        self.target_session.commit()
        logger.info("Cleared existing processed data")
        
        # Fetch all source cases
        source_cases = self.source_session.query(SourceCaseDetail).all()
        logger.info(f"Found {len(source_cases)} source cases")
        
        # Process cases
        processed_count = 0
        failed_count = 0
        
        for case in source_cases:
            processed_case = self.process_single_case(case)
            if processed_case:
                self.target_session.add(processed_case)
                processed_count += 1
                
                # Commit in batches
                if processed_count % 100 == 0:
                    self.target_session.commit()
                    logger.info(f"Processed {processed_count} cases...")
            else:
                failed_count += 1
        
        # Final commit
        self.target_session.commit()
        
        logger.info(f"ETL process completed. Processed: {processed_count}, Failed: {failed_count}")
        
        # Close sessions
        self.source_session.close()
        self.target_session.close()
    
    def get_universities_list(self) -> List[str]:
        """Get list of university names for frontend"""
        university_names = []
        
        # Add predefined universities
        for uni_name in self.university_tiers.keys():
            university_names.append(uni_name)
        
        # Add universities from Excel file
        for uni in self.expanded_universities:
            if uni['name'] not in university_names:
                university_names.append(uni['name'])
        
        return sorted(university_names)
    
    def get_majors_list(self) -> List[Dict[str, str]]:
        """Get list of majors with categories for frontend"""
        majors_list = []
        
        # Add predefined majors
        for major_name, category in self.major_categories.items():
            majors_list.append({
                'name': major_name,
                'category': category,
                'code': '',
                'discipline': category
            })
        
        # Add majors from PDF file
        for major in self.expanded_majors:
            # Check if major already exists
            existing = any(m['name'] == major['name'] for m in majors_list)
            if not existing:
                majors_list.append({
                    'name': major['name'],
                    'category': major['discipline'],
                    'code': major['code'],
                    'discipline': major['discipline']
                })
        
        # Sort by discipline and then by name
        majors_list.sort(key=lambda x: (x['discipline'], x['name']))
        return majors_list

if __name__ == "__main__":
    processor = ETLProcessor()
    processor.run_etl()