# Phone Screen Agent

AI-powered phone screen and system design interview agent using Retell AI and Tavus.

## Features

- **Phone Screen Interviews** - Automated technical phone screens via Retell AI
- **System Design Interviews** - Visual system design interviews via Tavus with Excalidraw integration
- **Automatic Grading** - LLM-powered evaluation of both interview types
- **Diagram Analysis** - Real-time architecture diagram feedback using `check_diagram` tool
- **Webhook Handling** - Processes Retell and Tavus webhooks for call data and transcripts

## Setup

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# OpenAI / X.AI Configuration
OPENAI_ORGANIZATION_ID=your_openai_org_id
OPENAI_API_KEY=your_xai_api_key_here
OPENAI_BASE_URL=https://api.x.ai/v1
LLM_MODEL=grok-beta

# Retell AI Configuration
RETELL_API_KEY=your_retell_api_key_here

# Excalidraw Configuration
EXCALIDRAW_BASE_URL=http://localhost:3010

# Optional: Skip signature verification for debugging
# SKIP_SIGNATURE_VERIFICATION=false
```

#### Configuration Details

- **OPENAI_ORGANIZATION_ID**: Your OpenAI organization ID
- **OPENAI_API_KEY**: Your X.AI API key (or OpenAI key if using OpenAI)
- **OPENAI_BASE_URL**: API endpoint (`https://api.x.ai/v1` for X.AI, `https://api.openai.com/v1` for OpenAI)
- **LLM_MODEL**: Model to use (`grok-beta` for X.AI, `gpt-4o` for OpenAI)
- **RETELL_API_KEY**: Your Retell AI API key for phone screen interviews
- **EXCALIDRAW_BASE_URL**: URL of your Excalidraw instance (default: `http://localhost:3010`)
- **SKIP_SIGNATURE_VERIFICATION**: Set to `true` to skip Retell webhook signature verification (useful for debugging with ngrok)

### 3. Start Excalidraw (for System Design Interviews)

In a separate terminal, start the Excalidraw canvas:

```bash
cd ../mcp_excalidraw
npm run build
npm run canvas
```

This will start Excalidraw on `http://localhost:3010`.

### 4. Expose Server with ngrok

In another terminal, use ngrok to expose the server to the public internet:

```bash
ngrok http 8080
```

You should see a forwarding address like:
`https://abc123.ngrok-free.app`

### 5. Start the Server

```bash
uvicorn app.server:app --reload --port=8080
```

## Retell AI Setup

### Create Custom LLM Agent

1. Go to [Retell Dashboard](https://beta.retellai.com/dashboard)
2. Create a new agent with Custom LLM
3. Use your ngrok URL with the `/llm-websocket` path:
   ```
   wss://abc123.ngrok-free.app/llm-websocket
   ```

### Configure Webhooks

Set up webhooks in Retell Dashboard to point to:
```
https://abc123.ngrok-free.app/webhook
```

This enables automatic grading of phone screen interviews.

## Tavus Setup

Configure Tavus webhooks to point to:
```
https://abc123.ngrok-free.app/tavus-webhook
```

This enables automatic grading of system design interviews.

## Endpoints

- `GET /` - Health check
- `POST /check_diagram` - Analyze Excalidraw diagrams for architecture issues
- `POST /webhook` - Retell webhook handler (call events and grading)
- `POST /tavus-webhook` - Tavus webhook handler (conversation events and grading)
- `WS /llm-websocket/{call_id}` - Retell LLM WebSocket connection

## Interview Grading

The system automatically grades interviews when webhooks are received:

### Phone Screen Grading
- **Trigger**: Retell `call_ended` webhook
- **Output**: `call_data/{call_id}_phone_screen_grade.json`
- **Rubric**: Technical depth (40%), Communication (30%), Problem-solving (20%), Cultural fit (10%)

### System Design Grading
- **Trigger**: Tavus webhook with transcript
- **Output**: `tavus_webhooks/{conversation_id}_{timestamp}_system_design_grade.json`
- **Rubric**: Requirements (15%), Architecture (35%), Scalability (25%), Technical depth (15%), Communication (10%)

Each grade includes:
- Score (0-3): Strong No, Weak No, Weak Yes, Strong Yes
- Reasoning with specific examples
- Interview summary

## Production Deployment

For production:
1. Host the code on a cloud provider (AWS, GCP, Azure, etc.)
2. Use a proper domain with SSL/TLS
3. Set up proper authentication and rate limiting
4. Configure production-grade logging and monitoring
5. Remove `SKIP_SIGNATURE_VERIFICATION` or set to `false`
