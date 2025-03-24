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
   # Environment (development or production)
   ENVIRONMENT=development

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

## Deployment with Coolify and Nixpacks

This project is designed to be deployed using [Coolify](https://coolify.io/) with Nixpacks for building the application.

### Preparing for Deployment

1. Make sure your code is pushed to a Git repository accessible by your Coolify instance.

2. In Coolify, create a new service and select your repository.

3. Choose Nixpacks as the build method.

4. Configure the following environment variables in Coolify:

   ```
   ENVIRONMENT=production
   API_BEARER_TOKEN=your_actual_production_token
   DB_HOST=your_production_db_host
   DB_PORT=5432
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=pineapple_leads
   DB_SSLMODE=prefer
   PORT=9000
   REQUEST_TIMEOUT=30
   MAX_CONCURRENT_CALLS=10
   LEAD_TRANSFER_ENDPOINT=https://gw.pineapple.co.za/users/motor_lead
   QUICK_QUOTE_ENDPOINT=https://gw.pineapple.co.za/api/v1/quote/quick-quote
   ```

5. Set the port configuration to match the `PORT` environment variable.

6. Configure a health check endpoint at `/health`.

7. Deploy the application using Coolify's deployment tools.

### Additional Deployment Configurations

For production deployments, consider setting up:

1. **Database Connection**: Link to a production-grade PostgreSQL database
2. **Secrets Management**: Secure handling of the API bearer token and database credentials
3. **HTTPS**: Enable SSL for secure communication
4. **Scaling**: Configure appropriate resource allocation based on expected load
5. **Monitoring**: Set up logging and monitoring integrations

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

The API includes a special mode for Swagger documentation testing only. By setting the `API_BEARER_TOKEN` to `swagger_documentation_token`, mock responses will be generated automatically when accessing API endpoints through the Swagger UI. This allows for testing and exploring the API without making actual calls to the Pineapple services.

This feature should only be used for documentation and development purposes and never in production environments.

Example mock responses when using Swagger UI:

### Lead Transfer API Mock Response

```json
{
	"success": true,
	"data": {
		"uuid": "swagger-doc-uuid-1616598956",
		"redirect_url": "https://test-pineapple-claims.herokuapp.com/car-insurance/get-started?uuid=swagger-doc-uuid-1616598956&ref=swagger-doc&name=Peter"
	}
}
```

### Quick Quote API Mock Response

```json
{
	"success": true,
	"id": "swagger-doc-quote-1616598956",
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
