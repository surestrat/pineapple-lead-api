# FastAPI Lead and Quote API

A comprehensive API system for managing leads and insurance quotes, with integration to Pineapple's insurance services. Built with FastAPI and SQLModel, using SQLite for data storage.

## Key Features

- **Lead Management**

  - Create, read, update, and delete leads
  - Lead transfer between owners
  - Integration with Pineapple's lead system
  - Advanced filtering and pagination

- **Quote Management**

  - Generate quotes for leads
  - Integration with Pineapple's quick quote system
  - Support for multiple currencies
  - Quote validation and expiry tracking

- **Technical Features**
  - Async SQLite database operations
  - Comprehensive API documentation
  - Health monitoring endpoints
  - Robust error handling
  - Type safety with Pydantic v2
  - Docker support

## Quick Start

### Prerequisites

- Python 3.9+
- Poetry (recommended) or pip
- SQLite3
- Docker (optional)

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd fastapi-lead-quote-api
   ```

2. Set up environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   # Using Poetry (recommended)
   poetry install

   # Using pip
   pip install -r requirements.txt
   ```

4. Configure environment:

   ```bash
   cp .env.example .env
   ```

   Default SQLite configuration is already set in .env:

   ```
   DATABASE_URL=sqlite+aiosqlite:///./app.db
   ```

5. Initialize database:

   ```bash
   python init_dev_db.py
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- Detailed developer documentation: [DEVELOPER.md](docs/DEVELOPER.md)

## Testing

Run the test suite:

```bash
pytest
```

## Project Structure

```
fastapi-lead-quote-api/
├── app/
│   ├── api/              # API routes and handlers
│   ├── core/            # Core functionality and config
│   ├── db/              # Database models and repositories
│   ├── models/          # SQLModel definitions
│   └── schemas/         # Pydantic schemas
├── tests/              # Test suite
└── docs/              # Documentation
```

## Configuration

Key environment variables:

```bash
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
PORT=8000
PINEAPPLE_API_TOKEN=your_pineapple_api_token_here
```

For detailed configuration and usage, see [DEVELOPER.md](docs/DEVELOPER.md).

## License

MIT License
