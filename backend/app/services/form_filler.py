"""
Form Filler Service
Integrates with the job-application-automator MCP server
"""
import asyncio
import json
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.database import Database


class FormFillerService:
    """Service to fill job application forms"""
    
    @staticmethod
    async def fill_and_apply(
        application_id: str,
        job_url: str,
        profile: Dict[str, Any],
        resume_url: Optional[str] = None,
        cover_letter: Optional[str] = None
    ):
        """
        Fill and submit job application form
        Integrates with the existing form_filler.py from MCP server
        """
        db = Database.get_client()
        
        try:
            # Update status
            db.table("applications").update({
                "automation_status": "extracting",
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            # Log start
            db.table("automation_logs").insert({
                "application_id": application_id,
                "user_id": profile["id"],
                "action": "form_extraction_started",
                "success": True,
                "metadata": {"job_url": job_url}
            }).execute()
            
            # Prepare form data from profile
            form_data = {
                "personal_info": {
                    "full_name": profile.get("full_name", ""),
                    "email": profile.get("email", ""),
                    "phone": profile.get("phone", ""),
                    "location": profile.get("location", "")
                },
                "resume_url": resume_url,
                "cover_letter": cover_letter,
                "resume_text": profile.get("resume_text", "")
            }
            
            # Create temporary JSON file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(form_data, f)
                form_data_file = f.name
            
            # Update status
            db.table("applications").update({
                "automation_status": "filling",
                "form_data": form_data,
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            # Call the form filler script
            automator_path = settings.JOB_AUTOMATOR_PATH
            script_path = f"{automator_path}/job_application_automator/form_filler.py"
            
            # Run form filler
            process = await asyncio.create_subprocess_exec(
                "python3",
                script_path,
                "--json", form_data_file,
                "--url", job_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up temp file
            import os
            os.unlink(form_data_file)
            
            if process.returncode == 0:
                # Success
                db.table("applications").update({
                    "automation_status": "completed",
                    "status": "applied",
                    "applied_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filled_success",
                    "success": True,
                    "metadata": {
                        "job_url": job_url,
                        "output": stdout.decode()
                    }
                }).execute()
            else:
                # Failed
                error_msg = stderr.decode()
                db.table("applications").update({
                    "automation_status": "failed",
                    "automation_error": error_msg,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filled_failed",
                    "success": False,
                    "error_message": error_msg
                }).execute()
        
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            db.table("applications").update({
                "automation_status": "failed",
                "automation_error": error_msg,
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            db.table("automation_logs").insert({
                "application_id": application_id,
                "user_id": profile["id"],
                "action": "form_filling_error",
                "success": False,
                "error_message": error_msg
            }).execute()
