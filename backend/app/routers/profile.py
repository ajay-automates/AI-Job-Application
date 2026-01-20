"""
Profile API Router
Handles user profile and resume management
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from supabase import Client
from datetime import datetime
from app.database import get_db
from app.services.resume_parser import ResumeParserService

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    resume_text: Optional[str] = None
    preferences: Optional[dict] = None


@router.get("/{user_id}")
async def get_profile(
    user_id: str,
    db: Client = Depends(get_db)
):
    """Get user profile"""
    response = db.table("profiles").select("*").eq("id", user_id).single().execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return response.data


@router.patch("/{user_id}")
async def update_profile(
    user_id: str,
    update: ProfileUpdate,
    db: Client = Depends(get_db)
):
    """Update user profile"""
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now().isoformat()
    
    response = db.table("profiles").update(update_data).eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return response.data[0]


@router.post("/{user_id}/resume")
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...),
    db: Client = Depends(get_db)
):
    """Upload and parse resume"""
    
    # Read file content
    content = await file.read()
    
    # Parse resume
    parsed_data = await ResumeParserService.parse_resume(content, file.filename)
    
    # Update profile with parsed data
    update_data = {
        "resume_text": parsed_data.get("text", ""),
        "resume_url": parsed_data.get("url", ""),
        "updated_at": datetime.now().isoformat()
    }
    
    # Extract additional info if available
    if parsed_data.get("phone"):
        update_data["phone"] = parsed_data["phone"]
    if parsed_data.get("location"):
        update_data["location"] = parsed_data["location"]
    
    response = db.table("profiles").update(update_data).eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "message": "Resume uploaded successfully",
        "profile": response.data[0],
        "parsed_data": parsed_data
    }


@router.delete("/{user_id}/resume")
async def delete_resume(
    user_id: str,
    db: Client = Depends(get_db)
):
    """Delete resume from profile"""
    update_data = {
        "resume_text": None,
        "resume_url": None,
        "updated_at": datetime.now().isoformat()
    }
    
    response = db.table("profiles").update(update_data).eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Resume deleted successfully"}
