"""
Supabase Database Manager
Verwaltet Verbindung und Operationen für beide PiTops
"""

from supabase import create_client, Client
from datetime import datetime
import config
import uuid

class SupabaseManager:
    def __init__(self):
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            print("❌ FEHLER: Supabase Credentials fehlen in .env!")
            print("💡 Bitte SUPABASE_URL und SUPABASE_KEY setzen")
            self.client = None
            return
        
        try:
            self.client: Client = create_client(
                config.SUPABASE_URL,
                config.SUPABASE_KEY
            )
            print(f"✅ Supabase verbunden ({config.DEVICE_ID})")
            self._test_connection()
            
        except Exception as e:
            print(f"❌ Supabase Verbindungsfehler: {e}")
            self.client = None
    
    # Testet Datenbankverbindung
    def _test_connection(self):
        try:
            response = self.client.table('sessions').select("id").limit(1).execute()
            print(f"✅ Datenbank erreichbar ({len(response.data) if hasattr(response, 'data') else 0} sessions)")
        except Exception as e:
            print(f"⚠️  Datenbank-Test fehlgeschlagen: {e}")
    
    # ===== SESSION MANAGEMENT =====
    
    # Erstellt neue Session (nur PiTop 1)
    def create_session(self):
        if not self.client:
            return None
        
        try:
            session_id = str(uuid.uuid4())
            
            data = {
                "session_id": session_id,
                "start_time": datetime.utcnow().isoformat(),
                "timer_status": "idle",
                "user_name": config.USER_NAME,
                "user_weight": config.USER_WEIGHT,
                "user_height": config.USER_HEIGHT,
                "device_id": config.DEVICE_ID
            }
            
            response = self.client.table('sessions').insert(data).execute()
            
            if response.data:
                print(f"✅ Session erstellt: {session_id[:8]}...")
                return session_id
            
            return None
            
        except Exception as e:
            print(f"❌ Session-Fehler: {e}")
            return None
    
    # Aktualisiert Timer-Status (working, work_ended, break, break_ended)
    def update_timer_status(self, session_id, status):
        if not self.client or not session_id:
            return False
        
        try:
            self.client.table('sessions')\
                .update({"timer_status": status})\
                .eq('session_id', session_id)\
                .execute()
            
            print(f"📊 Timer Status: {status}")
            return True
            
        except Exception as e:
            print(f"❌ Status-Update Fehler: {e}")
            return False
    
    # Erhöht pause_count um 1
    def increment_pause_count(self, session_id):
        if not self.client or not session_id:
            return False
        
        try:
            # Aktuellen Wert holen
            response = self.client.table('sessions')\
                .select('pause_count')\
                .eq('session_id', session_id)\
                .single()\
                .execute()
            
            current_count = response.data.get('pause_count', 0) if response.data else 0
            new_count = current_count + 1
            
            # Erhöhen
            self.client.table('sessions')\
                .update({"pause_count": new_count})\
                .eq('session_id', session_id)\
                .execute()
            
            print(f"�� Pause Count: {new_count}")
            return new_count
            
        except Exception as e:
            print(f"❌ Pause-Count Fehler: {e}")
            return False
    
    # Beendet Session
    def end_session(self, session_id, total_work_time, total_pause_time):
        if not self.client or not session_id:
            return False
        
        try:
            self.client.table('sessions')\
                .update({
                    "end_time": datetime.utcnow().isoformat(),
                    "total_work_time": total_work_time,
                    "total_pause_time": total_pause_time,
                    "timer_status": "ended"
                })\
                .eq('session_id', session_id)\
                .execute()
            
            print(f"✅ Session beendet: {session_id[:8]}...")
            return True
            
        except Exception as e:
            print(f"❌ Session-End Fehler: {e}")
            return False
    
    # ===== LOGGING =====
    
    # Loggt CO2-Messung
    def log_co2(self, session_id, co2_level, tvoc_level=None, is_alarm=False, alarm_type=None):
        if not self.client:
            return False
        
        try:
            data = {
                "session_id": session_id,
                "co2_level": co2_level,
                "tvoc_level": tvoc_level,
                "is_alarm": is_alarm,
                "alarm_type": alarm_type,
                "device_id": config.DEVICE_ID
            }
            
            self.client.table('co2_measurements').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"❌ CO2 Log Fehler: {e}")
            return False
    
    # Loggt Schritte (PiTop 2)
    def log_steps(self, session_id, pause_number, step_count, calories, distance):
        if not self.client:
            return False
        
        try:
            data = {
                "session_id": session_id,
                "pause_number": pause_number,
                "step_count": step_count,
                "calories_burned": calories,
                "distance_meters": distance,
                "device_id": config.DEVICE_ID
            }
            
            self.client.table('breakdata').insert(data).execute()
            print(f"💾 Schritte gespeichert: {step_count:,} (Pause {pause_number})")
            return True
            
        except Exception as e:
            print(f"❌ Steps Log Fehler: {e}")
            return False
    
    # ===== QUERIES (für PiTop 2) =====
    
    # Holt aktuelle Session (ohne end_time)
    def get_active_session(self):
        if not self.client:
            return None
        
        try:
            response = self.client.table('sessions')\
                .select('session_id, pause_count, timer_status, user_weight, user_height')\
                .is_('end_time', 'null')\
                .order('start_time', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data and len(response.data) > 0:
                session = response.data[0]
                print(f"📊 Aktive Session: {session['session_id'][:8]}...")
                return session
            
            print("ℹ️  Keine aktive Session gefunden")
            return None
            
        except Exception as e:
            print(f"❌ Query-Fehler: {e}")
            return None
    
    # Holt aktuellen Timer-Status
    def get_timer_status(self, session_id):
        """Holt aktuellen Timer-Status"""
        if not self.client or not session_id:
            return None
        
        try:
            response = self.client.table('sessions')\
                .select('timer_status')\
                .eq('session_id', session_id)\
                .single()\
                .execute()
            
            if response.data:
                return response.data.get('timer_status')
            
            return None
            
        except Exception as e:
            print(f"❌ Status-Query Fehler: {e}")
            return None
    
    # ===== REPORT DATA =====
    
    # Holt alle Daten für Report
    def get_session_report_data(self, session_id):
        if not self.client or not session_id:
            return None
        
        try:
            # 1. Session Info
            session_response = self.client.table('sessions')\
                .select('*')\
                .eq('session_id', session_id)\
                .single()\
                .execute()
            
            # 2. CO2 Daten
            co2_response = self.client.table('co2_measurements')\
                .select('co2_level, is_alarm')\
                .eq('session_id', session_id)\
                .execute()
            
            co2_values = [row['co2_level'] for row in co2_response.data] if co2_response.data else []
            
            # Alarm-Perioden zählen (nicht einzelne Messungen)
            alarm_count = 0
            was_in_alarm = False
            for row in co2_response.data:
                if row.get('is_alarm') and not was_in_alarm:
                    alarm_count += 1
                    was_in_alarm = True
                elif not row.get('is_alarm'):
                    was_in_alarm = False
            
            co2_stats = {
                'avg_co2': int(sum(co2_values) / len(co2_values)) if co2_values else 0,
                'min_co2': min(co2_values) if co2_values else 0,
                'max_co2': max(co2_values) if co2_values else 0,
                'alarm_count': alarm_count
            }
            
            # 3. Bewegungsdaten (letzter Eintrag)
            movement_response = self.client.table('breakdata')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('pause_number', desc=True)\
                .limit(1)\
                .execute()
            
            movement_data = movement_response.data[0] if movement_response.data else {
                'step_count': 0,
                'calories_burned': 0,
                'distance_meters': 0
            }
            
            return {
                'session': session_response.data if session_response.data else {},
                'co2': co2_stats,
                'movement': movement_data
            }
            
        except Exception as e:
            print(f"❌ Report-Daten Fehler: {e}")
            return None
