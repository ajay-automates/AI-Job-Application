"""
Automation API Router
Handles automated job application tasks
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from supabase import Client
from app.database import get_db
from app.services.form_filler import FormFillerService
from app.services.job_scraper import JobScraperService

router = APIRouter()


class AutoApplyRequest(BaseModel):
    user_id: str
    job_url: str
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None


class ScrapeJobsRequest(BaseModel):
    keywords: str
    location: Optional[str] = None
    max_results: int = 50


@router.post("/apply")
async def auto_apply(
    request: AutoApplyRequest,
    background_tasks: BackgroundTasks,
    db: Client = Depends(get_db)
):
    """Automatically apply to a job"""
    
    # Get user profile for resume data
    profile_response = db.table("profiles").select("*").eq(
        "id", request.user_id
    ).single().execute()
    
    if not profile_response.data:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = profile_response.data
    
    # Create application record
    app_data = {
        "user_id": request.user_id,
        "status": "in_progress",
        "automation_enabled": True,
        "automation_status": "queued"
    }
    
    app_response = db.table("applications").insert(app_data).execute()
    application_id = app_response.data[0]["id"]
    
    # Queue background task
    background_tasks.add_task(
        FormFillerService.fill_and_apply,
        application_id=application_id,
        job_url=request.job_url,
        profile=profile,
        resume_url=request.resume_url or profile.get("resume_url"),
        cover_letter=request.cover_letter
    )
    
    return {
        "application_id": application_id,
        "status": "queued",
        "message": "Application automation started"
    }


@router.post("/scrape-jobs")
async def scrape_jobs(
    request: ScrapeJobsRequest,
    background_tasks: BackgroundTasks,
    db: Client = Depends(get_db)
):
    """Scrape jobs from job boards"""
    
    # Queue background task
    background_tasks.add_task(
        JobScraperService.scrape_and_save,
        keywords=request.keywords,
        location=request.location,
        max_results=request.max_results
    )
    
    return {
        "status": "queued",
        "message": f"Job scraping started for '{request.keywords}'"
    }


@router.get("/status/{application_id}")
async def get_automation_status(
    application_id: str,
    db: Client = Depends(get_db)
):
    """Get automation status for an application"""
    
    response = db.table("applications").select(
        "automation_status,automation_error"
    ).eq("id", application_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return response.data


@router.get("/logs/{application_id}")
async def get_automation_logs(
    application_id: str,
    db: Client = Depends(get_db)
):
    """Get automation logs for an application"""
    
    response = db.table("automation_logs").select("*").eq(
        "application_id", application_id
    ).order("created_at", desc=True).execute()
    
    return {
        "logs": response.data,
        "count": len(response.data)
    }
