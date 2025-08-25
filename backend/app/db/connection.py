from supabase import create_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_supabase_client():
    """Create Supabase client with proper error handling"""
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("Missing Supabase configuration: SUPABASE_URL and SUPABASE_KEY are required")
            raise ValueError("Missing Supabase configuration")
        
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Supabase client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise e

# Create the global client
try:
    supabase = create_supabase_client()
except Exception as e:
    # Log the error but don't crash the application at import time
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    supabase = None
