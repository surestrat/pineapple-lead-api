from fastapi.testclient import TestClient
from app.main import app
from app.schemas.quote import QuoteCreate, QuoteResponse

client = TestClient(app)

def test_create_quote():
    quote_data = {
        "description": "Test Quote",
        "amount": 100.0,
        "currency": "USD"
    }
    response = client.post("/quick-quote/", json=quote_data)
    assert response.status_code == 201
    assert response.json() == QuoteResponse(**quote_data).dict()

def test_get_quote():
    response = client.get("/quick-quote/1")
    assert response.status_code == 200
    assert "description" in response.json()
    assert "amount" in response.json()
    assert "currency" in response.json()

def test_get_nonexistent_quote():
    response = client.get("/quick-quote/999")
    assert response.status_code == 404

def test_update_quote():
    update_data = {
        "description": "Updated Quote",
        "amount": 150.0,
        "currency": "USD"
    }
    response = client.put("/quick-quote/1", json=update_data)
    assert response.status_code == 200
    assert response.json() == QuoteResponse(**update_data).dict()

def test_delete_quote():
    response = client.delete("/quick-quote/1")
    assert response.status_code == 204
    response = client.get("/quick-quote/1")
    assert response.status_code == 404