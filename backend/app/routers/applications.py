"""
Applications API Router
Handles job application tracking and management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from supabase import Client
from datetime import datetime
from app.database import get_db

router = APIRouter()


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
