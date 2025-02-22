# test_main.py
import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from main import app, integration_config

client = TestClient(app)

def generate_signature(payload: bytes, secret: str) -> str:
    computed_hmac = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={computed_hmac}"

def test_push_event():
    payload = {
        "pusher": {"name": "testuser"},
        "commits": [
            {"message": "Initial commit"},
            {"message": "Added README"}
        ]
    }
    payload_bytes = json.dumps(payload).encode()
    signature = generate_signature(payload_bytes, integration_config.github_secret)
    
    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }
    
    response = client.post("/webhook", data=payload_bytes, headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Event processed and forwarded to Telex"
