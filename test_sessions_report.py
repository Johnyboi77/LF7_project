"""
Test Report - Compare multiple sessions
Zeigt Report für mehrere Sessions an
"""

import os
import sys

os.environ['DEVICE_OVERRIDE'] = 'pitop1'

from database.supabase_manager import SupabaseManager
from services.discord_templates import NotificationService

def test_session(db, notify, session_id):
    """Test a single session"""
    print(f"\n{'='*70}")
    print(f"📊 Session: {session_id[:8]}...")
    print(f"{'='*70}")

    try:
        report_data = db.get_session_report_data(session_id)

        if not report_data:
            print("❌ Keine Report-Daten gefunden!")
            return False

        # Terminal Report
        notify.print_terminal_report(report_data)
        return True

    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_all_sessions(db):
    """Get list of all sessions"""
    try:
        result = db.client.table('sessions')\
            .select('session_id, start_time, end_time, pause_count, total_work_time, total_pause_time')\
            .order('start_time', desc=True)\
            .limit(5)\
            .execute()

        if result.data:
            return result.data
        return []
    except Exception as e:
        print(f"❌ Error getting sessions: {e}")
        return []

def main():
    db = SupabaseManager()
    notify = NotificationService()

    if not db.client:
        print("❌ Database connection failed!")
        return

    if len(sys.argv) > 1:
        # Test specific session
        session_id = sys.argv[1]
        test_session(db, notify, session_id)
    else:
        # Test multiple recent sessions
        print("\n" + "="*70)
        print("📊 TESTE LETZTE 5 SESSIONS")
        print("="*70)

        sessions = get_all_sessions(db)

        if not sessions:
            print("❌ Keine Sessions gefunden!")
            return

        print(f"\n✅ Gefundene Sessions: {len(sessions)}\n")

        success_count = 0
        for i, session in enumerate(sessions, 1):
            session_id = session['session_id']
            print(f"\n[{i}/{len(sessions)}] Testing: {session_id[:8]}...")
            print(f"    start_time: {session.get('start_time', 'N/A')}")
            print(f"    end_time: {session.get('end_time', 'N/A')}")
            print(f"    pause_count: {session.get('pause_count', 0)}")
            print(f"    work_time: {session.get('total_work_time', 0)}s")
            print(f"    break_time: {session.get('total_pause_time', 0)}s")

            if test_session(db, notify, session_id):
                success_count += 1

        print(f"\n\n✅ Erfolgreich: {success_count}/{len(sessions)} Sessions")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Abgebrochen")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
