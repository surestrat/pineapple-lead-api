# Pineapple Integration API

This project provides a FastAPI backend to integrate with Pineapple's Quick Quote and Lead Transfer APIs. It includes:

- Endpoints to receive quote requests and lead transfer requests.
- Interaction with Pineapple's external APIs.
- Storage of requests and responses in a PostgreSQL database (compatible with Supabase).
- JWT-based authentication for securing endpoints.
- Database migrations using Alembic.
- Configuration management using Pydantic Settings and `.env` files.

## Project Structure

- **app/** - Main application code
  - **api/** - API endpoints and route definitions
  - **core/** - Core application functionality
  - **crud/** - Database operations
  - **db/** - Database connection
  - **models/** - SQLAlchemy database models
  - **schemas/** - Pydantic data schemas
  - **services/** - Business logic and external service integrations
- **migrations/** - Alembic database migrations
- **.env** - Environment variables (not in git)

## Database Tables

The application uses the following tables in Supabase:

1. **users** - User authentication data (6 columns)
2. **quotes** - Insurance quote records (7 columns)
3. **leads** - Lead transfer records (5 columns)
4. **vehicles** - Vehicle information (22 columns)
5. **addresses** - Address information for vehicles (8 columns)
6. **drivers** - Driver information (13 columns)

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**

    - Copy `.env.example` to `.env`.
    - Edit `.env` and provide your actual `DATABASE_URL`, `PINEAPPLE_API_BEARER_TOKEN`, and generate a strong `JWT_SECRET_KEY`.

5.  **Set up the database:**
    - Ensure your PostgreSQL database (e.g., from Supabase) is running and accessible.
    - Run database migrations:
      ```bash
      alembic upgrade head
      ```

## Running the Application

```bash
uvicorn app.main:app --reload
```

## Development Workflow

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
   alembic downgrade -1
   ```
