# Testing Guide

This document provides detailed information on how to test the Pineapple Lead API.

## Testing Tools

The project includes several testing utilities:

1. **test_api.py**: Command-line tool for testing API endpoints
2. **run_tests.bat**: Menu-driven test runner for Windows
3. **curl_commands.sh**: Shell script for testing with curl on Linux/Mac
4. **debug_token.py**: Tool for decoding and validating JWT tokens
5. **env_diagnosis.py**: Tool for checking environment configuration
6. **validate_env.py**: Tool for validating the environment setup
7. **Swagger UI**: Interactive API documentation and testing interface

## Authentication Testing

All protected endpoints require authentication. You must first obtain a JWT token:

### Get Authentication Token

#### Using the API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

Expected response:

```json
{
	"access_token": "eyJhbGciOiJIUzI1...",
	"token_type": "bearer"
}
```

#### Using Swagger UI:

1. Go to http://localhost:8000
2. Expand the `/api/v1/auth/token` endpoint
3. Click "Try it out"
4. Enter credentials and execute
5. Copy the token

### Using the Token

To use the token with protected endpoints, include it in the Authorization header:

```bash
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Testing Endpoints

### 1. Lead Creation

#### Test Data:

```json
{
	"source": "TEST",
	"first_name": "John",
	"last_name": "Doe",
	"email": "johndoe@example.com",
	"id_number": "8001015009087",
	"contact_number": "0712345678"
}
```

#### Using test_api.py:

```bash
python test_api.py --lead
```

#### Using curl:

```bash
curl -X POST http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "TEST",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@example.com",
    "id_number": "8001015009087",
    "contact_number": "0712345678"
  }'
```

### 2. Quick Quote Creation

#### Test Data:

See the detailed example in `test_api.py` in the `get_quote_test_data()` function.

#### Using test_api.py:

```bash
python test_api.py --quote
```

## Understanding Test Logs

When running with `LOG_LEVEL=DEBUG`, you'll see detailed logs of the request processing:

1. **Authentication Flow**:

   ```
   DEBUG: ==== LOGIN REQUEST ====
   DEBUG: Login request for user: test
   DEBUG: ==== AUTHENTICATION ATTEMPT ====
   INFO: Authentication successful for user: test
   DEBUG: Creating access token...
   DEBUG: Token created successfully.
   ```

2. **Request Processing**:

   ```
   DEBUG: Processing request to path: /api/v1/leads/
   DEBUG: Received lead creation request: {...}
   DEBUG: Authorization header: Bearer eyJhbGciOiJ...
   DEBUG: JWT token validated: {'sub': 'test', 'exp': ...}
   ```

3. **API Call to Pineapple**:
   ```
   DEBUG: Sending lead to Pineapple API: {...}
   DEBUG: Using authorization token format: Bearer KEY=xxx... (truncated)
   DEBUG: Pineapple API response: {...}
   ```

## Common Error Patterns

### 1. Authentication Failures
