import hashlib
import hmac
import json
import pytest
from fastapi.testclient import TestClient
from main import app, verify_github_signature, integration_config

client = TestClient(app)

def test_verify_github_signature():
    payload = b'{"test": "data"}'
    secret = "85a22e915f5828b81e100d5ad85e98d9e1990b42"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_github_signature(payload, signature, secret) == True

def test_github_webhook_push_event():
    payload = {
        "pusher": {"name": "testuser"},
        "commits": [{"message": "Initial commit"}]
    }
    payload_str = json.dumps(payload, separators=(',', ':'))
    payload_bytes = payload_str.encode("utf-8")
    signature = "sha256=" + hmac.new(
        integration_config.github_secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push",
        "Content-Type": "application/json"
    }
    
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Event processed and forwarded to Telex"}

def test_github_webhook_invalid_signature():
    payload = {"test": "data"}
    headers = {
        "X-Hub-Signature-256": "invalidsignature",
        "X-GitHub-Event": "push"
    }
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}

def test_github_webhook_missing_signature():
    payload = {"test": "data"}
    headers = {
        "X-GitHub-Event": "push"
    }
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Missing GitHub signature header"}

def test_github_webhook_invalid_json():
    payload = "invalid json"
    headers = {
        "X-Hub-Signature-256": "sha256=" + hmac.new(
            integration_config.github_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest(),
        "X-GitHub-Event": "push",
        "Content-Type": "application/json"
    }
    response = client.post("/webhook", data=payload, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON payload"}

def test_github_webhook_other_event():
    payload = {
        "action": "opened",
        "issue": {"title": "New issue"}
    }
    payload_str = json.dumps(payload, separators=(',', ':'))
    payload_bytes = payload_str.encode("utf-8")
    signature = "sha256=" + hmac.new(
        integration_config.github_secret.encode(), payload_bytes, hashlib.sha256
    ).hexdigest()
    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "issues",
        "Content-Type": "application/json"
    }
    
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Event processed and forwarded to Telex"}