"""
Form Filler Service
Integrates with the job-application-automator MCP server
"""
import asyncio
import json
import subprocess
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.database import Database

logger = logging.getLogger(__name__)

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
        Fill and apply to a job with timeout protection.
        
        Timeout: 5 minutes max
        If exceeds timeout: Mark as failed with error_code='timeout'
        """
        db = Database.get_client()
        
        try:
            # Update status to "in_progress"
            db.table("applications").update({
                "automation_status": "in_progress",
                "last_attempted_at": datetime.utcnow().isoformat()
            }).eq("id", application_id).execute()
            
            logger.info(f"Starting auto-apply for application {application_id}")
            
            # WRAP THE ENTIRE PROCESS WITH TIMEOUT
            try:
                await asyncio.wait_for(
                    FormFillerService._execute_form_filling(
                        application_id=application_id,
                        job_url=job_url,
                        profile=profile,
                        resume_url=resume_url,
                        cover_letter=cover_letter
                    ),
                    timeout=300  # 5 minutes timeout
                )
                
                # If we get here, it succeeded (or failed responsibly within)
                logger.info(f"Successfully completed auto-apply for {application_id}")
                
            except asyncio.TimeoutError:
                logger.error(f"AUTO-APPLY TIMEOUT: Application {application_id} took > 5 minutes")
                
                # Update database with timeout error
                db.table("applications").update({
                    "automation_status": "failed",
                    "error_code": "timeout",
                    "error_message": "Form filling timeout: Process exceeded 5 minute limit",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", application_id).execute()
                
                # Log the failure
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filling_timeout",
                    "success": False,
                    "error_message": "Form filling timeout: Process exceeded 5 minute limit",
                    "metadata": {"timeout_seconds": 300, "error_code": "timeout"}
                }).execute()
                
                raise
            
        except Exception as e:
            # Check if it was already handled (e.g. timeout)
            if isinstance(e, asyncio.TimeoutError):
                return

            logger.error(f"Error in fill_and_apply: {str(e)}", exc_info=True)
            
            # Update database with error
            db.table("applications").update({
                "automation_status": "failed",
                "error_code": "exception",
                "error_message": str(e),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", application_id).execute()
            
            # Log the failure
            db.table("automation_logs").insert({
                "application_id": application_id,
                "user_id": profile["id"],
                "action": "form_filling_error",
                "success": False,
                "error_message": str(e),
                "metadata": {"error": str(e), "error_code": "exception"}
            }).execute()

    @staticmethod
    async def _execute_form_filling(
        application_id: str,
        job_url: str,
        profile: Dict[str, Any],
        resume_url: Optional[str] = None,
        cover_letter: Optional[str] = None
    ):
        """
        Actual form filling logic (separated for timeout wrapping)
        Add logging at each major step
        """
        db = Database.get_client()
        
        # STEP 1: Extraction
        logger.info(f"[{application_id}] Step 1: Starting form extraction")
        
        db.table("applications").update({
            "automation_status": "extracting",
            "updated_at": datetime.now().isoformat()
        }).eq("id", application_id).execute()

        db.table("automation_logs").insert({
            "application_id": application_id,
            "user_id": profile["id"],
            "action": "form_extraction_started",
            "success": True,
            "metadata": {"job_url": job_url}
        }).execute()
        
        # Prepare form data
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
        
        if cover_letter:
            form_data["user_input_template"].append({
                "field_name": "cover_letter",
                "field_type": "textarea",
                "value": cover_letter,
                "label": "Cover Letter"
            })
        
        import tempfile
        
        form_data_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(form_data, f)
                form_data_file = f.name
            
            logger.info(f"[{application_id}] Step 2: Filling form fields")
            
            db.table("applications").update({
                "automation_status": "filling",
                "form_data": form_data,
                "updated_at": datetime.now().isoformat()
            }).eq("id", application_id).execute()
            
            automator_path = settings.JOB_AUTOMATOR_PATH
            if not automator_path:
                msg = "JOB_AUTOMATOR_PATH not configured. Browser automation requires special setup for production."
                db.table("applications").update({
                    "automation_status": "queued",
                    "automation_error": msg,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", application_id).execute()
                
                db.table("automation_logs").insert({
                    "application_id": application_id,
                    "user_id": profile["id"],
                    "action": "form_filler_not_configured",
                    "success": False,
                    "error_message": msg,
                    "metadata": {
                        "job_url": job_url,
                        "note": "For production, consider using a headless browser service or running automation locally"
                    }
                }).execute()
                # Stop but don't raise as error, just queued
                return

            script_path = f"{automator_path}/job_application_automator/form_filler.py"
            
            if not os.path.exists(script_path):
                # Fallback
                fallback_script = os.path.join(os.getcwd(), "job_application_automator", "form_filler.py")
                if os.path.exists(fallback_script):
                    script_path = fallback_script
                    automator_path = os.getcwd()
                
            if not os.path.exists(script_path):
                raise Exception(f"Form filler script not found at {script_path}")
            
            logger.info(f"[{application_id}] Step 3: Submitting form (running script)")
            
            # Comprehensive logging before subprocess launch
            logger.info(f"[{application_id}] Launching subprocess:")
            logger.info(f"  Command: python3")
            logger.info(f"  Script: {script_path}")
            logger.info(f"  Args: {form_data_file}")
            logger.info(f"  CWD: {automator_path}")
            logger.info(f"  Script exists: {os.path.exists(script_path)}")
            logger.info(f"  Form data file exists: {os.path.exists(form_data_file)}")
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "python3",
                    script_path,
                    form_data_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=automator_path
                )
                logger.info(f"[{application_id}] Subprocess created successfully (PID: {process.pid})")
            except Exception as launch_error:
                logger.error(f"[{application_id}] Failed to launch subprocess: {launch_error}", exc_info=True)
                raise
            
            # ✅ READ OUTPUT IN REAL-TIME (streaming)
            stdout_lines = []
            stderr_lines = []
            
            # Read stdout line by line
            async def read_stream(stream, output_list, stream_name):
                while True:
                    try:
                        line = await asyncio.wait_for(stream.readline(), timeout=1.0)
                        if not line:
                            break
                        decoded = line.decode('utf-8', errors='replace').strip()
                        if decoded:
                            output_list.append(decoded)
                            logger.info(f"[SUBPROCESS {stream_name}] {decoded}")
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error reading {stream_name}: {e}")
                        break
            
            # Create tasks to read stdout and stderr concurrently
            stdout_task = asyncio.create_task(read_stream(process.stdout, stdout_lines, "STDOUT"))
            stderr_task = asyncio.create_task(read_stream(process.stderr, stderr_lines, "STDERR"))
            
            # Wait for process to complete
            returncode = await process.wait()
            
            # Cancel the read tasks
            stdout_task.cancel()
            stderr_task.cancel()
            
            # Give final reads a moment to complete
            try:
                await asyncio.gather(stdout_task, stderr_task)
            except asyncio.CancelledError:
                pass
            
            # Combine outputs
            stdout = "\n".join(stdout_lines).encode('utf-8')
            stderr = "\n".join(stderr_lines).encode('utf-8')
            
            logger.info(f"Subprocess completed with return code: {returncode}")
            
            if returncode == 0:
                logger.info(f"[{application_id}] Completed successfully")
                
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
                error_msg = stderr.decode()
                raise Exception(f"Form filler script failed: {error_msg}")
        
        finally:
            # Clean up temp file
            if form_data_file and os.path.exists(form_data_file):
                try:
                    os.unlink(form_data_file)
                except:
                    pass
