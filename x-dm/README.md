# X DM POC

POC for sending Direct Messages via the X API for the xAI Hackathon.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Add your X API credentials to `.env`:
   - Get your API Key and API Secret from developer.x.com
   - Update the `.env` file with your credentials

3. Run the script:
```bash
npm run send
```

## Required Credentials

You need these from your X Developer Portal (developer.x.com):
- API Key (Consumer Key)
- API Secret (Consumer Secret)
- Access Token
- Access Token Secret

Make sure your app has "Read and Write and Direct Messages" permissions enabled.

## Security Note

⚠️ The access token and secret in `.env` were shared publicly and should be regenerated after testing.
