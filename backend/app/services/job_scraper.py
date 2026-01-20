"""
Job Scraper Service
Integrates with the job-board-aggregator backend
"""
import httpx
from typing import Optional
from datetime import datetime
from app.config import settings
from app.database import Database


class JobScraperService:
    """Service to scrape jobs from job boards"""
    
    @staticmethod
    async def scrape_and_save(
        keywords: str,
        location: Optional[str] = None,
        max_results: int = 50
    ):
        """
        Scrape jobs and save to database
        Integrates with existing job-board-aggregator
        """
        db = Database.get_client()
        
        try:
            # Call job board aggregator API with authentication
            async with httpx.AsyncClient() as client:
                params = {
                    "keywords": keywords,
                    "max_results": max_results
                }
                if location:
                    params["location"] = location
                
                # Add authentication header
                headers = {
                    "Authorization": f"Bearer {settings.API_AUTH_HASH}"
                }
                
                response = await client.get(
                    f"{settings.JOB_BOARD_AGGREGATOR_URL}/server/jobs/search",
                    params=params,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    jobs_data = response.json()
                    jobs = jobs_data.get("jobs", [])
                    
                    # Save jobs to database
                    saved_count = 0
                    for job in jobs:
                        try:
                            # Check if job already exists
                            existing = db.table("jobs").select("id").eq(
                                "url", job["url"]
                            ).execute()
                            
                            if not existing.data:
                                # Insert new job
                                job_record = {
                                    "title": job.get("title", ""),
                                    "company": job.get("company", ""),
                                    "url": job.get("url", ""),
                                    "description": job.get("description", ""),
                                    "location": job.get("location", ""),
                                    "salary_min": job.get("salary_min"),
                                    "salary_max": job.get("salary_max"),
                                    "salary_currency": job.get("salary_currency", "USD"),
                                    "job_type": job.get("job_type"),
                                    "remote_type": job.get("remote_type"),
                                    "source": job.get("source", "aggregator"),
                                    "raw_data": job,
                                    "scraped_at": datetime.now().isoformat(),
                                    "is_active": True
                                }
                                
                                db.table("jobs").insert(job_record).execute()
                                saved_count += 1
                        
                        except Exception as e:
                            print(f"Error saving job: {e}")
                            continue
                    
                    # Log result
                    db.table("automation_logs").insert({
                        "action": "job_scraping_completed",
                        "success": True,
                        "metadata": {
                            "keywords": keywords,
                            "location": location,
                            "jobs_found": len(jobs),
                            "jobs_saved": saved_count
                        }
                    }).execute()
                    
                    # Trigger auto-matching for all users with resumes
                    if saved_count > 0:
                        try:
                            from app.services.job_matcher import JobMatcherService
                            
                            # Get all users with resumes
                            users_response = db.table("profiles").select("id,resume_text").execute()
                            users_with_resumes = [
                                u for u in users_response.data 
                                if u.get("resume_text")
                            ]
                            
                            # Trigger matching for each user (in background)
                            for user in users_with_resumes:
                                try:
                                    # Match only the new jobs
                                    await JobMatcherService.batch_match_jobs(
                                        user_id=user["id"],
                                        profile=user,
                                        max_jobs=saved_count
                                    )
                                except Exception as e:
                                    print(f"Error matching jobs for user {user['id']}: {e}")
                        except Exception as e:
                            print(f"Error triggering auto-matching: {e}")
                    
                    return {
                        "success": True,
                        "jobs_found": len(jobs),
                        "jobs_saved": saved_count
                    }
                else:
                    raise Exception(f"API returned status {response.status_code}")
        
        except Exception as e:
            # Log error
            db.table("automation_logs").insert({
                "action": "job_scraping_failed",
                "success": False,
                "error_message": str(e),
                "metadata": {
                    "keywords": keywords,
                    "location": location
                }
            }).execute()
            
            return {
                "success": False,
                "error": str(e)
            }
