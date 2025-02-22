import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class IntegrationConfig(BaseModel):
    integration_id: str
    name: str
    description: str
    integration_type: str
    telex_webhook_url: str
    github_secret: str
    enabled: bool

integration_config = IntegrationConfig(
    integration_id="github-telex-integration",
    name="GitHub to Telex Integration",
    description="Sends GitHub events to a Telex channel",
    integration_type="Output",
    telex_webhook_url=os.getenv("TELEX_WEBHOOK_URL"),
    github_secret=os.getenv("GITHUB_SECRET"),
    enabled=True
)
