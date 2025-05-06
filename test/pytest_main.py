import pytest
from httpx import AsyncClient
from main import app 
import os

pytestmark = pytest.mark.asyncio
BASE_URL = " http://0.0.0.0:8000" 

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client

# --- Test Cases ---

async def test_read_root(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Social Media Reply Generator API!"}

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code in [200, 503] 
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "llm" in data

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY") or not os.getenv("MONGODB_URI"),
                    reason="Requires GOOGLE_API_KEY and MONGODB_URI environment variables")
async def test_create_reply_success(async_client: AsyncClient):
    post_data = {
        "platform": "Twitter",
        "post_text": "Testing the new API endpoint! #testing"
    }
    response = await async_client.post("/reply", json=post_data)

    assert response.status_code == 200

    data = response.json()
    assert "platform" in data
    assert "post_text" in data
    assert "generated_reply" in data
    assert data["platform"] == post_data["platform"]
    assert data["post_text"] == post_data["post_text"]
    assert isinstance(data["generated_reply"], str)
    assert len(data["generated_reply"]) > 0 

async def test_create_reply_missing_field(async_client: AsyncClient):
    """Test the /reply endpoint with missing required fields."""
    post_data_missing = {
        "platform": "Twitter"
    }
    response = await async_client.post("/reply", json=post_data_missing)
    assert response.status_code == 422 

async def test_create_reply_invalid_data_type(async_client: AsyncClient):
    """Test the /reply endpoint with invalid data types."""
    post_data_invalid = {
        "platform": 123, 
        "post_text": "Some text"
    }
    response = await async_client.post("/reply", json=post_data_invalid)
    assert response.status_code == 422 