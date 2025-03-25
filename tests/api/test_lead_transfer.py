from fastapi.testclient import TestClient
from app.main import app
from app.schemas.lead import LeadCreate, LeadResponse

client = TestClient(app)

def test_create_lead_transfer():
    lead_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "source": "Website"
    }
    response = client.post("/api/lead-transfer/", json=lead_data)
    assert response.status_code == 201
    lead = LeadResponse(**response.json())
    assert lead.name == lead_data["name"]
    assert lead.email == lead_data["email"]

def test_get_lead_transfer():
    response = client.get("/api/lead-transfer/1")
    assert response.status_code == 200
    lead = LeadResponse(**response.json())
    assert lead.id == 1

def test_update_lead_transfer():
    lead_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "0987654321",
        "source": "Referral"
    }
    response = client.put("/api/lead-transfer/1", json=lead_data)
    assert response.status_code == 200
    lead = LeadResponse(**response.json())
    assert lead.name == lead_data["name"]

def test_delete_lead_transfer():
    response = client.delete("/api/lead-transfer/1")
    assert response.status_code == 204
    response = client.get("/api/lead-transfer/1")
    assert response.status_code == 404