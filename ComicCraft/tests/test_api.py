import os
os.environ["AI_MODE"] = "demo"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_json_generation():
    payload = {
        "story_prompt": "A brave fox explores an enchanted forest.",
        "character_name": "Lumi",
        "setting": "enchanted forest",
        "tone": "dramatic",
        "art_style": "comic book",
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["panels"]) == 5
    assert data["pdf_url"].endswith(".pdf")


def test_image_endpoint():
    response = client.get("/test-image?prompt=happy%20fox")
    assert response.status_code == 200
    assert response.json()["success"] is True
