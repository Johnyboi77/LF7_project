/* Keep supabase db for this project alive */

export default async function handler(req, res) {
  const SUPABASE_URL = 'https://lbaeftxthrpajcgdxdcz.supabase.co';
  const SUPABASE_KEY = process.env.SUPABASE_KEY;

  try {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/breakdata`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({
        session_id: crypto.randomUUID(),
        pause_number: 0,
        step_count: 0,
        calories_burned: '0',
        distance_meters: '0',
        device_id: 'cron'
      })
    });

    if (response.ok) {
      return res.status(200).json({ 
        success: true, 
        message: 'Database alive!',
        timestamp: new Date().toISOString()
      });
    } else {
      const error = await response.text();
      return res.status(500).json({ success: false, error });
    }
  } catch (error) {
    return res.status(500).json({ success: false, error: error.message });
  }
}