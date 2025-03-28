"""
Utility to generate a Postman collection for the Pineapple Lead API.
This script creates a Postman collection file that can be imported into Postman.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import uuid

# Import the env_loader to get environment variables
from app.utils.env_loader import get_env, load_env_files

# Make sure environment variables are loaded
load_env_files(verbose=True)


def create_postman_collection():
    """
    Create a Postman collection for the Pineapple Lead API
    """
    # Get environment variables
    api_bearer_token = get_env("API_BEARER_TOKEN", "")
    secret = get_env("SECRET", "")
    
    # Format the bearer token for Pineapple API
    if api_bearer_token and secret and "KEY=" not in api_bearer_token:
        bearer_token = f"KEY={api_bearer_token} SECRET={secret}"
    else:
        bearer_token = api_bearer_token
    
    # Base URLs
    local_url = "http://localhost:8000"
    pineapple_url = get_env("PINEAPPLE_API_BASE_URL", "http://gw.pineapple.co.za")
    
    # Create collection structure
    collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": "Pineapple Lead API Collection",
            "description": "API for managing leads and quotes for insurance products",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            # Authentication
            {
                "name": "Authentication",
                "item": [
                    {
                        "name": "Get JWT Token",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "username": get_env("TEST_USERNAME", "test"),
                                        "password": get_env("TEST_PASSWORD", "test"),
                                    }
                                ),
                            },
                            "url": {
                                "raw": f"{local_url}/api/v1/auth/token",
                                "protocol": "http",
                                "host": ["localhost"],
                                "port": "8000",
                                "path": ["api", "v1", "auth", "token"],
                            },
                            "description": "Get a JWT token for authentication",
                        },
                        "response": [],
                    }
                ],
            },
            # Leads
            {
                "name": "Leads",
                "item": [
                    {
                        "name": "Create Lead",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [{"key": "token", "value": "{{jwt_token}}", "type": "string"}],
                            },
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "source": "POSTMAN_TEST",
                                        "first_name": "Peter",
                                        "last_name": "Smith",
                                        "email": f"test.{int(datetime.now().timestamp())}@example.com",
                                        "id_number": "9510025800086",
                                        "quote_id": "",
                                        "contact_number": "0737111119",
                                    }
                                ),
                            },
                            "url": {
                                "raw": f"{local_url}/api/v1/leads",
                                "protocol": "http",
                                "host": ["localhost"],
                                "port": "8000",
                                "path": ["api", "v1", "leads"],
                            },
                            "description": "Create a new lead",
                        },
                        "response": [],
                    }
                ],
            },
            # Quotes
            {
                "name": "Quotes",
                "item": [
                    {
                        "name": "Create Quote",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [{"key": "token", "value": "{{jwt_token}}", "type": "string"}],
                            },
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "source": "POSTMAN_TEST",
                                        "externalReferenceId": f"TEST-{int(datetime.now().timestamp())}",
                                        "vehicles": [
                                            {
                                                "year": 2019,
                                                "make": "Volkswagen",
                                                "model": "Polo Tsi 1.2 Comfortline",
                                                "mmCode": "00815170",
                                                "modified": "N",
                                                "category": "HB",
                                                "colour": "White",
                                                "engineSize": 1.2,
                                                "financed": "N",
                                                "owner": "Y",
                                                "status": "New",
                                                "partyIsRegularDriver": "Y",
                                                "accessories": "Y",
                                                "accessoriesAmount": 20000,
                                                "retailValue": 200000,
                                                "marketValue": 180000,
                                                "insuredValueType": "Retail",
                                                "useType": "Private",
                                                "overnightParkingSituation": "Garage",
                                                "coverCode": "Comprehensive",
                                                "address": {
                                                    "addressLine": "123 Main Street",
                                                    "postalCode": 2196,
                                                    "suburb": "Sandton",
                                                    "latitude": -26.10757,
                                                    "longitude": 28.0567,
                                                },
                                                "regularDriver": {
                                                    "maritalStatus": "Married",
                                                    "currentlyInsured": True,
                                                    "yearsWithoutClaims": 0,
                                                    "relationToPolicyHolder": "Self",
                                                    "emailAddress": f"test.driver.{int(datetime.now().timestamp())}@example.com",
                                                    "mobileNumber": "0821234567",
                                                    "idNumber": "9404054800086",
                                                    "prvInsLosses": 0,
                                                    "licenseIssueDate": "2018-10-02",
                                                    "dateOfBirth": "1994-04-05",
                                                },
                                            }
                                        ],
                                    }
                                ),
                            },
                            "url": {
                                "raw": f"{local_url}/api/v1/quotes",
                                "protocol": "http",
                                "host": ["localhost"],
                                "port": "8000",
                                "path": ["api", "v1", "quotes"],
                            },
                            "description": "Create a new quote",
                        },
                        "response": [],
                    }
                ],
            },
            # Direct Pineapple API Calls
            {
                "name": "Pineapple API Direct",
                "item": [
                    {
                        "name": "Lead Transfer (Direct)",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [{"key": "token", "value": bearer_token, "type": "string"}],
                            },
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "source": "SureStrat",
                                        "first_name": "Peter",
                                        "last_name": "Smith",
                                        "email": f"peterSmith{int(datetime.now().timestamp())}@pineapple.co.za",
                                        "id_number": "9510025800086",
                                        "quote_id": "",
                                        "contact_number": "0737111119",
                                    }
                                ),
                            },
                            "url": {
                                "raw": f"{pineapple_url}/users/motor_lead",
                                "protocol": "http",
                                "host": pineapple_url.replace("http://", "").split("/"),
                                "path": ["users", "motor_lead"],
                            },
                            "description": "Direct call to Pineapple API to create a lead",
                        },
                        "response": [],
                    },
                    {
                        "name": "Quick Quote (Direct)",
                        "request": {
                            "auth": {
                                "type": "bearer",
                                "bearer": [{"key": "token", "value": bearer_token, "type": "string"}],
                            },
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps(
                                    {
                                        "source": "SureStrat",
                                        "externalReferenceId": f"TEST-{int(datetime.now().timestamp())}",
                                        "vehicles": [
                                            {
                                                "year": 2019,
                                                "make": "Volkswagen",
                                                "model": "Polo Tsi 1.2 Comfortline",
                                                "mmCode": "00815170",
                                                "modified": "N",
                                                "category": "HB",
                                                "colour": "White",
                                                "engineSize": 1.2,
                                                "financed": "N",
                                                "owner": "Y",
                                                "status": "New",
                                                "partyIsRegularDriver": "Y",
                                                "accessories": "Y",
                                                "accessoriesAmount": 20000,
                                                "retailValue": 200000,
                                                "marketValue": 180000,
                                                "insuredValueType": "Retail",
                                                "useType": "Private",
                                                "overnightParkingSituation": "Garage",
                                                "coverCode": "Comprehensive",
                                                "address": {
                                                    "addressLine": "123 Main Street",
                                                    "postalCode": 2196,
                                                    "suburb": "Sandton",
                                                    "latitude": -26.10757,
                                                    "longitude": 28.0567,
                                                },
                                                "regularDriver": {
                                                    "maritalStatus": "Married",
                                                    "currentlyInsured": True,
                                                    "yearsWithoutClaims": 0,
                                                    "relationToPolicyHolder": "Self",
                                                    "emailAddress": f"test.driver.{int(datetime.now().timestamp())}@example.com",
                                                    "mobileNumber": "0821234567",
                                                    "idNumber": "9404054800086",
                                                    "prvInsLosses": 0,
                                                    "licenseIssueDate": "2018-10-02",
                                                    "dateOfBirth": "1994-04-05",
                                                },
                                            }
                                        ],
                                    }
                                ),
                            },
                            "url": {
                                "raw": f"{pineapple_url}/api/v1/quote/quick-quote",
                                "protocol": "http",
                                "host": pineapple_url.replace("http://", "").split("/"),
                                "path": ["api", "v1", "quote", "quick-quote"],
                            },
                            "description": "Direct call to Pineapple API to create a quote",
                        },
                        "response": [],
                    },
                ],
            },
        ],
        "variable": [
            {
                "key": "jwt_token",
                "value": "",
                "type": "string",
                "description": "JWT token from authentication",
            }
        ],
    }

    # Write to file
    output_path = Path(__file__).parent.parent.parent / "postman_collection.json"
    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)

    print(f"Postman collection created at: {output_path}")


if __name__ == "__main__":
    create_postman_collection()
