# Build stage
FROM golang:1.18-alpine AS builder

# Set working directory
WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy go.mod and go.sum files
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o pineapple-lead-api .

# Runtime stage
FROM alpine:3.14

WORKDIR /app

# Install dependencies required for runtime
RUN apk add --no-cache ca-certificates tzdata

# Copy the binary from builder
COPY --from=builder /app/pineapple-lead-api .

# Copy necessary files
COPY --from=builder /app/docs ./docs
COPY --from=builder /app/swagger ./swagger
COPY --from=builder /app/migrations ./migrations
COPY --from=builder /app/.env.example ./.env.example

# Create a non-root user
RUN adduser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the application port
EXPOSE 9000

# Command to run the application
CMD ["./pineapple-lead-api"]
