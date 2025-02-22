# GitHub to Telex Integration

This integration receives GitHub webhook events, processes them, and sends a summarized message to a Telex channel via its webhook. It is built using FastAPI and is designed as an **Output** integration according to the Telex integration documentation.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)


## Features

- **Modular Codebase:** Organized into separate modules for configuration, GitHub utilities, and Telex utilities.
- **Signature Verification:** Verifies GitHub webhook signatures using HMAC SHA256.
- **Dynamic Event Handling:** Extracts usernames and creates Telex payloads for multiple GitHub event types (e.g., push, pull_request, issues).
- **Asynchronous Processing:** Uses FastAPI's background tasks to forward messages to Telex without delaying webhook responses.
- **Robust Logging:** Provides informative logging for debugging and error tracking.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- httpx
- pydantic
- python-dotenv
- pytest (for testing)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/telex_integrations/github-telex-integration.git
   cd github-telex-integration
```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
```

3. **Install the Required Packages:**

   ```bash
   pip install -r requirements.txt
```

## Configuration

1. **Create a `.env` File:**

   ```bash
   touch .env
```

2. **Add the Required Environment Variables:**

   ```env
   GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
   TELEX_WEBHOOK_URL=your_telex_webhook_url
   ```

## Running the Application

1. **Run the Application:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```


## Testing

1. **Run the Tests:**

   ```bash
   pytest test.py
    ```

## Deployment

Deploy the integration to your chosen hosting provider (e.g., Render, Heroku, AWS). Ensure your deployed URL is publicly accessible. Once deployed, update your GitHub webhook configuration to point to the deployed URL (e.g., https://your-deployed-app.com/webhook).

Screenshots
Include screenshots that demonstrate the following:

A git push event received by the integration.

image showing commit message and author[commit.png]

A message sent to the Telex channel for the git push event.

image showing message sent to telex channel[telex.png]