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
            "database": "configured" if analysis_service else "not_configured",
            "cases_loaded": "lazy_loading",
            "llm_api": "configured" if settings.SILICONFLOW_API_KEY else "not_configured"
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
        
        # Check if analysis service is available
        if not analysis_service:
            logger.error("Analysis service is not available")
            raise HTTPException(
                status_code=503,
                detail="非常抱歉，大模型无法连接，请联系客服"
            )
        
        # Try to use real analysis service
        try:
            report = analysis_service.generate_analysis_report(user_background)
            if report:
                logger.info("Analysis completed successfully using real service")
                return report
            else:
                logger.error("Analysis service returned empty report")
                raise HTTPException(
                    status_code=503,
                    detail="非常抱歉，大模型无法连接，请联系客服"
                )
        except Exception as e:
            logger.error(f"Analysis service failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="非常抱歉，大模型无法连接，请联系客服"
            )
        
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
        if not analysis_service:
            raise HTTPException(
                status_code=503,
                detail="非常抱歉，大模型无法连接，请联系客服"
            )
        
        case_details = analysis_service.get_case_details([case_id])
        if case_details:
            return case_details[0]
        else:
            raise HTTPException(
                status_code=404,
                detail="案例未找到"
            )
        
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
        if not analysis_service:
            raise HTTPException(
                status_code=503,
                detail="非常抱歉，大模型无法连接，请联系客服"
            )
        
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
        if not analysis_service:
            raise HTTPException(
                status_code=503,
                detail="非常抱歉，大模型无法连接，请联系客服"
            )
        
        if analysis_service.similarity_matcher.cases_df is not None:
            cases_df = analysis_service.similarity_matcher.cases_df
            
            if not cases_df.empty:
                stats = {
                    "total_cases": len(cases_df),
                    "countries": cases_df['admitted_country'].value_counts().head(10).to_dict(),
                    "universities": cases_df['admitted_university'].value_counts().head(10).to_dict(),
                    "majors": cases_df['undergraduate_major_category'].value_counts().to_dict()
                }
                return stats
        
        raise HTTPException(
            status_code=503,
            detail="统计数据不可用"
        )
        
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