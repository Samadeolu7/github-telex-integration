import logging
import httpx
from config import integration_config

async def send_to_telex(payload: dict):
    """Send the payload to Telex asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            integration_config.telex_webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code not in [200, 202]:
            logging.error(f"Failed to send message to Telex: {response.text}")
        else:
            logging.info("Message sent to Telex successfully")