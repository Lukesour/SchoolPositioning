from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Models
class SourceCaseDetail(Base):
    """Original case details table"""
    __tablename__ = "case_details"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    university = Column(String)
    program = Column(String)
    student_background = Column(Text)
    gpa = Column(String)
    language_score = Column(String)
    graduation_year = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    student_name = Column(String)
    admitted_university = Column(String)
    admitted_program = Column(String)
    undergraduate_university = Column(String)
    undergraduate_major = Column(String)
    basic_background = Column(Text)
    key_experience = Column(Text)
    scraping_status = Column(String)
    scraping_notes = Column(Text)
    process_timestamp = Column(DateTime)

class ProcessedCase(Base):
    """Processed and cleaned case data"""
    __tablename__ = "processed_cases"
    
    id = Column(Integer, primary_key=True)
    original_id = Column(Integer)  # Reference to original case
    
    # Structured academic info
    gpa_4_scale = Column(Float)
    gpa_original = Column(String)
    gpa_scale_type = Column(String)  # "4.0", "100", etc.
    
    # University info
    undergraduate_university = Column(String)
    undergraduate_university_tier = Column(String)  # "985", "211", "双一流", "普通本科", etc.
    undergraduate_major = Column(String)
    undergraduate_major_category = Column(String)  # "CS", "EE", "Finance", etc.
    
    # Language scores
    language_test_type = Column(String)  # "TOEFL", "IELTS"
    language_total_score = Column(Integer)
    language_reading = Column(Integer)
    language_listening = Column(Integer)
    language_speaking = Column(Integer)
    language_writing = Column(Integer)
    
    # Standardized test scores
    gre_total = Column(Integer)
    gre_verbal = Column(Integer)
    gre_quantitative = Column(Integer)
    gre_writing = Column(Float)
    gmat_total = Column(Integer)
    
    # Admission info
    admitted_university = Column(String)
    admitted_program = Column(String)
    admitted_country = Column(String)
    admitted_degree_type = Column(String)  # "Master", "PhD"
    
    # Experience (structured)
    research_experience_count = Column(Integer)
    internship_experience_count = Column(Integer)
    work_experience_years = Column(Float)
    
    # Text fields for similarity matching
    experience_text = Column(Text)  # Cleaned and structured experience text
    background_summary = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models for API
class UserBackground(BaseModel):
    # Academic background
    undergraduate_university: str
    undergraduate_major: str
    gpa: float
    gpa_scale: str  # "4.0" or "100"
    graduation_year: int
    
    # Language scores (optional)
    language_test_type: Optional[str] = None  # "TOEFL" or "IELTS"
    language_total_score: Optional[int] = None
    language_reading: Optional[int] = None
    language_listening: Optional[int] = None
    language_speaking: Optional[int] = None
    language_writing: Optional[int] = None
    
    # Standardized test scores (optional)
    gre_total: Optional[int] = None
    gre_verbal: Optional[int] = None
    gre_quantitative: Optional[int] = None
    gre_writing: Optional[float] = None
    gmat_total: Optional[int] = None
    
    # Application intentions
    target_countries: List[str]
    target_majors: List[str]
    target_degree_type: str  # "Master" or "PhD"
    
    # Experience (optional)
    research_experiences: Optional[List[Dict[str, str]]] = []
    internship_experiences: Optional[List[Dict[str, str]]] = []
    other_experiences: Optional[List[Dict[str, str]]] = []

class CompetitivenessAnalysis(BaseModel):
    strengths: str
    weaknesses: str
    summary: str

class SchoolRecommendation(BaseModel):
    university: str
    program: str
    reason: str

class SchoolRecommendations(BaseModel):
    reach: List[SchoolRecommendation]
    target: List[SchoolRecommendation]
    safety: List[SchoolRecommendation]
    case_insights: str

class CaseComparison(BaseModel):
    gpa: str
    university: str
    experience: str

class CaseAnalysis(BaseModel):
    case_id: int
    admitted_university: str
    admitted_program: str
    gpa: str
    language_score: str
    language_test_type: Optional[str] = None  # "TOEFL" or "IELTS"
    key_experiences: Optional[str] = None  # 主要经历摘要
    undergraduate_info: str
    comparison: CaseComparison
    success_factors: str
    takeaways: str

class ActionPlan(BaseModel):
    timeframe: str
    action: str
    goal: str

class BackgroundImprovement(BaseModel):
    action_plan: List[ActionPlan]
    strategy_summary: str

class AnalysisReport(BaseModel):
    competitiveness: CompetitivenessAnalysis
    school_recommendations: SchoolRecommendations
    similar_cases: List[CaseAnalysis]
    background_improvement: Optional[BackgroundImprovement] = None