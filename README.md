# Pineapple Lead API v2

A FastAPI-based service that integrates with Pineapple's insurance API for handling leads and quotes.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Data Flow](#data-flow)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

This API service acts as a middleware between client applications and Pineapple's insurance API. It handles:

- Lead management
- Quick quote generation
- Data persistence using Appwrite
- Authentication and rate limiting

## Features

- FastAPI-based REST API
- JWT Authentication
- Rate limiting
- Appwrite database integration
- Async HTTP client for external API calls
- Rich logging
- CORS support
- Input validation using Pydantic
- Error handling and monitoring

## Project Structure

```
app/
├── auth/
│   └── jwt_utils.py         # JWT authentication utilities
├── config/
│   └── settings.py          # Application configuration
├── database/
│   ├── appwrite_client.py   # Appwrite client setup
│   └── appwrite_service.py  # Database operations
├── middleware/
│   └── auth_middleware.py   # Authentication middleware
├── routes/
│   ├── auth.py             # Authentication endpoints
│   ├── leads.py            # Lead management endpoints
│   └── quotes.py           # Quote generation endpoints
├── schemas/
│   ├── auth_schemas.py     # Authentication models
│   ├── lead_schemas.py     # Lead data models
│   └── quote_schemas.py    # Quote data models
├── services/
│   ├── auth_services.py    # Authentication business logic
│   ├── lead_services.py    # Lead management logic
│   └── quote_services.py   # Quote generation logic
├── utils/
│   └── logger.py           # Logging configuration
├── .env                    # Environment variables
├── .env.example           # Environment template
└── main.py               # Application entry point
```

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd pineapple-lead-api-v2
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp app/.env.example app/.env
# Edit app/.env with your configuration
```

5. Run the application:

```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/token`: Get JWT access token
  ```json
  {
  	"username": "string",
  	"password": "string"
  }
  ```

### Leads

- `POST /api/v1/leads`: Create new lead
  ```json
  {
  	"source": "string",
  	"first_name": "string",
  	"last_name": "string",
  	"email": "string",
  	"id_number": "string",
  	"quote_id": "string",
  	"contact_number": "string"
  }
  ```

### Quotes

- `POST /api/v1/quotes`: Generate quick quote
  ```json
  {
  	"source": "string",
  	"externalReferenceId": "string",
  	"vehicles": [
  		{
  			"year": "integer",
  			"make": "string",
  			"model": "string"
  			// ... other vehicle details
  		}
  	]
  }
  ```

## Authentication

The API uses two types of authentication:

1. JWT tokens for internal API authentication
2. Bearer token for Pineapple API authentication

### JWT Authentication

- Used for protecting API endpoints
- Tokens issued via `/api/v1/auth/token`
- 30-minute expiration
- Required in Authorization header: `Bearer <token>`

### Pineapple API Authentication

- Bearer token configured in environment variables
- Automatically added to requests to Pineapple API
- Format: `KEY=<key> SECRET=<secret>`

## Data Flow

1. **Quote Generation**:

   ```
   Client → API → Appwrite (store) → Pineapple API → Update Appwrite → Response
   ```

2. **Lead Creation**:
   ```
   Client → API → Appwrite (store) → Pineapple API → Response
   ```

## Error Handling

- HTTP 400: Bad Request (validation errors)
- HTTP 401: Unauthorized (authentication failures)
- HTTP 429: Too Many Requests (rate limit exceeded)
- HTTP 500: Internal Server Error
- HTTP 502: Bad Gateway (Pineapple API errors)
- HTTP 504: Gateway Timeout (Pineapple API timeout)

## Logging

- Uses Rich for colored console output
- Log levels: DEBUG, INFO, WARNING, ERROR
- Logs stored with timestamp and context
- Configurable via LOG_LEVEL environment variable

## Environment Variables

```bash
SECRET_KEY=             # JWT secret key
ALGORITHM=              # JWT algorithm (HS256)
APPWRITE_ENDPOINT=      # Appwrite API endpoint
APPWRITE_PROJECT_ID=    # Appwrite project ID
APPWRITE_API_KEY=       # Appwrite API key
APPWRITE_DATABASE_ID=   # Appwrite database ID
APPWRITE_LEADS_COLLECTION_ID=   # Leads collection ID
APPWRITE_QUOTES_COLLECTION_ID=  # Quotes collection ID
RATE_LIMIT=            # Rate limit per minute
LOG_LEVEL=             # Logging level
API_BEARER_TOKEN=      # Pineapple API bearer token
PINEAPPLE_API_BASE_URL=    # Pineapple API base URL
PINEAPPLE_LEAD_ENDPOINT=   # Lead endpoint
PINEAPPLE_QUOTE_ENDPOINT=  # Quote endpoint
PROTECTED_ENDPOINTS=    # Comma-separated protected endpoints
```

## Rate Limiting

- Default: 100 requests per minute
- Configurable via RATE_LIMIT environment variable
- Applied globally and per endpoint
- Returns 429 status code when exceeded

## Development

1. Enable debug mode:

```bash
LOG_LEVEL=DEBUG
```

2. Run tests:

```bash
pytest
```

3. Format code:

```bash
black app/
```

## Production Deployment

1. Set secure environment variables
2. Configure proper CORS origins
3. Set production log level
4. Use proper SSL/TLS
5. Configure proper rate limits
6. Use production-grade ASGI server (e.g., Gunicorn with Uvicorn workers)

## Docker Deployment

### Using Docker

1. Build the Docker image:

```bash
docker build -t pineapple-lead-api .
```

2. Run the container:

```bash
docker run -d -p 8000:8000 --env-file app/.env --name pineapple-api pineapple-lead-api
```

### Using Docker Compose

1. Start the services:

```bash
docker-compose up -d
```

2. View logs:

```bash
docker-compose logs -f
```

3. Stop the services:

```bash
docker-compose down
```

### Docker Commands

- Rebuild the image: `docker-compose build`
- Restart services: `docker-compose restart`
- View container status: `docker-compose ps`
- Scale services: `docker-compose up -d --scale api=3`

## Testing

### Running Tests

You can test the API using the provided utilities.

#### 1. Using `test_api.py`

Run the `test_api.py` script to test specific endpoints or all endpoints:

```bash
# Test lead creation
python test_api.py --lead

# Test quote creation
python test_api.py --quote

# Run all tests
python test_api.py --all
```

You can also specify a custom endpoint and method:

```bash
python test_api.py --endpoint /api/v1/leads --method POST
```

#### 2. Using `run_tests.bat` (Windows)

For Windows users, a batch file is provided for convenience:

```cmd
run_tests.bat
```

Follow the menu prompts to select and run tests.

#### 3. Using `curl_commands.sh` (Linux/Mac)

For Linux/Mac users, a shell script is provided to test the API using `curl`:

```bash
bash curl_commands.sh
```

This script will:

1. Authenticate and retrieve a token.
2. Use the token to create a lead.

#### 4. Debugging Tokens

Use the `debug_token.py` utility to decode and verify JWT tokens:

```bash
python app/utils/debug_token.py <your-jwt-token>
```

#### 5. Diagnosing Environment Issues

Run the `env_diagnosis.py` script to check for missing or misconfigured environment variables:

```bash
python app/utils/env_diagnosis.py
```

#### 6. Validating Environment Configuration

Run the `validate_env.py` script to validate your environment setup:

```bash
python validate_env.py
```

#### 7. Manual Testing with Swagger UI

The API includes Swagger UI documentation that allows interactive testing:

1. Start the application:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. Open a web browser and navigate to: http://localhost:8000

3. You'll see the Swagger UI interface with all available endpoints.

4. To authenticate:

   - Click on the `/api/v1/auth/token` endpoint
   - Click the "Try it out" button
   - Enter the test credentials:
     ```json
     {
     	"username": "test",
     	"password": "test"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` value from the response

5. To test protected endpoints:
   - Click on the endpoint you want to test (e.g., `/api/v1/leads`)
   - Click the "Authorize" button at the top right
   - Enter your token with the format: `Bearer <your-token>`
   - Click "Authorize"
   - Now you can test the protected endpoints

### Understanding Test Logs

When running the application with `LOG_LEVEL=DEBUG`, you'll see detailed logs:

- **Authentication logs**: Show the JWT token creation and validation
- **Request processing logs**: Show incoming requests and their headers
- **Authorization logs**: Show token validation results
- **API call logs**: Show requests to external APIs (Pineapple and Appwrite)

Typical log patterns:
