"""
Job Matcher Service
AI-powered job matching based on resume and job description
"""
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings
from app.database import Database


class JobMatcherService:
    """Service to match jobs with user profiles using AI"""
    
    @staticmethod
    async def calculate_match_score(
        user_id: str,
        job_id: str,
        profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate match score between user and job
        Returns score (0-100) and reasons
        """
        
        resume_text = profile.get("resume_text", "")
        job_description = job.get("description", "")
        job_title = job.get("title", "")
        
        if not resume_text or not job_description:
            return {
                "match_score": 0,
                "match_reasons": [],
                "ai_analysis": "Insufficient data for matching"
            }
        
        # Use OpenAI to calculate match
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith('sk-'):
            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"""
                Analyze how well this candidate matches this job.
                
                Job Title: {job_title}
                Job Description: {job_description[:2000]}
                
                Candidate Resume: {resume_text[:2000]}
                
                Provide:
                1. Match score (0-100)
                2. Top 3-5 reasons for the score
                3. Brief analysis
                
                Return as JSON with keys: score, reasons (array), analysis (string)
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                
                # Save match to database
                db = Database.get_client()
                match_data = {
                    "user_id": user_id,
                    "job_id": job_id,
                    "match_score": result.get("score", 0),
                    "match_reasons": result.get("reasons", []),
                    "ai_analysis": result.get("analysis", "")
                }
                
                # Check if match already exists
                existing = db.table("job_matches").select("id").eq(
                    "user_id", user_id
                ).eq("job_id", job_id).execute()
                
                if existing.data:
                    # Update existing
                    db.table("job_matches").update(match_data).eq(
                        "id", existing.data[0]["id"]
                    ).execute()
                else:
                    # Insert new
                    db.table("job_matches").insert(match_data).execute()
                
                return match_data
            
            except Exception as e:
                print(f"Matching error: {e}")
        
        # Fallback: simple keyword matching
        return {
            "match_score": 50,
            "match_reasons": ["Basic keyword match"],
            "ai_analysis": "AI matching unavailable, using fallback"
        }
    
    @staticmethod
    async def batch_match_jobs(
        user_id: str,
        profile: Dict[str, Any],
        max_jobs: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Match user with multiple jobs
        """
        db = Database.get_client()
        
        # Get active jobs
        jobs_response = db.table("jobs").select("*").eq(
            "is_active", True
        ).limit(max_jobs).execute()
        
        jobs = jobs_response.data
        matches = []
        
        for job in jobs:
            try:
                match = await JobMatcherService.calculate_match_score(
                    user_id=user_id,
                    job_id=job["id"],
                    profile=profile,
                    job=job
                )
                matches.append(match)
            except Exception as e:
                print(f"Error matching job {job['id']}: {e}")
                continue
        
        return matches
