#!/bin/bash
# Helper script for making authenticated API requests

# Base URL
BASE_URL="http://localhost:8000"

# First, get an authentication token
echo "Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}')

# Extract token from response
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')

if [ -z "$TOKEN" ]; then
  echo "Failed to get authentication token. Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Token obtained successfully"

# Example: Create a lead with the token
echo -e "\nCreating a lead..."
curl -X POST \
  "${BASE_URL}/api/v1/leads/" \
  -H "accept: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
  "source": "CURL_TEST",
  "first_name": "John",
  "last_name": "Doe",
  "email": "johndoe@example.com",
  "id_number": "8001015009087",
  "contact_number": "0712345678"
}'

echo -e "\n\nDone"
