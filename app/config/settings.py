import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuration settings for the application.
    This class manages various configuration settings loaded from environment variables,
    providing fallback default values when environment variables are not set.
    Attributes:
            secret_key (str): Secret key for JWT token generation and validation.
                    Defaults to "your-secret-key".
            algorithm (str): Algorithm used for JWT token encoding/decoding.
                    Defaults to "HS256".
            appwrite_endpoint (str): Endpoint URL for Appwrite service.
                    Defaults to "YOUR_APPWRITE_ENDPOINT".
            appwrite_project_id (str): Project ID for Appwrite service.
                    Defaults to "YOUR_APPWRITE_PROJECT_ID".
            appwrite_api_key (str): API key for Appwrite service authentication.
                    Defaults to "YOUR_APPWRITE_API_KEY".
            appwrite_database_id (str): Database ID for Appwrite service.
                    Defaults to "YOUR_DATABASE_ID".
            appwrite_leads_collection_id (str): Collection ID for leads in Appwrite.
                    Defaults to "leads".
            appwrite_quotes_collection_id (str): Collection ID for quotes in Appwrite.
                    Defaults to "quotes".
            rate_limit (int): Maximum number of requests allowed.
                    Defaults to 100.
            log_level (str): Logging level for the application.
                    Defaults to "INFO".
            api_bearer_token (str): Bearer token for API authentication.
                    Defaults to "your-bearer-token".
            protected_endpoints (list): List of protected endpoints.
                    Defaults to ["/api/v1/leads", "/api/v1/quotes"].
            pineapple_api_base_url (str): Base URL for Pineapple API.
                    Defaults to "http://gw-test.pineapple.co.za".
            pineapple_lead_endpoint (str): Endpoint for Pineapple lead.
                    Defaults to "/users/motor_lead".
            pineapple_quote_endpoint (str): Endpoint for Pineapple quote.
                    Defaults to "/api/v1/quote/quick-quote".
    """

    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    appwrite_endpoint: str = os.getenv("APPWRITE_ENDPOINT", "YOUR_APPWRITE_ENDPOINT")
    appwrite_project_id: str = os.getenv(
        "APPWRITE_PROJECT_ID", "YOUR_APPWRITE_PROJECT_ID"
    )
    appwrite_api_key: str = os.getenv("APPWRITE_API_KEY", "YOUR_APPWRITE_API_KEY")
    appwrite_database_id: str = os.getenv("APPWRITE_DATABASE_ID", "YOUR_DATABASE_ID")
    appwrite_leads_collection_id: str = os.getenv(
        "APPWRITE_LEADS_COLLECTION_ID", "leads"
    )
    appwrite_quotes_collection_id: str = os.getenv(
        "APPWRITE_QUOTES_COLLECTION_ID", "quotes"
    )
    rate_limit: int = int(os.getenv("RATE_LIMIT", 100))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_bearer_token: str = os.getenv("API_BEARER_TOKEN", "your-bearer-token")
    protected_endpoints: list = os.getenv(
        "PROTECTED_ENDPOINTS", "/api/v1/leads,/api/v1/quotes"
    ).split(",")
    pineapple_api_base_url: str = os.getenv(
        "PINEAPPLE_API_BASE_URL", "http://gw-test.pineapple.co.za"
    )
    pineapple_lead_endpoint: str = os.getenv(
        "PINEAPPLE_LEAD_ENDPOINT", "/users/motor_lead"
    )
    pineapple_quote_endpoint: str = os.getenv(
        "PINEAPPLE_QUOTE_ENDPOINT", "/api/v1/quote/quick-quote"
    )


settings = Settings()
