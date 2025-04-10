# Pineapple Integration API

This project provides a FastAPI backend to integrate with Pineapple's Quick Quote and Lead Transfer APIs. It includes:

- Endpoints to receive quote requests and lead transfer requests.
- Interaction with Pineapple's external APIs.
- Storage of requests and responses in a PostgreSQL database (compatible with Supabase).
- JWT-based authentication via Supabase Auth.
- Database migrations using Alembic.
- Configuration management using Pydantic Settings and `.env` files.
- Rate limiting for API endpoints.
- Comprehensive logging with Rich handler.

## Table of Contents

- [Project Structure](#project-structure)
- [Database Tables](#database-tables)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Consuming the API](#consuming-the-api)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Potential Improvements](#potential-improvements)
- [Troubleshooting](#troubleshooting)

## Project Structure

- **app/** - Main application code
  - **api/** - API endpoints and route definitions
    - **v1/** - Version 1 of the API
      - **endpoints/** - API endpoint modules
    - **routes/** - Alternative API routes organization
    - **models/** - Pydantic models for API requests/responses
    - **deps.py** - Dependency injection functions
  - **core/** - Core application functionality
    - **config.py** - Settings and configuration
    - **logging_config.py** - Logging configuration
    - **rate_limiter.py** - Rate limiting configuration
  - **crud/** - Database operations
    - **crud_quote.py** - Quote record operations
    - **crud_lead.py** - Lead record operations
  - **db/** - Database connection
    - **session.py** - Supabase client setup
  - **models/** - SQLAlchemy database models
    - **database.py** - Database connection setup
    - **tables.py** - SQLAlchemy ORM models
    - **pineapple.py** - Pineapple API models
  - **schemas/** - Pydantic data schemas
    - **user.py** - User authentication schemas
    - **quote.py** - Quote request/response schemas
    - **lead.py** - Lead transfer schemas
    - **token.py** - Authentication token schemas
  - **services/** - Business logic and external service integrations
    - **pineapple_api.py** - Pineapple API integration
  - **main.py** - FastAPI application entry point
- **migrations/** - Alembic database migrations
  - **versions/** - Migration version files
  - **env.py** - Alembic environment configuration
- **.env** - Environment variables (not in git)
- **.env.example** - Example environment variables file

## Database Tables

The application uses the following tables in a PostgreSQL database:

1. **users** - User authentication data

   - `id` (UUID, PK) - User identifier
   - `first_name` (String) - User's first name
   - `last_name` (String) - User's last name
   - `email` (String) - User's email address
   - `id_number` (String) - User's ID number
   - `contact_number` (String) - User's contact number

2. **quotes** - Insurance quote records

   - `id` (UUID, PK) - Quote identifier
   - `user_id` (UUID, FK) - Reference to user
   - `external_reference_id` (String) - External reference ID
   - `source` (String) - Source of the quote
   - `quote_id` (String) - External quote ID
   - `premium` (Numeric) - Premium amount
   - `excess` (Numeric) - Excess amount

3. **leads** - Lead transfer records

   - `id` (UUID, PK) - Lead identifier
   - `user_id` (UUID, FK) - Reference to user
   - `source` (String) - Source of the lead
   - `quote_id` (UUID, FK) - Reference to quote
   - `created_at` (Timestamp) - Creation timestamp

4. **vehicles** - Vehicle information

   - `id` (UUID, PK) - Vehicle identifier
   - `user_id` (UUID, FK) - Reference to user
   - `year` (Integer) - Vehicle year
   - `make` (String) - Vehicle make
   - `model` (String) - Vehicle model
   - Plus 18 other fields capturing vehicle details

5. **addresses** - Address information for vehicles

   - `id` (UUID, PK) - Address identifier
   - `user_id` (UUID, FK) - Reference to user
   - `vehicle_id` (UUID, FK) - Reference to vehicle
   - `address_line` (String) - Street address
   - `postal_code` (Integer) - Postal code
   - `suburb` (String) - Suburb name
   - `latitude` (Numeric) - Latitude coordinate
   - `longitude` (Numeric) - Longitude coordinate

6. **drivers** - Driver information
   - `id` (UUID, PK) - Driver identifier
   - `user_id` (UUID, FK) - Reference to user
   - `vehicle_id` (UUID, FK) - Reference to vehicle
   - Plus 10 other driver-related fields

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL database (can use Supabase)
- Pineapple API credentials

### Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd pineapple-lead-api
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   - Copy `.env.example` to `.env`
   - Edit `.env` with your actual configuration:

   ```bash
   cp .env.example .env
   # Edit .env with your favorite text editor
   ```

   Essential environment variables:

   - `DATABASE_URL`: PostgreSQL connection string
   - `SUPABASE_URL`: Supabase project URL
   - `SUPABASE_KEY`: Supabase anon or service key
   - `PINEAPPLE_API_URL`: Pineapple API base URL
   - `PINEAPPLE_API_BEARER_TOKEN`: Pineapple API authentication token (format: `KEY=<api_key> SECRET=<api_secret>`)

5. **Set up the database:**

   ```bash
   # Run database migrations to create all tables
   alembic upgrade head
   ```

6. **Run the application:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

   Swagger documentation will be at `http://localhost:8000/docs`.

## API Endpoints

### Authentication Endpoints

- **POST /api/v1/auth/login**

  - Description: Authenticate to get access token
  - Request: Username (email) and password
  - Response: JWT token for API access
  - Rate limit: 10 requests per minute

- **POST /api/v1/auth/test-token**
  - Description: Test if token is valid
  - Request: Bearer token in header
  - Response: User information

### Quote Endpoints

- **POST /api/v1/quotes/quick**

  - Description: Get insurance premium quote
  - Request: Vehicle and driver information
  - Response: Premium and excess amounts
  - Authentication: Required
  - Rate limit: 30 requests per minute

- **POST /api/v1/quotes/quick-quote** (Legacy endpoint)
  - Description: Alternative endpoint for quotes
  - Request: Similar to /quotes/quick
  - Response: Premium information
  - Authentication: Required

### Lead Endpoints

- **POST /api/v1/leads/transfer**
  - Description: Transfer lead to Pineapple
  - Request: Lead information with quote ID
  - Response: Success status and redirect URL
  - Authentication: Required

### Health Check

- **GET /api/v1/health**

  - Description: API health check
  - Response: Status and version
  - Authentication: Not required

- **GET /**
  - Description: Root level health check
  - Response: Welcome message and status
  - Authentication: Not required

## Consuming the API

### Authentication Flow

1. **Login to get a token:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=userpassword"
   ```

   Response:

   ```json
   {
   	"access_token": "eyJ0eXA...",
   	"token_type": "bearer",
   	"refresh_token": "eyJ0eXA...",
   	"expires_in": 3600
   }
   ```

2. **Use the token for authenticated requests:**

   ```bash
   curl -X GET "http://localhost:8000/api/v1/auth/test-token" \
     -H "Authorization: Bearer eyJ0eXA..."
   ```

### Request Flow (Typical Use Case)

1. **Send a quote request:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/quotes/quick" \
     -H "Authorization: Bearer eyJ0eXA..." \
     -H "Content-Type: application/json" \
     -d '{
       "vehicles": [
         {
           "year": 2020,
           "make": "Toyota",
           "model": "Corolla",
           "modified": "N",
           "category": "SD",
           "colour": "White",
           "financed": "Y",
           "owner": "Y",
           "status": "SecondHand",
           "partyIsRegularDriver": "Y",
           "accessories": "N",
           "retailValue": 250000,
           "insuredValueType": "Retail",
           "useType": "Private",
           "overnightParkingSituation": "Garage",
           "coverCode": "Comprehensive",
           "address": {
             "addressLine": "123 Main Street",
             "postalCode": 2000,
             "suburb": "Sandton"
           },
           "regularDriver": {
             "maritalStatus": "Single",
             "currentlyInsured": true,
             "yearsWithoutClaims": 5,
             "relationToPolicyHolder": "Self",
             "emailAddress": "driver@example.com",
             "mobileNumber": "0712345678"
           }
         }
       ]
     }'
   ```

   Response:

   ```json
   {
   	"success": true,
   	"quote_id": "quote_12345",
   	"quote_data": [
   		{
   			"premium": 850.75,
   			"excess": 5000.0
   		}
   	],
   	"local_quote_reference_id": "b0e7b-4c5d-8e6f-7g8h9i",
   	"message": "Quote retrieved successfully."
   }
   ```

2. **Transfer a lead using the quote ID:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/leads/transfer" \
     -H "Authorization: Bearer eyJ0eXA..." \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Smith",
       "email": "john.smith@example.com",
       "contact_number": "0712345678",
       "quote_id": "quote_12345"
     }'
   ```

   Response:

   ```json
   {
   	"success": true,
   	"data": {
   		"uuid": "lead_67890",
   		"redirect_url": "https://pineapple.co.za/quotes/lead_67890"
   	}
   }
   ```

## Development Workflow

### Working with Migrations

1. **Create a new migration:**

   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations:**

   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations:**
   ```bash
   alembic downgrade -1  # Rollback one migration
   alembic downgrade base  # Rollback all migrations
   ```

### Running Tests

_Note: Tests are yet to be implemented._

```bash
pytest
```

## Deployment

### Deploying with Docker

1. **Build the Docker image:**

   ```bash
   docker build -t pineapple-lead-api .
   ```

2. **Run the container:**

   ```bash
   docker run -d -p 8000:8000 --env-file .env pineapple-lead-api
   ```

### Deploying on a VPS or Cloud Platform

1. Clone the repository
2. Set up environment variables
3. Install dependencies
4. Set up a production WSGI server (like Gunicorn)
5. Configure a reverse proxy (like Nginx)

Example Gunicorn command:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Docker Deployment

This project includes Docker configuration for easy deployment.

#### Prerequisites

- Docker and Docker Compose installed on your system
- Pineapple API credentials

#### Quick Start

1. **Build and start the containers:**

   ```bash
   docker-compose up -d
   ```

   This will start both the API and PostgreSQL database.

2. **Run database migrations:**

   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **Check the logs:**

   ```bash
   docker-compose logs -f api
   ```

4. **Access the API:**

   The API will be available at http://localhost:8000

   Swagger documentation: http://localhost:8000/docs

#### Configuration

All environment variables can be set in a `.env` file or passed directly to docker-compose:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
PINEAPPLE_API_URL=http://gw-test.pineapple.co.za
PINEAPPLE_API_BEARER_TOKEN="KEY=<api_key> SECRET=<api_secret>"
PINEAPPLE_SOURCE_NAME=SureStrat
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"
```

#### Production Deployment

For production deployment, additional considerations:

1. **Use volumes for persistent data:**

   - Database data is already configured as a persistent volume
   - Consider volume for log files if needed

2. **Set secure passwords:**

   - Change the PostgreSQL password in docker-compose.yml
   - Use Docker secrets for sensitive information

3. **Configure TLS:**

   - Use a reverse proxy like Nginx or Traefik for TLS termination
   - Set up proper certificates

4. **Container orchestration:**
   - For high-availability, consider Kubernetes or Docker Swarm

## Potential Improvements

### API Features

1. **Enhanced Quote Management**

   - Implement quote comparison functionality
   - Add quote versioning for tracking changes

2. **User Management**

   - Add user registration directly through the API
   - Implement profile management endpoints

3. **Advanced Authentication**

   - Add multi-factor authentication
   - Implement token refresh functionality
   - Add social login options

4. **Data Processing**
   - Add analytics endpoints for quote/lead conversion rates
   - Implement caching for frequent quote requests

### Technical Improvements

1. **Testing**

   - Add unit tests for core functionality
   - Implement integration tests for API endpoints
   - Add performance testing for high-traffic scenarios

2. **Infrastructure**

   - Implement containerization with Docker Compose
   - Add CI/CD pipeline configuration
   - Optimize database query performance
   - Implement Kubernetes deployment

3. **Security**

   - Add rate limiting based on user ID
   - Implement request validation middleware
   - Add audit logging for sensitive operations
   - Implement CORS configuration management

4. **Documentation**

   - Generate API documentation with examples
   - Add SDK for common programming languages

5. **Monitoring**
   - Add Prometheus metrics
   - Implement health check endpoints
   - Set up alerting for critical issues

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

   - Check your `DATABASE_URL` environment variable
   - Ensure PostgreSQL server is running
   - Check network connectivity to database server

2. **Authentication Issues**

   - Verify Supabase URL and API key
   - Check token expiration
   - Ensure correct user credentials

3. **Pineapple API Integration Problems**
   - Confirm Pineapple API credentials are correct
   - Check API endpoints are accessible
   - Verify request format matches API specifications

### Logging

The application uses Rich for enhanced console logging. Set the `LOG_LEVEL` environment variable to control verbosity:

- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Minor issues that don't affect functionality
- `ERROR`: Errors that prevent features from working
- `CRITICAL`: Critical errors that prevent application startup

Log files are stored in the application's root directory by default.

### Getting Help

For support or feature requests, please:

- Open an issue on the repository
- Contact the development team
- Check the Pineapple API documentation for request formatting
