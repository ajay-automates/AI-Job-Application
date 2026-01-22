"""
Resume Parser Service
Extracts information from resume files
"""
import io
from typing import Dict, Any
from openai import OpenAI
from app.config import settings


class ResumeParserService:
    """Service to parse resume files"""
    
    @staticmethod
    async def parse_resume(content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured information
        Uses OpenAI to extract key information
        """
        
        # For now, we'll do basic text extraction
        # In production, you'd use a proper PDF/DOCX parser
        
        try:
            # Try to decode as text
            text = content.decode('utf-8', errors='ignore')
        except:
            text = str(content)
        
        # Use OpenAI to extract structured data
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith('sk-'):
            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"""
                Extract the following information from this resume:
                - Full name
                - Email
                - Phone number
                - Location (city, state)
                - Skills (comma separated)
                - Years of experience
                - Education (degree and institution)
                - Work experience summary
                
                Resume text:
                {text[:3000]}  # First 3000 chars
                
                Return as JSON with keys: name, email, phone, location, skills, experience_years, education, summary
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                import json
                parsed = json.loads(response.choices[0].message.content)
                
                return {
                    "text": text,
                    "phone": parsed.get("phone"),
                    "location": parsed.get("location"),
                    "parsed_data": parsed
                }
            
            except Exception as e:
                print(f"OpenAI parsing error: {e}")
        
        # Fallback: return raw text
        return {
            "text": text,
            "phone": None,
            "location": None,
            "parsed_data": {}
        }
