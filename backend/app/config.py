"""
Configuration management for backend API
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # MCP Integration
    JOB_AUTOMATOR_PATH: str = os.getenv("JOB_AUTOMATOR_PATH", os.getcwd())
    JOB_BOARD_AGGREGATOR_URL: str = os.getenv("JOB_BOARD_AGGREGATOR_URL", "http://localhost:8080")
    API_AUTH_HASH: str = os.getenv("API_AUTH_HASH", "your-secure-auth-hash-change-in-production")
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
