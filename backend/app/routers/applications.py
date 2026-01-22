"""
Applications API Router
Handles job application tracking and management
"""
# Define router first to ensure it's always available, even if imports fail
from fastapi import APIRouter
router = APIRouter()

# Now import other dependencies
from typing import List, Optional
from fastapi import Depends, HTTPException, Query, Body
from pydantic import BaseModel
from supabase import Client
from datetime import datetime
from app.database import get_db


class ApplicationCreate(BaseModel):
    job_id: str
    user_id: str
    status: str = "pending"
    form_data: Optional[dict] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    automation_enabled: bool = False


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    submitted_application_url: Optional[str] = None
    submission_confirmed: Optional[bool] = None


class ApplicationOutcome(BaseModel):
    outcome: str
    user_id: str


@router.get("/")
async def get_applications(
    user_id: str = Query(...),
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db)
):
    """Get user's applications"""
    query = db.table("applications").select(
        "*,jobs(*)"
    ).eq("user_id", user_id)
    
    if status:
        query = query.eq("status", status)
    
    response = query.order("created_at", desc=True).range(
        skip, skip + limit - 1
    ).execute()
    
    return {
        "applications": response.data,
        "count": len(response.data)
    }


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    db: Client = Depends(get_db)
):
    """Get a specific application"""
    response = db.table("applications").select(
        "*,jobs(*)"
    ).eq("id", application_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return response.data


@router.post("/")
async def create_application(
    application: ApplicationCreate,
    db: Client = Depends(get_db)
):
    """Create a new application"""
    app_data = application.dict()
    app_data["created_at"] = datetime.now().isoformat()
    app_data["updated_at"] = datetime.now().isoformat()
    
    response = db.table("applications").insert(app_data).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create application")
    
    return response.data[0]


@router.patch("/{application_id}")
async def update_application(
    application_id: str,
    update: ApplicationUpdate,
    db: Client = Depends(get_db)
):
    """Update an application"""
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now().isoformat()
    
    response = db.table("applications").update(update_data).eq(
        "id", application_id
    ).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return response.data[0]


@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    db: Client = Depends(get_db)
):
    """Delete an application"""
    response = db.table("applications").delete().eq("id", application_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Application deleted successfully"}


@router.get("/stats/{user_id}")
async def get_application_stats(
    user_id: str,
    db: Client = Depends(get_db)
):
    """Get application statistics for a user"""
    
    # Get all applications
    all_apps = db.table("applications").select("status").eq("user_id", user_id).execute()
    
    # Count by status
    stats = {}
    for app in all_apps.data:
        status = app.get("status", "unknown")
        stats[status] = stats.get(status, 0) + 1
    
    return {
        "total": len(all_apps.data),
        "by_status": stats
    }


@router.put("/{application_id}/outcome")
async def record_application_outcome(
    application_id: str,
    outcome_data: ApplicationOutcome,
    db: Client = Depends(get_db)
):
    """
    PHASE 1: Record application outcome
    This is how Phase 1 tracks if applications succeed or fail
    """
    outcome = outcome_data.outcome
    user_id = outcome_data.user_id
    
    # Validate outcome
    valid_outcomes = ['interview_scheduled', 'rejected', 'no_response', 'pending']
    if outcome not in valid_outcomes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid outcome. Must be one of: {valid_outcomes}"
        )
    
    # Update application
    response = db.table("applications").update({
        "application_outcome": outcome,
        "outcome_recorded_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", application_id).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Application not found or user mismatch")
    
    # Log the outcome recording
    db.table("automation_logs").insert({
        "application_id": application_id,
        "user_id": user_id,
        "action": "application_outcome_recorded",
        "success": True,
        "metadata": {"outcome": outcome}
    }).execute()
    
    return {"success": True, "outcome": outcome}


@router.get("/user/metrics")
async def get_application_metrics(
    user_id: str = Query(...),
    db: Client = Depends(get_db)
):
    """
    PHASE 1: Get metrics showing success rates
    This is how you PROVE your system works
    """
    
    # Get all applications for user
    all_apps = db.table("applications").select(
        "automation_status, application_outcome, error_code"
    ).eq("user_id", user_id).execute()
    
    apps = all_apps.data or []
    
    # Calculate metrics
    total_applications = len(apps)
    
    # Automation metrics
    automation_failed = sum(1 for a in apps if a.get('automation_status') == 'failed')
    automation_completed = sum(1 for a in apps if a.get('automation_status') == 'completed')
    
    # Outcome metrics  
    interviews = sum(1 for a in apps if a.get('application_outcome') == 'interview_scheduled')
    rejections = sum(1 for a in apps if a.get('application_outcome') == 'rejected')
    no_response = sum(1 for a in apps if a.get('application_outcome') == 'no_response')
    
    # Error codes
    timeouts = sum(1 for a in apps if a.get('error_code') == 'timeout')
    exceptions = sum(1 for a in apps if a.get('error_code') == 'exception')
    
    return {
        "total_applications": total_applications,
        "automation": {
            "completed": automation_completed,
            "failed": automation_failed,
            "success_rate": automation_completed / total_applications if total_applications > 0 else 0
        },
        "outcomes": {
            "interviews": interviews,
            "rejections": rejections,
            "no_response": no_response,
            "interview_rate": interviews / total_applications if total_applications > 0 else 0
        },
        "errors": {
            "timeouts": timeouts,
            "exceptions": exceptions
        }
    }
