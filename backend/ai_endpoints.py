"""
AI Analyzer endpoints: Website analysis with Grock API
"""

from fastapi import APIRouter, HTTPException, Depends, status
import logging
from datetime import datetime
from typing import Optional

from models_saas import AIAnalysisRequest
from auth_endpoints import get_current_user
from database_saas import create_ai_analysis, get_ai_analysis, get_user_ai_analyses

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


# ==================== Grock Mock Service ====================

async def analyze_website(url: str) -> dict:
    """
    Mock website analysis (replace with real Grock API integration).
    
    In production, integrate with Grock API:
    - Send URL to Grock API
    - Get AI-powered analysis: tech stack, SEO, performance, security
    - Extract meta info, emails, social links
    """
    
    # Mock analysis result
    return {
        "tech_stack": ["React", "Next.js", "Tailwind CSS", "Vercel"],
        "meta_description": "API Load Testing & Website Analysis Platform",
        "emails": ["support@example.com", "hello@example.com"],
        "social_links": {
            "twitter": "https://twitter.com/example",
            "linkedin": "https://linkedin.com/company/example",
            "github": "https://github.com/example"
        },
        "grock_summary": "Modern full-stack application built with React and Next.js, hosted on Vercel. "
                        "Strong frontend architecture with responsive design. Appears to be enterprise-grade SaaS.",
        "seo_score": 78,
        "performance_score": 85
    }


# ==================== Endpoints ====================

@router.post("/analyze")
async def analyze_website_endpoint(
    request: AIAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze website using AI (Grock API).
    
    - Detects tech stack
    - Extracts meta information
    - Finds contact emails
    - Identifies social links
    - Generates AI summary
    - Provides SEO & performance scores
    """
    try:
        user_id = str(current_user["_id"])
        
        # Validate URL
        if not request.url.startswith(("http://", "https://")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format"
            )
        
        # Call Grock API (mock)
        analysis_data = await analyze_website(request.url)
        
        # Store analysis
        analysis_doc = {
            "url": request.url,
            "tech_stack": analysis_data["tech_stack"],
            "meta_description": analysis_data["meta_description"],
            "emails": analysis_data["emails"],
            "social_links": analysis_data["social_links"],
            "grock_summary": analysis_data["grock_summary"],
            "seo_score": analysis_data["seo_score"],
            "performance_score": analysis_data["performance_score"],
            "created_at": datetime.utcnow()
        }
        
        analysis_id = await create_ai_analysis(user_id, analysis_doc)
        
        logger.info(f"✓ Analysis created: {analysis_id} | User: {user_id} | URL: {request.url}")
        
        return {
            "id": analysis_id,
            "url": request.url,
            "tech_stack": analysis_data["tech_stack"],
            "meta_description": analysis_data["meta_description"],
            "emails": analysis_data["emails"],
            "social_links": analysis_data["social_links"],
            "grock_summary": analysis_data["grock_summary"],
            "seo_score": analysis_data["seo_score"],
            "performance_score": analysis_data["performance_score"],
            "created_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze website"
        )


@router.get("/analyses")
async def list_analyses(current_user: dict = Depends(get_current_user)):
    """
    Get user's AI analysis history.
    """
    try:
        user_id = str(current_user["_id"])
        analyses = await get_user_ai_analyses(user_id, limit=50)
        
        return {
            "analyses": [
                {
                    "id": str(a["_id"]),
                    "url": a["url"],
                    "tech_stack": a["tech_stack"],
                    "seo_score": a["seo_score"],
                    "performance_score": a["performance_score"],
                    "created_at": a["created_at"]
                }
                for a in analyses
            ]
        }
    
    except Exception as e:
        logger.error(f"✗ List analyses failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list analyses"
        )


@router.get("/analyses/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed analysis.
    """
    try:
        analysis = await get_ai_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # Check ownership
        if analysis["user_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "id": str(analysis["_id"]),
            "url": analysis["url"],
            "tech_stack": analysis["tech_stack"],
            "meta_description": analysis.get("meta_description"),
            "emails": analysis["emails"],
            "social_links": analysis["social_links"],
            "grock_summary": analysis["grock_summary"],
            "seo_score": analysis["seo_score"],
            "performance_score": analysis["performance_score"],
            "created_at": analysis["created_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Get analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analysis"
        )
