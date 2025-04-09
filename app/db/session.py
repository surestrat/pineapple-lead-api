import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)
supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Initializes and returns the Supabase client (lazy initialization)."""
    global supabase_client
    if supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.critical("Supabase URL or Key not configured!")
            raise ConnectionError("Supabase URL or Key not configured.")
        try:
            logger.info(
                f"Initializing Supabase client with URL: {settings.SUPABASE_URL[:20]}..."
            )
            supabase_client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized successfully.")

            # Test the connection by making a simple query
            try:
                # Try to fetch one row from the users table as a test
                test_result = (
                    supabase_client.table("users").select("id").limit(1).execute()
                )
                if test_result.data is not None:
                    logger.info(
                        "Supabase connection test successful - users table is accessible."
                    )
                else:
                    logger.warning(
                        "Supabase connection test completed but returned no data."
                    )
            except Exception as test_e:
                logger.warning(f"Supabase connection test failed: {test_e}")
                # Don't raise here, just log the warning

        except Exception as e:
            logger.exception("Error initializing Supabase client!")
            raise ConnectionError(f"Could not connect to Supabase: {e}") from e
    return supabase_client


# Dependency for FastAPI
def get_db():
    """FastAPI dependency to get Supabase client."""
    try:
        client = get_supabase_client()
        yield client
    except Exception as e:
        logger.exception("Error occurred within Supabase client request context.")
        # Re-raise for FastAPI's exception handling
        raise
