# Pineapple Lead API

A production-grade API service that integrates with Pineapple's insurance system for lead transfer and quick quotation services.

## Overview

The Pineapple Lead API is a robust middleware service designed to:

1. Forward lead information to Pineapple's insurance system
2. Request vehicle insurance quotes from Pineapple's quotation service
3. Store transaction data in PostgreSQL for record-keeping and analytics
4. Provide a reliable, scalable, and concurrent architecture for high performance

The API is built using Go with Chi router, offering excellent performance characteristics, proper error handling, request validation, and rate limiting to protect both the client and upstream services.

## Features

- **Lead Transfer Service**: Securely transfer customer leads to Pineapple's system
- **Quick Quote Service**: Obtain vehicle insurance quotes with detailed parameters
- **PostgreSQL Integration**: Persist all transaction data for audit and analytics
- **Database Migrations**: Automated schema management for smooth deployments
- **Request Validation**: Comprehensive input validation and error handling
- **Rate Limiting**: Protection against abuse and overload
- **Concurrency**: Efficient handling of multiple requests through goroutines and channels
- **Timeout Handling**: Proper context-based timeouts for all operations
- **Logging**: Detailed operational logging for monitoring and troubleshooting
- **Health Checks**: Endpoint for monitoring system health
- **API Documentation**: Interactive OpenAPI/Swagger documentation

## System Requirements

- Go 1.18 or higher
- PostgreSQL 12 or higher
- Accessible network to Pineapple APIs

## Installation

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/surestrat/pineapple-lead-api.git
   cd pineapple-lead-api
   ```

2. Install dependencies:

   ```bash
   go mod tidy
   ```

3. Configure environment variables in `.env` file:

   ```properties
   # Authentication
   API_BEARER_TOKEN="your_pineapple_bearer_token"

   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_db_password
   DB_NAME=pineapple_leads
   DB_SSLMODE=disable

   # API Endpoints
   LEAD_TRANSFER_ENDPOINT=http://gw-test.pineapple.co.za/users/motor_lead
   QUICK_QUOTE_ENDPOINT=http://gw-test.pineapple.co.za/api/v1/quote/quick-quote

   # Server Configuration
   PORT=9000                  # API service port
   REQUEST_TIMEOUT=30         # Seconds
   MAX_CONCURRENT_CALLS=10    # Maximum concurrent upstream API calls
   ```

4. Create the database:

   ```bash
   createdb -U postgres pineapple_leads
   ```

5. Run the application:
   ```bash
   go run main.go
   ```

### Using Docker

1. Copy the example environment file and configure it:

   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

2. Build and run with Docker Compose:

   ```bash
   docker-compose up -d
   ```

   This will:

   - Build the application image
   - Create a PostgreSQL database container
   - Configure networking between the containers
   - Set up appropriate environment variables
   - Mount volumes for data persistence

3. Monitor the deployment:

   ```bash
   docker-compose logs -f
   ```

4. Access the API at http://localhost:9000

5. Check service health:

   ```bash
   curl http://localhost:9000/health
   ```

6. To stop the services:

   ```bash
   docker-compose down
   ```

7. To stop the services and remove data volumes:

   ```bash
   docker-compose down -v
   ```

#### Docker Deployment in Production

For production environments, consider these additional steps:

1. Use Docker secrets or a secure environment variable manager instead of .env files
2. Set up a reverse proxy (Nginx/Traefik) with SSL termination
3. Configure container resource limits appropriately
4. Set up monitoring and logging solutions (Prometheus/Grafana)
5. Use a container orchestration platform like Kubernetes for high availability

Example production deployment command:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## API Documentation

The API includes comprehensive documentation using OpenAPI/Swagger. When the application is running, you can access:

- Interactive API documentation: http://localhost:9000/swagger/
- OpenAPI specification: http://localhost:9000/docs/swagger.json

The documentation is interactive, allowing you to:

- Explore all available endpoints
- View request/response schemas
- Try endpoints directly from the browser
- See detailed validation requirements
- Download the OpenAPI spec for client code generation

## Database Schema

The API manages two primary tables:

### Lead Transfers

Stores all lead transfer requests and their responses:

| Column         | Type      | Description                       |
| -------------- | --------- | --------------------------------- |
| id             | SERIAL    | Primary key                       |
| source         | TEXT      | Lead source identifier            |
| first_name     | TEXT      | Customer's first name             |
| last_name      | TEXT      | Customer's last name              |
| email          | TEXT      | Customer's email address          |
| id_number      | TEXT      | ID number (optional)              |
| quote_id       | TEXT      | Associated quote ID (optional)    |
| contact_number | TEXT      | Customer's contact number         |
| response_uuid  | TEXT      | UUID returned by Pineapple        |
| redirect_url   | TEXT      | Redirect URL for customer journey |
| created_at     | TIMESTAMP | Record creation timestamp         |

### Quick Quotes

Stores all quick quote requests and their responses:

| Column                | Type      | Description                    |
| --------------------- | --------- | ------------------------------ |
| id                    | SERIAL    | Primary key                    |
| source                | TEXT      | Quote source identifier        |
| external_reference_id | TEXT      | External system reference      |
| vehicle_count         | INTEGER   | Number of vehicles in quote    |
| response_id           | TEXT      | Quote ID returned by Pineapple |
| response_premium      | NUMERIC   | Quoted premium amount          |
| response_excess       | NUMERIC   | Quoted excess amount           |
| created_at            | TIMESTAMP | Record creation timestamp      |

## API Reference

### Authentication

All requests to upstream Pineapple services use bearer token authentication. The token must be set in the `API_BEARER_TOKEN` environment variable.

### Endpoints

#### 1. Lead Transfer API

**Endpoint:** `POST /users/motor_lead`

**Description:** Transfers a customer lead to Pineapple's system

**Request Headers:**

- Content-Type: application/json

**Request Body:**

```json
{
	"source": "SureStrat",
	"first_name": "Peter",
	"last_name": "Smith",
	"email": "PeterSmith007@gmail.com",
	"id_number": "9510025800086",
	"quote_id": "679765d8cdfba62ff342d2ef",
	"contact_number": "0737111119"
}
```

**Response:**

```json
{
	"success": true,
	"data": {
		"uuid": "66e1894aa137e938de5a76c5",
		"redirect_url": "https://test-pineapple-claims.herokuapp.com/car-insurance/get-started?uuid=66e1894aa137e938de5a76c5&ref=serithi"
	}
}
```

#### 2. Quick Quote API

**Endpoint:** `POST /api/v1/quote/quick-quote`

**Description:** Retrieves a quick insurance quote for one or more vehicles

_For complete request/response details, please refer to the Swagger documentation._

#### 3. Health Check

**Endpoint:** `GET /health`

**Description:** Checks if the API is running correctly

**Response:**

```json
{
	"status": "healthy",
	"version": "1.0.0",
	"cpus": 8
}
```

## Development Mode

The API includes a development mode that uses mock responses when you don't have a valid API bearer token. This allows you to:

1. Test the API without needing real Pineapple API credentials
2. Develop and test frontend integrations locally
3. Run the service without connecting to external systems

To activate development mode, set the API_BEARER_TOKEN to "your_bearer_token_here" in your .env file. The system will log a warning indicating that mock responses are being used, and it will generate appropriate mock data for all API calls.

Example mock responses:

### Lead Transfer API Mock Response

```json
{
	"success": true,
	"data": {
		"uuid": "mock-1616598956",
		"redirect_url": "https://test-pineapple-claims.herokuapp.com/car-insurance/get-started?uuid=mock-1616598956&ref=mock&name=Peter"
	}
}
```

### Quick Quote API Mock Response

```json
{
	"success": true,
	"id": "mock-quote-1616598956",
	"data": [
		{
			"premium": 1240.46,
			"excess": 6200
		}
	]
}
```

## Client Code Generation

The OpenAPI specification can be used to generate client libraries in various languages:

### JavaScript Example

Using OpenAPI Generator:

```bash
npx @openapitools/openapi-generator-cli generate -i http://localhost:9000/docs/swagger.json -g javascript -o ./js-client
```

### Python Example

Using OpenAPI Generator:

```bash
npx @openapitools/openapi-generator-cli generate -i http://localhost:9000/docs/swagger.json -g python -o ./python-client
```

## Error Handling

The API returns standardized error responses:

```json
{
	"success": false,
	"error": "Error message details"
}
```

## Concurrency Model

The API employs a sophisticated concurrency model:

1. **Request Processing**: Each incoming request is processed in its own goroutine
2. **Semaphore Control**: A semaphore limits concurrent calls to upstream APIs
3. **Context Timeouts**: All operations have context-based timeouts for resilience
4. **Background Persistence**: Database writes occur in separate goroutines to minimize request latency
5. **Connection Pooling**: Database connections are managed through a pool for efficiency

## Deployment

### Kubernetes Deployment

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pineapple-lead-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pineapple-lead-api
  template:
    metadata:
      labels:
        app: pineapple-lead-api
    spec:
      containers:
        - name: pineapple-lead-api
          image: pineapple-lead-api:latest
          ports:
            - containerPort: 9000
          env:
            - name: API_BEARER_TOKEN
              valueFrom:
                secretKeyRef:
                  name: pineapple-secrets
                  key: api_bearer_token
            - name: DB_HOST
              value: "postgres-service"
            - name: DB_PORT
              value: "5432"
            - name: DB_USER
              value: "postgres"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secrets
                  key: password
            - name: DB_NAME
              value: "pineapple_leads"
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "100m"
              memory: "128Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 9000
            initialDelaySeconds: 30
            periodSeconds: 10
```

## Support

For support inquiries, contact:

- Email: support@surestrat.com
- Issue Tracker: [GitHub Issues](https://github.com/surestrat/pineapple-lead-api/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
