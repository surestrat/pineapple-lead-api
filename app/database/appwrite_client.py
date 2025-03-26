from appwrite.client import Client
from app.config.settings import settings


def get_appwrite_client() -> Client:
    """
    Get an initialized Appwrite client.
    This function initializes and configures an Appwrite Client instance with application settings.
    Returns:
            Client: A configured Appwrite Client instance ready for interacting with the Appwrite API.
    """

    client = Client()
    client.set_endpoint(settings.appwrite_endpoint)
    client.set_project(settings.appwrite_project_id)
    client.set_key(settings.appwrite_api_key)
    return client
