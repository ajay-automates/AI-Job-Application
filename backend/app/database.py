"""
Database utilities and Supabase client
"""
from supabase import create_client, Client
from app.config import settings


class Database:
    """Supabase database client wrapper"""
    
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client"""
        if cls._client is None:
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        return cls._client
    
    @classmethod
    def get_anon_client(cls, access_token: str = None) -> Client:
        """Get Supabase client with user auth token"""
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        if access_token:
            client.auth.set_session(access_token, "")
        return client


# Dependency for FastAPI routes
def get_db() -> Client:
    """FastAPI dependency to get database client"""
    return Database.get_client()
