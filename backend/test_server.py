#!/usr/bin/env python3
"""
简化的测试服务器，专门测试新的API端点
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from scripts.etl_processor import ETLProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="留学定位与选校规划系统 - 测试版",
    description="测试新的院校和专业API端点",
    version="1.0.0-test"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ETL processor
etl_processor = None

@app.on_event("startup")
async def startup_event():
    global etl_processor
    logger.info("Starting up test server...")
    etl_processor = ETLProcessor()
    logger.info("Test server startup completed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "留学定位与选校规划系统 - 测试API", "status": "running"}

@app.get("/api/universities")
async def get_universities():
    """Get list of all universities"""
    try:
        universities = etl_processor.get_universities_list()
        return {"universities": universities}
        
    except Exception as e:
        logger.error(f"Error getting universities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取院校列表失败: {str(e)}"
        )

@app.get("/api/majors")
async def get_majors():
    """Get list of all majors with categories"""
    try:
        majors = etl_processor.get_majors_list()
        return {"majors": majors}
        
    except Exception as e:
        logger.error(f"Error getting majors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取专业列表失败: {str(e)}"
        )

@app.get("/api/stats")
async def get_basic_stats():
    """Get basic statistics"""
    try:
        universities = etl_processor.get_universities_list()
        majors = etl_processor.get_majors_list()
        
        # Count majors by discipline
        disciplines = {}
        for major in majors:
            discipline = major['discipline']
            disciplines[discipline] = disciplines.get(discipline, 0) + 1
        
        return {
            "total_universities": len(universities),
            "total_majors": len(majors),
            "disciplines": disciplines
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )

@app.post("/api/analyze")
async def analyze_user_background(user_data: dict):
    """Simplified analysis endpoint for testing"""
    try:
        logger.info(f"Received analysis request for user from {user_data.get('undergraduate_university', 'Unknown')}")
        
        # Basic validation
        if not user_data.get('undergraduate_university') or not user_data.get('undergraduate_major'):
            raise HTTPException(
                status_code=400,
                detail="本科院校和专业信息是必填项"
            )
        
        if not user_data.get('target_countries') or not user_data.get('target_majors'):
            raise HTTPException(
                status_code=400,
                detail="目标国家和专业信息是必填项"
            )
        
        # Generate a mock analysis report matching frontend interface
        mock_report = {
            "competitiveness": {
                "strengths": "学术背景良好，本科院校声誉不错，GPA表现优秀，具备一定的竞争优势。",
                "weaknesses": "语言成绩有待提升，实习经验相对较少，建议增加相关领域的实践经历。",
                "summary": "整体竞争力中等偏上，在提升语言成绩和增加实习经验后，申请成功率将显著提高。"
            },
            "school_recommendations": {
                "reach": [
                    {
                        "university": "University of Toronto",
                        "program": "Computer Science Master",
                        "reason": "顶尖院校，专业排名优秀，但竞争激烈，需要优秀的语言成绩和丰富经验"
                    },
                    {
                        "university": "University of British Columbia", 
                        "program": "Data Science Master",
                        "reason": "加拿大顶级院校，数据科学项目知名度高，对学术背景要求较高"
                    }
                ],
                "target": [
                    {
                        "university": "University of Melbourne",
                        "program": "Information Technology Master", 
                        "reason": "澳洲八大名校，IT专业实力强劲，录取要求相对合理"
                    },
                    {
                        "university": "University of Waterloo",
                        "program": "Computer Science Master",
                        "reason": "加拿大计算机专业强校，与您的背景匹配度较高"
                    }
                ],
                "safety": [
                    {
                        "university": "Simon Fraser University",
                        "program": "Computing Science Master",
                        "reason": "加拿大知名院校，计算机专业实力不错，录取相对容易"
                    },
                    {
                        "university": "University of Calgary",
                        "program": "Computer Science Master", 
                        "reason": "加拿大综合性大学，计算机专业发展良好，适合作为保底选择"
                    }
                ],
                "case_insights": "根据相似背景的成功案例分析，建议重点关注加拿大和澳洲的院校，这些地区对中国学生较为友好，且专业实力强劲。"
            },
            "similar_cases": [
                {
                    "gpa": "3.5",
                    "language_score": 70,  # This will be displayed as 7.0 for IELTS
                    "language_test_type": "IELTS",
                    "undergraduate_info": "985院校 计算机科学专业",
                    "admitted_university": "University of Toronto",
                    "admitted_program": "Computer Science Master",
                    "key_experiences": "2段实习经历，1个科研项目"
                },
                {
                    "gpa": "3.7", 
                    "language_score": 65,  # This will be displayed as 6.5 for IELTS
                    "language_test_type": "IELTS",
                    "undergraduate_info": "211院校 软件工程专业",
                    "admitted_university": "University of Melbourne", 
                    "admitted_program": "Information Technology Master",
                    "key_experiences": "3段实习经历，参与开源项目"
                },
                {
                    "gpa": "3.6",
                    "language_score": 105,  # TOEFL score, should remain as 105
                    "language_test_type": "TOEFL",
                    "undergraduate_info": "双一流院校 数据科学专业",
                    "admitted_university": "University of British Columbia",
                    "admitted_program": "Data Science Master", 
                    "key_experiences": "2段实习经历，发表1篇论文"
                }
            ],
            "background_improvement": {
                "priority_actions": [
                    "提升语言成绩至IELTS 7.0+或TOEFL 100+",
                    "增加2-3段相关领域实习经历",
                    "参与1-2个科研项目或开源项目"
                ],
                "timeline_suggestions": "建议在申请前6-12个月开始准备，确保有充足时间提升各项指标",
                "additional_tips": "可以考虑参加一些专业相关的竞赛或获得相关认证，增强申请竞争力"
            }
        }
        
        logger.info("Mock analysis completed successfully")
        return mock_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析服务暂时不可用，请稍后重试: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )