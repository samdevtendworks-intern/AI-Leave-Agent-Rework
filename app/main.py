"""
FastAPI Main Application
RESTful API for the Leave Review Agent
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.models import (
    AnalyzeLeaveInput, AnalyzeLeaveOutput,
    LeaveRequest, HealthCheckResponse
)
from app.leave_service import leave_analysis_service
from app.data_service import data_service
from app.ai_service import ai_service
from app.mock_data import MockDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Leave Review Agent API")
    logger.info(f"Version: {settings.app_version}")
    
    # Check if mock data exists, if not generate it
    if not data_service.is_data_loaded():
        logger.warning("Mock data not found. Generating...")
        generator = MockDataGenerator()
        generator.save_mock_data("data")
        data_service.load_data()
    else:
        stats = data_service.get_statistics()
        logger.info(f"📊 Data loaded: {stats}")
    
    # Check AI service
    if ai_service.is_configured():
        logger.info("🤖 Gemini AI: Configured")
    else:
        logger.warning("⚠️  Gemini AI: Not configured (using fallback)")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Leave Review Agent API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Assisted Leave Review & Recommendation Agent for HRMS",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please check the logs.",
            "type": type(exc).__name__
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and configuration
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        gemini_configured=ai_service.is_configured()
    )


@app.post(
    "/api/v1/analyze-leave",
    response_model=AnalyzeLeaveOutput,
    tags=["Leave Analysis"],
    status_code=status.HTTP_200_OK
)
async def analyze_leave(input_data: AnalyzeLeaveInput):
    """
    Analyze a leave request and provide recommendation
    
    This endpoint performs comprehensive analysis including:
    - Team capacity calculation
    - Behavioral pattern recognition
    - Rule-based decision making
    - AI-powered recommendation generation
    
    Args:
        input_data: Leave request with team context
    
    Returns:
        Complete analysis with recommendation and factors
    
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Received analysis request for employee {input_data.request.emp_id}")
        
        result = await leave_analysis_service.analyze_leave_request(input_data)
        
        logger.info(f"Analysis complete: {result.recommendation.value}")
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post(
    "/api/v1/analyze-leave-simple",
    response_model=AnalyzeLeaveOutput,
    tags=["Leave Analysis"],
    status_code=status.HTTP_200_OK
)
async def analyze_leave_simple(request: LeaveRequest):
    """
    Analyze a leave request with automatic context fetching from mock data
    
    This is a simplified endpoint that automatically fetches team context
    from the mock data based on the department ID.
    
    Args:
        request: Leave request details only
    
    Returns:
        Complete analysis with recommendation
    
    Raises:
        HTTPException: If analysis fails or department not found
    """
    try:
        logger.info(f"Received simple analysis request for {request.emp_id}")
        
        if not data_service.is_data_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Mock data not available. Please use /api/v1/analyze-leave with team_context."
            )
        
        result = await leave_analysis_service.analyze_with_auto_context(request)
        
        logger.info(f"Simple analysis complete: {result.recommendation.value}")
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Simple analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/v1/departments", tags=["Data"])
async def get_departments():
    """
    Get list of all available departments in mock data
    
    Returns:
        List of department IDs with team sizes
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mock data not available"
        )
    
    departments = data_service.get_all_departments()
    
    return {
        "departments": [
            {
                "dept_id": dept_id,
                "team_size": data_service.get_team_size(dept_id)
            }
            for dept_id in departments
        ],
        "total": len(departments)
    }


@app.get("/api/v1/statistics", tags=["Data"])
async def get_statistics():
    """
    Get data statistics
    
    Returns:
        Statistics about loaded data
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mock data not available"
        )
    
    return data_service.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
