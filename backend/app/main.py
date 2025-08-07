from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import json
from pathlib import Path
from contextlib import asynccontextmanager
from models.schemas import UserBackground, AnalysisReport
from services.analysis_service import AnalysisService
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global analysis service instance
analysis_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global analysis_service
    logger.info("Starting up application...")
    try:
        analysis_service = AnalysisService()
        logger.info("Analysis service initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize analysis service: {e}")
        analysis_service = None
    logger.info("Application startup completed")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title="留学定位与选校规划系统",
    description="基于AI和大数据的个性化留学申请分析平台",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_mock_analysis_report(user_background: UserBackground) -> AnalysisReport:
    """生成模拟分析报告"""
    return AnalysisReport(
        competitiveness={
            "strengths": f"基于您的背景，您在{user_background.undergraduate_major}领域有较强的学术基础。",
            "weaknesses": "建议加强语言能力和科研经历。",
            "summary": "整体竞争力良好，有较大提升空间。"
        },
        school_recommendations={
            "reach": [
                {
                    "university": "Stanford University",
                    "program": "Computer Science",
                    "reason": "顶尖院校，适合优秀学生申请"
                }
            ],
            "target": [
                {
                    "university": "University of California, Berkeley",
                    "program": "Data Science",
                    "reason": "匹配您的背景，录取概率较高"
                }
            ],
            "safety": [
                {
                    "university": "University of Southern California",
                    "program": "Computer Science",
                    "reason": "保底选择，录取概率很高"
                }
            ],
            "case_insights": "基于相似案例分析，建议重点准备语言考试和科研经历。"
        },
        similar_cases=[
            {
                "case_id": 1,
                "admitted_university": "Stanford University",
                "admitted_program": "Computer Science",
                "gpa": "3.8",
                "language_score": "7.5" if user_background.language_test_type == "IELTS" else "100",
                "language_test_type": user_background.language_test_type or "TOEFL",
                "undergraduate_info": f"{user_background.undergraduate_university} - {user_background.undergraduate_major}",
                "comparison": {
                    "gpa": "GPA相似，学术背景匹配",
                    "university": "院校背景相当",
                    "experience": "科研经历需要加强"
                },
                "success_factors": "优秀的GPA和语言成绩是关键",
                "takeaways": "建议参加更多科研项目和实习"
            }
        ],
        background_improvement={
            "action_plan": [
                {
                    "timeframe": "3-6个月",
                    "action": "提高语言成绩",
                    "goal": "达到目标院校要求"
                },
                {
                    "timeframe": "6-12个月",
                    "action": "参与科研项目",
                    "goal": "增强学术背景"
                }
            ],
            "strategy_summary": "系统性的背景提升计划将显著提高申请成功率。"
        }
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "留学定位与选校规划系统 API", "status": "running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Basic health check without loading data
        return {
            "status": "healthy",
            "database": "configured" if analysis_service else "mock_mode",
            "cases_loaded": "lazy_loading",
            "gemini_api": "configured" if settings.GEMINI_API_KEY else "not_configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/api/analyze", response_model=AnalysisReport)
async def analyze_user_background(user_background: UserBackground):
    """
    Analyze user background and generate comprehensive report
    """
    try:
        logger.info(f"Received analysis request for user from {user_background.undergraduate_university}")
        
        # Validate input
        if not user_background.undergraduate_university or not user_background.undergraduate_major:
            raise HTTPException(
                status_code=400,
                detail="本科院校和专业信息是必填项"
            )
        
        if not user_background.target_countries or not user_background.target_majors:
            raise HTTPException(
                status_code=400,
                detail="目标国家和专业信息是必填项"
            )
        
        # Try to use real analysis service, fallback to mock
        if analysis_service:
            try:
                report = analysis_service.generate_analysis_report(user_background)
                if report:
                    logger.info("Analysis completed successfully using real service")
                    return report
            except Exception as e:
                logger.warning(f"Real analysis service failed, using mock: {e}")
        
        # Generate mock analysis report
        logger.info("Using mock analysis service")
        report = generate_mock_analysis_report(user_background)
        
        if not report:
            raise HTTPException(
                status_code=500,
                detail="分析报告生成失败，请稍后重试"
            )
        
        logger.info("Mock analysis completed successfully")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.get("/api/cases/{case_id}")
async def get_case_details(case_id: int):
    """Get detailed information for a specific case"""
    try:
        if analysis_service:
            case_details = analysis_service.get_case_details([case_id])
            if case_details:
                return case_details[0]
        
        # Return mock case details
        return {
            "case_id": case_id,
            "admitted_university": "Stanford University",
            "admitted_program": "Computer Science",
            "gpa": "3.8",
            "language_score": "7.5",
            "language_test_type": "IELTS",
            "undergraduate_info": "清华大学 - 计算机科学与技术"
        }
        
    except Exception as e:
        logger.error(f"Error getting case details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取案例详情失败: {str(e)}"
        )

@app.post("/api/refresh-data")
async def refresh_similarity_data(background_tasks: BackgroundTasks):
    """Refresh similarity matching data"""
    try:
        if analysis_service:
            background_tasks.add_task(analysis_service.refresh_similarity_data)
        return {"message": "数据刷新任务已启动"}
        
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据刷新失败: {str(e)}"
        )

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        if analysis_service and analysis_service.similarity_matcher.cases_df is not None:
            cases_df = analysis_service.similarity_matcher.cases_df
            
            if not cases_df.empty:
                stats = {
                    "total_cases": len(cases_df),
                    "countries": cases_df['admitted_country'].value_counts().head(10).to_dict(),
                    "universities": cases_df['admitted_university'].value_counts().head(10).to_dict(),
                    "majors": cases_df['undergraduate_major_category'].value_counts().to_dict()
                }
                return stats
        
        # Return mock stats
        return {
            "total_cases": 1000,
            "countries": {"美国": 500, "英国": 300, "加拿大": 200},
            "universities": {"Stanford": 50, "MIT": 45, "UC Berkeley": 40},
            "majors": {"CS": 300, "EE": 200, "ME": 150}
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

@app.get("/api/universities")
async def get_universities():
    """Get list of universities"""
    try:
        data_file = Path(__file__).parent.parent.parent / "data" / "frontend_data.json"
        
        if not data_file.exists():
            raise HTTPException(
                status_code=404,
                detail="院校数据文件不存在"
            )
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "universities": data.get("universities", []),
            "count": len(data.get("universities", []))
        }
        
    except Exception as e:
        logger.error(f"Error getting universities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取院校列表失败: {str(e)}"
        )

@app.get("/api/majors")
async def get_majors():
    """Get list of majors"""
    try:
        data_file = Path(__file__).parent.parent.parent / "data" / "frontend_data.json"
        
        if not data_file.exists():
            raise HTTPException(
                status_code=404,
                detail="专业数据文件不存在"
            )
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "majors": data.get("majors", []),
            "majors_by_category": data.get("majors_by_category", {}),
            "count": len(data.get("majors", []))
        }
        
    except Exception as e:
        logger.error(f"Error getting majors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取专业列表失败: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )