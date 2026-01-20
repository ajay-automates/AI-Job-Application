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
            
            # Prepare form data in the format expected by form_filler.py
            # form_filler.py expects: url, form_context, user_input_template
            form_data = {
                "url": job_url,
                "form_context": {
                    "job_url": job_url,
                    "form_type": "application_form"
                },
                "user_input_template": [
                    {
                        "field_name": "full_name",
                        "field_type": "text",
                        "value": profile.get("full_name", ""),
                        "label": "Full Name"
                    },
                    {
                        "field_name": "email",
                        "field_type": "email",
                        "value": profile.get("email", ""),
                        "label": "Email"
                    },
                    {
                        "field_name": "phone",
                        "field_type": "tel",
                        "value": profile.get("phone", ""),
                        "label": "Phone"
                    },
                    {
                        "field_name": "location",
                        "field_type": "text",
                        "value": profile.get("location", ""),
                        "label": "Location"
                    },
                    {
                        "field_name": "resume_text",
                        "field_type": "textarea",
                        "value": profile.get("resume_text", ""),
                        "label": "Resume"
                    }
                ]
            }
            
            # Add cover letter if provided
            if cover_letter:
                form_data["user_input_template"].append({
                    "field_name": "cover_letter",
                    "field_type": "textarea",
                    "value": cover_letter,
                    "label": "Cover Letter"
                })
            
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
            if not automator_path:
                # In production, form filler might not be available
                # For now, mark as queued and provide instructions
                db.table("applications").update({
                    "automation_status": "queued",
                    "automation_error": "Form filler not configured. JOB_AUTOMATOR_PATH not set in production. Browser automation requires local setup or headless browser service.",
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filler_not_configured",
                    "success": False,
                    "error_message": "JOB_AUTOMATOR_PATH not configured. Browser automation requires special setup for production.",
                    "metadata": {
                        "job_url": job_url,
                        "note": "For production, consider using a headless browser service or running automation locally"
                    }
                }).execute()
                return  # Exit early
            
            script_path = f"{automator_path}/job_application_automator/form_filler.py"
            
            # Verify script exists
            import os
            if not os.path.exists(script_path):
                error_msg = f"Form filler script not found at: {script_path}. Please verify JOB_AUTOMATOR_PATH is correct."
                db.table("applications").update({
                    "automation_status": "failed",
                    "automation_error": error_msg,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filler_script_not_found",
                    "success": False,
                    "error_message": error_msg
                }).execute()
                return  # Exit early
            
            # Run form filler (it expects just the JSON file path as argument)
            try:
                process = await asyncio.create_subprocess_exec(
                    "python3",
                    script_path,
                    form_data_file,  # Just the JSON file path, no --json or --url flags
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=automator_path  # Set working directory
                )
                
                stdout, stderr = await process.communicate()
                
                # Clean up temp file
                try:
                    os.unlink(form_data_file)
                except:
                    pass  # Ignore cleanup errors
                
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
            except Exception as process_error:
                # Handle subprocess errors
                error_msg = str(process_error)
                db.table("applications").update({
                    "automation_status": "failed",
                    "automation_error": f"Failed to run form filler: {error_msg}",
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filler_process_error",
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
