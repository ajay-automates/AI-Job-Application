"""
Jobs API Router
Handles job listing operations
"""
# Define router first to ensure it's always available, even if imports fail
from fastapi import APIRouter
router = APIRouter()

# Now import other dependencies
from typing import List, Optional
from fastapi import Depends, HTTPException, Query, BackgroundTasks
from supabase import Client
from app.database import get_db
from app.services.job_matcher import JobMatcherService


@router.get("/")
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """Get list of jobs with filters"""
    query = db.table("jobs").select("*").eq("is_active", True)
    
    # Apply filters
    if search:
        query = query.or_(f"title.ilike.%{search}%,company.ilike.%{search}%")
    
    if location:
        query = query.ilike("location", f"%{location}%")
    
    if job_type:
        query = query.eq("job_type", job_type)
    
    # Pagination and order
    response = query.order("posted_date", desc=True).range(skip, skip + limit - 1).execute()
    
    return {
        "jobs": response.data,
        "count": len(response.data),
        "skip": skip,
        "limit": limit
    }


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    db: Client = Depends(get_db)
):
    """Get a specific job by ID"""
    response = db.table("jobs").select("*").eq("id", job_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return response.data


@router.get("/matches/{user_id}")
async def get_job_matches(
    user_id: str,
    min_score: int = Query(70, ge=0, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db)
):
    """Get matched jobs for a user"""
    response = db.table("job_matches").select(
        "*,jobs(*)"
    ).eq("user_id", user_id).gte("match_score", min_score).order(
        "match_score", desc=True
    ).range(skip, skip + limit - 1).execute()
    
    return {
        "matches": response.data,
        "count": len(response.data),
        "min_score": min_score
    }


@router.post("/match-all/{user_id}")
async def match_all_jobs(
    user_id: str,
    background_tasks: BackgroundTasks,
    max_jobs: int = Query(50, ge=1, le=200),
    db: Client = Depends(get_db)
):
    """Trigger AI matching for all active jobs for a user"""
    
    # Get user profile
    profile_response = db.table("profiles").select("*").eq(
        "id", user_id
    ).single().execute()
    
    if not profile_response.data:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = profile_response.data
    
    # Check if resume exists
    if not profile.get("resume_text"):
        raise HTTPException(
            status_code=400, 
            detail="Resume required. Please upload your resume first."
        )
    
    # Queue background task for matching
    background_tasks.add_task(
        JobMatcherService.batch_match_jobs,
        user_id=user_id,
        profile=profile,
        max_jobs=max_jobs
    )
    
    return {
        "status": "queued",
        "message": f"AI matching started for up to {max_jobs} jobs",
        "user_id": user_id
    }
