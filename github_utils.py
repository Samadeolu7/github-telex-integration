import hmac
import hashlib
import json

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify that the payload signature matches the one generated with the secret."""
    computed_hmac = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={computed_hmac}"
    return hmac.compare_digest(expected_signature, signature)

def extract_username(event_type: str, payload: dict) -> str:
    """Extract the username based on the event type."""
    event_user_mapping = {
        "push": lambda p: p.get("pusher", {}).get("name", "unknown"),
        "pull_request": lambda p: p.get("pull_request", {}).get("user", {}).get("login", "unknown"),
        "issues": lambda p: p.get("issue", {}).get("user", {}).get("login", "unknown"),
        # Add more event types as needed
    }
    return event_user_mapping.get(event_type, lambda p: "unknown")(payload)

def create_telex_payload(event_type: str, payload: dict) -> dict:
    """Create the payload to send to Telex based on the event type."""
    username = extract_username(event_type, payload)
    if event_type == "push":
        commits = payload.get("commits", [])
        commit_messages = "\n".join([f"- {commit.get('message')}" for commit in commits])
        message = f"GitHub Push Event by {username}:\n{commit_messages}"
    
    elif event_type == "issues":
        action = payload.get("action", "unknown")
        issue = payload.get("issue", {})
        username = issue.get("user", {}).get("login", "unknown")
        title = issue.get("title", "No title")
        body = issue.get("body", "")
        html_url = issue.get("html_url", "")
        # Truncate body if it is too long for a concise summary
        if len(body) > 200:
            body = body[:200] + "..."
        message = (
            f"GitHub Issue {action} by {username}:\n"
            f"Title: {title}\n"
            f"URL: {html_url}\n"
            f"Description: {body}"
        )

    else:
        message = f"GitHub Event: {event_type}\nPayload: {json.dumps(payload, indent=2)}"
    
    return {
        "event_name": event_type,
        "message": message,
        "status": "success",
        "username": username
    }
