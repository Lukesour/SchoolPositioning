from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
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
    analysis_service = AnalysisService()
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
            "database": "configured",
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
        
        # Generate analysis report
        report = analysis_service.generate_analysis_report(user_background)
        
        if not report:
            raise HTTPException(
                status_code=500,
                detail="分析报告生成失败，请稍后重试"
            )
        
        logger.info("Analysis completed successfully")
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
        case_details = analysis_service.get_case_details([case_id])
        
        if not case_details:
            raise HTTPException(
                status_code=404,
                detail="案例未找到"
            )
        
        return case_details[0]
        
    except HTTPException:
        raise
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
        cases_df = analysis_service.similarity_matcher.cases_df
        
        if cases_df is None or cases_df.empty:
            return {
                "total_cases": 0,
                "countries": [],
                "universities": [],
                "majors": []
            }
        
        stats = {
            "total_cases": len(cases_df),
            "countries": cases_df['admitted_country'].value_counts().head(10).to_dict(),
            "universities": cases_df['admitted_university'].value_counts().head(10).to_dict(),
            "majors": cases_df['undergraduate_major_category'].value_counts().to_dict()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
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