export async function onRequest() {
  return new Response(JSON.stringify({ 
    status: 'healthy',
    timestamp: new Date().toISOString()
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
