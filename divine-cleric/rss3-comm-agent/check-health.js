const axios = require('axios');

// Get URL from command line argument or environment variable
const url = process.argv[2] || process.env.RAILWAY_URL || process.env.RAILWAY_PUBLIC_DOMAIN;

if (!url) {
  console.error('❌ Error: Please provide the Railway server URL');
  console.log('Usage: node check-health.js <railway-url>');
  console.log('   or: RAILWAY_URL=<railway-url> node check-health.js');
  process.exit(1);
}

// Normalize URL (add https:// if not present, remove trailing slash)
let serverUrl = url.trim();
if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
  serverUrl = `https://${serverUrl}`;
}
serverUrl = serverUrl.replace(/\/$/, '');

console.log(`🔍 Checking health of: ${serverUrl}`);

async function checkHealth() {
  try {
    // Check health endpoint
    const healthResponse = await axios.get(`${serverUrl}/health`, {
      timeout: 10000
    });
    
    console.log('\n✅ Server is UP and healthy!');
    console.log('📊 Health Status:');
    console.log(JSON.stringify(healthResponse.data, null, 2));
    
    // Also check root endpoint
    try {
      const rootResponse = await axios.get(`${serverUrl}/`, {
        timeout: 5000
      });
      console.log(`\n📡 Root endpoint response: ${rootResponse.data}`);
    } catch (err) {
      console.log('\n⚠️  Root endpoint check failed (non-critical)');
    }
    
    process.exit(0);
  } catch (error) {
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      console.error('\n❌ Server is DOWN or unreachable');
      console.error(`   Error: ${error.message}`);
    } else if (error.response) {
      console.error('\n⚠️  Server responded but with error status');
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Response: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      console.error('\n❌ Error checking server health:');
      console.error(`   ${error.message}`);
    }
    process.exit(1);
  }
}

checkHealth();

