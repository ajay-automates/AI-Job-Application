"""
Jobs API Router
Handles job listing operations
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from app.database import get_db

router = APIRouter()


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
