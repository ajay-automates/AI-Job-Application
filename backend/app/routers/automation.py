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
    job_id: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None


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
    
    # Get or create job record if job_url provided
    job_id = request.job_id
    if request.job_url and not job_id:
        try:
            # Check if job exists with this URL
            existing_job = db.table("jobs").select("id").eq("url", request.job_url).maybe_single().execute()
            
            if existing_job.data:
                job_id = existing_job.data["id"]
            else:
                # Create a job record from URL
                new_job = db.table("jobs").insert({
                    "title": request.job_title or "Job from URL",
                    "company": request.company or "Unknown",
                    "url": request.job_url,
                    "description": f"Job application URL: {request.job_url}",
                    "is_active": True,
                    "source": "manual_url"
                }).execute()
                if new_job.data:
                    job_id = new_job.data[0]["id"]
        except Exception as job_error:
            # If job creation fails, continue without job_id
            # Application can still be created without job record
            print(f"Warning: Could not create/find job record: {job_error}")
            job_id = None
    
    # Create application record
    app_data = {
        "user_id": request.user_id,
        "status": "in_progress",
        "automation_enabled": True,
        "automation_status": "queued"
    }
    
    if job_id:
        app_data["job_id"] = job_id
    
    try:
        app_response = db.table("applications").insert(app_data).execute()
        
        if not app_response.data:
            raise HTTPException(status_code=500, detail="Failed to create application record")
        
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
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"Error creating application: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Failed to create application: {error_msg}")


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
