# main.py
import hmac
import hashlib
import json
from fastapi import FastAPI, Request, Header, HTTPException
import httpx
from pydantic import BaseModel

app = FastAPI(title="GitHub to Telex Integration")

# Integration configuration – typically loaded from integration.json or environment variables
TELEX_WEBHOOK_URL = "https://telex.im/webhook/your-channel"  # Replace with your Telex channel webhook
GITHUB_SECRET = "your_github_secret"  # Replace with your GitHub webhook secret

class IntegrationConfig(BaseModel):
    integration_id: str
    name: str
    description: str
    integration_type: str
    telex_webhook_url: str
    github_secret: str
    enabled: bool

# For this example, we hard-code the configuration.
integration_config = IntegrationConfig(
    integration_id="github-telex-integration",
    name="GitHub to Telex Integration",
    description="Sends GitHub events to a Telex channel",
    integration_type="Output",
    telex_webhook_url=TELEX_WEBHOOK_URL,
    github_secret=GITHUB_SECRET,
    enabled=True
)

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify that the payload signature matches the one generated with the secret."""
    computed_hmac = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={computed_hmac}"
    return hmac.compare_digest(expected_signature, signature)

@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header("unknown")
):
    # Retrieve and verify the GitHub signature header
    body = await request.body()
    if not x_hub_signature_256:
        raise HTTPException(status_code=400, detail="Missing GitHub signature header")
    if not verify_github_signature(body, x_hub_signature_256, integration_config.github_secret):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse the JSON payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Process the payload based on the event type (e.g., push event)
    message = ""
    if x_github_event == "push":
        pusher = payload.get("pusher", {}).get("name", "someone")
        commits = payload.get("commits", [])
        commit_messages = "\n".join([f"- {commit.get('message')}" for commit in commits])
        message = f"GitHub Push Event by {pusher}:\n{commit_messages}"
    else:
        # For other event types, include a generic message.
        message = f"GitHub Event: {x_github_event}\nPayload: {json.dumps(payload, indent=2)}"
    
    # Send the summarized message to Telex via its webhook URL
    async with httpx.AsyncClient() as client:
        telex_response = await client.post(
            integration_config.telex_webhook_url,
            json={"text": message}
        )
        if telex_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to send message to Telex")
    
    return {"detail": "Event processed and forwarded to Telex"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
