# Developer Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Database Setup](#database-setup)
- [API Implementation](#api-implementation)
- [Testing Guide](#testing-guide)
- [Future Improvements](#future-improvements)

## System Overview

### Architecture Design

The system uses a layered architecture:

1. **API Layer** (`app/api/`)

   - HTTP endpoints using FastAPI
   - Request/response handling
   - Input validation using Pydantic models

2. **Service Layer** (`app/api/*/service.py`)

   - Business logic implementation
   - External API integration (Pineapple)
   - Error handling and logging

3. **Repository Layer** (`app/db/repositories/`)

   - Database operations
   - Async SQLite interaction
   - Type-safe queries using SQLModel

4. **Data Layer**
   - SQLite database
   - Async operations with aiosqlite
   - SQLModel for ORM functionality

## Database Setup

### SQLite Configuration

The project uses SQLite with async support through aiosqlite:

```python
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

Benefits of SQLite in this project:

- Zero-configuration database
- File-based storage
- Built-in async support
- Perfect for development and small to medium deployments

### Database Initialization

The database is initialized using `init_dev_db.py`:

```python
async def init_db():
    engine = create_async_engine(
        "sqlite+aiosqlite:///./app.db",
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Working with Models

Example Lead model usage:

```python
# Create a lead
lead = Lead(
    name="John Doe",
    email="john@example.com",
    status=LeadStatusEnum.NEW
)

# Save to database
db.add(lead)
await db.commit()
await db.refresh(lead)
```

## API Implementation

### Lead Management

The Lead API supports:

- Create new leads
- Update lead information
- Transfer leads between owners
- List leads with filtering
- Delete leads

Example lead creation:

```bash
curl -X POST "http://localhost:8000/api/v1/leads/" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "John Doe",
           "email": "john@example.com",
           "phone": "+27123456789"
         }'
```

### Quote Management

The Quote API provides:

- Quote generation
- Price calculations
- Integration with Pineapple's quote system
- Quote history tracking

Example quote creation:

```bash
curl -X POST "http://localhost:8000/api/v1/quotes/" \
     -H "Content-Type: application/json" \
     -d '{
           "lead_id": 1,
           "amount": 1000.00,
           "description": "Vehicle insurance quote",
           "currency": "ZAR"
         }'
```

## Testing Guide

### Test Structure

```
tests/
├── api/               # API endpoint tests
│   ├── test_lead_transfer.py
│   └── test_quick_quote.py
├── db/                # Repository tests
└── conftest.py       # Test fixtures
```

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/api/test_lead_transfer.py

# With coverage
pytest --cov=app tests/
```

### Test Database

Tests use an in-memory SQLite database:

```python
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
```

## Future Improvements

### Short Term

1. **Database Enhancements**

   - Add database migrations support
   - Implement connection pooling
   - Add database backup functionality

2. **API Features**

   - Bulk operations support
   - Rate limiting
   - Response caching
   - Webhook notifications

3. **Security**
   - JWT authentication
   - Role-based access control
   - API key management
   - Request validation middleware

### Medium Term

1. **Performance**

   - Query optimization
   - Result caching
   - Async batch processing
   - Background task queue

2. **Integration**
   - Additional insurance providers
   - CRM system integration
   - Email notification system
   - SMS notifications

### Long Term

1. **Architecture**

   - Consider migration to PostgreSQL for scaling
   - Microservices architecture
   - GraphQL API support
   - Event-driven architecture

2. **Features**

   - Machine learning for quote optimization
   - Real-time analytics
   - Advanced reporting
   - Mobile app API support

3. **Infrastructure**
   - Kubernetes deployment
   - Multi-region support
   - Automated scaling
   - Disaster recovery

## Best Practices

1. **Code Style**

   ```python
   # Use type hints
   async def get_lead(self, lead_id: int) -> Optional[Lead]:
       ...

   # Use async/await consistently
   async with engine.begin() as conn:
       ...

   # Proper error handling
   try:
       result = await operation()
   except SQLAlchemyError as e:
       logger.error(f"Database error: {e}")
       raise
   ```

2. **Error Handling**

   - Use custom exceptions
   - Proper error logging
   - Consistent error responses

3. **Testing**
   - Write tests first
   - Use fixtures
   - Mock external services

## Monitoring and Logging

1. **Health Checks**

   - Database connectivity
   - External service status
   - System resources

2. **Logging**
   - Request/response logging
   - Error tracking
   - Performance metrics

## Deployment

### Local Development

```bash
uvicorn app.main:app --reload --port 8000
```

### Production

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker

```bash
docker-compose up --build
```

## Support

For technical issues:

1. Check logs: `logs/app.log`
2. Run health check: `GET /health`
3. Test database: `python test_db_connection.py`
4. Contact development team

Remember to keep this documentation updated as the project evolves.
