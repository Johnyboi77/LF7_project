# PiTop1 schreibt timer_status='break' → Supabase

self.db.client.table('sessions').update({
    'timer_status': 'break'
}).eq('session_id', self.session_id).execute()

# PiTop2 liest alle 1 Sekunde aus Supabase:

result = self.db.client.table('sessions')\
    .select('session_id, timer_status')\
    .order('start_time', desc=True).limit(1).execute()

if result['timer_status'] == 'break':
    self.steps.start()  # ← Schrittzähler startet!
Keine direkte Kommunikation - alles über Supabase Datenbank als "Message Broker" 