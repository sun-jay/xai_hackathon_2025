# Interview Tools Backend

Backend service for interview tools including Excalidraw diagram analysis and Retell webhook handling.

> **Note:** This backend has been merged into `phone_screen_agent`. Use `phone_screen_agent` instead for all functionality.

## Features

- **Excalidraw Diagram Analysis** - `/check_diagram` endpoint for SPOF detection
- **Retell Webhooks** - `/retell_call_ended` and `/retell_call_analyzed` endpoints
- Call data storage with Retell API integration

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file with:
   ```
   EXCALIDRAW_BASE_URL=http://localhost:3010
   OPENAI_API_KEY=your_xai_api_key
   OPENAI_BASE_URL=https://api.x.ai/v1/
   OPENAI_MODEL=grok-4-1-fast-non-reasoning
   ```

## Running

```bash
python excalidraw-mcp.py
```

Server will start on `http://0.0.0.0:8000`

## Endpoints

- `POST /check_diagram` - Analyze Excalidraw diagrams for SPOFs
- `POST /retell_call_ended` - Retell webhook for call ended events
- `POST /retell_call_analyzed` - Retell webhook for call analyzed events

## Data Storage

- Call data is saved to `call_data/{call_id}.json`
- Includes webhook data and full call details from Retell API

## Migration Note

This service has been consolidated into `phone_screen_agent/app/server.py`. For new deployments, use the phone_screen_agent service which includes all this functionality plus additional features.
