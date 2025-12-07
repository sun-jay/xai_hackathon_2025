import { TwitterApi } from 'twitter-api-v2';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize X API client with OAuth 1.0a credentials
const client = new TwitterApi({
  appKey: process.env.API_KEY,
  appSecret: process.env.API_SECRET,
  accessToken: process.env.ACCESS_TOKEN,
  accessSecret: process.env.ACCESS_TOKEN_SECRET,
});

async function sendDM() {
  try {
    const recipientId = process.env.RECIPIENT_USER_ID;
    const message = process.env.MESSAGE || 'yo im testing my shi for the xai hackathon';

    console.log(`Sending DM to user ID: ${recipientId}`);
    console.log(`Message: "${message}"`);

    // Send the DM using X API v2 endpoint
    const result = await client.v2.sendDmToParticipant(recipientId, {
      text: message,
    });

    console.log('\n✅ DM sent successfully!');
    console.log('Response:', JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('\n❌ Error sending DM:');
    console.error('Error code:', error.code);
    console.error('Error message:', error.message);

    if (error.data) {
      console.error('Error details:', JSON.stringify(error.data, null, 2));
    }

    // Common error hints
    if (error.code === 403) {
      console.error('\n💡 Hint: Make sure your app has "Read and Write and Direct Messages" permissions');
      console.error('💡 Also verify you have the correct API credentials (API Key & Secret)');
    } else if (error.code === 401) {
      console.error('\n💡 Hint: Check your access token and secret are correct');
    }
  }
}

// Run the function
sendDM();
