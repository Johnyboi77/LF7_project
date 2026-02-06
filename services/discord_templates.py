"""
Discord Message Templates & Notification Service
Kombiniert Templates und Versand-Logik
"""

import requests
from datetime import datetime
import config


class MessageTemplates:
    """Alle Discord-Nachrichts-Vorlagen"""
    
    # ===== 1. SESSION START =====
    
    @staticmethod
    def session_start(user_name):
        """Wird beim Start der Lerneinheit versendet"""
        return {
            "title": f"👋 Hey {user_name}!",
            "description": (
                f"**Deine Lerneinheit wurde gestartet** 📚\n\n"
                f"⏱️ *30 Minuten ab jetzt! **\n"
            ),
            "color": 5763719,  # Blau
            "emoji": "📚"
        }
    
    # ===== 2. BREAK STATS (nach jeder Pause) =====
    
    @staticmethod
    def break_stats(user_name, pause_number, steps, calories, distance):
        """Wird nach JEDER Pause versendet (zusammenfassend)"""
        return {
            "title": f"☕ Pause #{pause_number} beendet!",
            "description": (
                f"Super, {user_name}! 🏃‍♀️\n\n"
                f"**Bewegung in der Pause:**\n"
                f"👣 Schritte: **{steps:,}**\n"
                f"🔥 Verbrannte Kalorien: **~{calories} kcal**\n"
                f"📏 Zurückgelegte Distanz: **~{distance}m**\n\n"
                f"{MessageTemplates._get_motivation(steps)}\n\n"
                f"🚀 Bereit für die nächste Lernphase?\n"
                f"👉 Drücke Button 1 zum Weitermachen!"
                f"👉 Halte Button 1 zum Beenden deiner Session!"
            ),
            "color": 10181046,  # Lila
            "emoji": "👣"
        }
    
    # ===== 3. SESSION REPORT (Finaler Report) =====
    
    @staticmethod
    def session_report(user_name, stats):
        """
        Finaler Report am Ende der Lerneinheit
        
        Args:
            user_name: Benutzer-Name
            stats: Dict mit session, co2, movement Daten
        """
        
        session = stats.get('session', {})
        co2 = stats.get('co2', {})
        movement = stats.get('movement', {})
        
        # ===== ZEITEN =====
        work_secs = session.get('total_work_time', 0)
        break_secs = session.get('total_pause_time', 0)
        pause_count = session.get('pause_count', 0)
        
        work_mins = work_secs // 60
        work_hours = work_mins // 60
        work_mins_rest = work_mins % 60
        break_mins = break_secs // 60
        
        if work_hours > 0:
            work_time_str = f"{work_hours}h {work_mins_rest}min"
        else:
            work_time_str = f"{work_mins}min"
        
        # ===== CO2 =====
        avg_co2 = co2.get('avg_co2', 0)
        min_co2 = co2.get('min_co2', 0)
        max_co2 = co2.get('max_co2', 0)
        alarm_count = co2.get('alarm_count', 0)
        
        if avg_co2 < 600:
            co2_rating = "💚 Ausgezeichnet"
        elif avg_co2 < 800:
            co2_rating = "💛 Gut"
        elif avg_co2 < 1000:
            co2_rating = "🧡 Mäßig"
        else:
            co2_rating = "❤️ Schlecht"
        
        # ===== BEWEGUNG =====
        steps = movement.get('step_count', 0)
        calories = movement.get('calories_burned', 0)
        distance = movement.get('distance_meters', 0)
        distance_km = distance / 1000
        
        step_goal = 10000
        step_percentage = min(100, (steps / step_goal) * 100) if steps > 0 else 0
        
        # ===== NACHRICHT =====
        description = (
            f"**⏰ ZEITÜBERSICHT**\n"
            f"🕐 Gesamte Lernzeit: **{work_time_str}**\n"
            f"☕ Gesamte Pausenzeit: **{break_mins} min**\n"
            f"📚 Anzahl Pausen: **{pause_count}**\n\n"
            
            f"**🌡️ LUFTQUALITÄT**\n"
            f"{co2_rating}\n"
            f"📊 Ø Durchschnitt: **{avg_co2} ppm**\n"
            f"📉 Minimum: **{min_co2} ppm**\n"
            f"📈 Maximum: **{max_co2} ppm**\n"
            f"⚠️ Co2 Alarm: **{alarm_count}x**\n\n"
            
            f"**👣 BEWEGUNG IN PAUSEN**\n"
            f"🚶 Schritte: **{steps:,}**\n"
            f"🔥 Kalorien: **{calories} kcal**\n"
            f"📏 Distanz: **{distance_km:.2f} km**\n"
            f"🎯 Tagesziel (10.000): **{step_percentage:.0f}%**\n\n"
            
            f"**Tolle Arbeit, {user_name}!** 🎉\n"
            f"Bis zur nächsten Session! 👋"
        )
        
        return {
            "title": f"📊 Session-Report für {user_name}\n",
            "description": description,
            "color": 10181046,  # Lila
            "emoji": "📊",
            "fields": [
                {
                    "name": "🎯 Zusammenfassung",
                    "value": f"**{work_time_str}** gelernt | **{pause_count}** Pausen | **{steps:,}** Schritte",
                    "inline": False
                }
            ]
        }
    
    # ===== CO2 ALERTS (Optional - nur bei kritischen Werten) =====
    
    @staticmethod
    def co2_critical(user_name, co2_level, tvoc_level):
        """Nur bei KRITISCHEN CO2-Werten (> 800 ppm)"""
        return {
            "title": f"🚨 KRITISCHE LUFTQUALITÄT!",
            "description": (
                f"{user_name}, Achtung! 🚨\n\n"
                f"**Die Luftqualität ist kritisch!**\n\n"
                f"📊 **Aktuelle Werte:**\n"
                f"• eCO2: **{co2_level} ppm** 🚨\n"
                f"• TVOC: **{tvoc_level} ppb**\n\n"
                f"🚪 **SOFORT LÜFTEN!**\n"
                f"Zu viel CO2 beeinträchtigt deine Konzentration.\n\n"
            ),
            "color": 15158332,  # Rot
            "emoji": "🚨"
        }
    
    # ===== HILFSFUNKTIONEN =====
    
    @staticmethod
    def _get_motivation(steps):
        """Motivierende Nachricht basierend auf Schritten"""
        if steps >= 1000:
            return "🏆 Wow, das waren super aktive Pausen!"
        elif steps >= 500:
            return "💪 Schön bewegt!"
        elif steps >= 200:
            return "👍 Weiter so!"
        elif steps > 0:
            return "🚶 Jeder Schritt zählt!"
        else:
            return "💤 Nächstes Mal etwas mehr Bewegung?"


class NotificationService:
    def __init__(self):
        self.webhook_url = config.DISCORD_WEBHOOK_URL
        self.is_enabled = bool(self.webhook_url)
        self.user_name = config.USER_NAME
        
        if self.is_enabled:
            print(f"✅ Discord Benachrichtigungen aktiv (für {self.user_name})")
        else:
            print("⚠️ Discord Webhook nicht konfiguriert")
    
    def send(self, message, notification_type="info", ping_user=False):
        """Sendet Benachrichtigung an Discord"""
        if not self.is_enabled:
            print(f"📢 [MOCK] {message}")
            return False
        
        try:
            embed = self._create_embed(message, notification_type)
            
            payload = {"embeds": [embed]}
            
            # Optional: User pingen
            if ping_user:
                payload["content"] = "🔔"
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 204:
                print(f"✅ Discord-Nachricht gesendet ({notification_type})")
                return True
            else:
                print(f"⚠️  Discord-Fehler: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Discord-Sendefehler: {e}")
            return False
    
    def _create_embed(self, message, notification_type):
        """Erstellt Discord Embed"""
        embed = {
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Learning Assistant"}
        }
        
        if notification_type == "session_start":
            embed.update({
                "title": f"👋 Hey {self.user_name}!",
                "description": message,
                "color": 5763719,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/books_1f4da.png"}
            })
        
        elif notification_type == "work_finished":
            embed.update({
                "title": f"⏰ Hey {self.user_name}!",
                "description": message,
                "color": 3447003,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/alarm-clock_23f0.png"}
            })
        
        elif notification_type == "break_finished":
            embed.update({
                "title": f"⏰ Hey {self.user_name}!",
                "description": message,
                "color": 3066993,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/alarm-clock_23f0.png"}
            })
        
        elif notification_type == "session_report":
            embed.update({
                "title": f"🎓 Session-Report für {self.user_name}",
                "description": message,
                "color": 10181046,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/bar-chart_1f4ca.png"}
            })
        
        elif notification_type == "co2_warning":
            embed.update({
                "title": f"🌡️ Hey {self.user_name}!",
                "description": message,
                "color": 16776960,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/warning_26a0-fe0f.png"}
            })
        
        elif notification_type == "co2_critical":
            embed.update({
                "title": f"🚨 {self.user_name}, Achtung!",
                "description": message,
                "color": 15158332,
                "thumbnail": {"url": "https://em-content.zobj.net/thumbs/160/twitter/348/warning_26a0-fe0f.png"}
            })
        
        else:
            embed.update({
                "title": "ℹ️ Info",
                "description": message,
                "color": 3447003
            })
        
        return embed
    
    # ===== PERSONALISIERTE NACHRICHTEN =====
    
    def send_session_start(self):
        """Session gestartet"""
        message = (
            f"**Deine Lerneinheit wurde gestartet!** 📚\n\n"
            f"Viel Erfolg beim konzentrierten Arbeiten! 💪"
        )
        self.send(message, "session_start", ping_user=True)
    
    def send_work_finished(self):
        """Arbeitszeit vorbei (30 Min)"""
        message = (
            f"**Deine 30-Minuten Lernphase ist vorbei!**\n\n"
            f"Zeit für eine 10-minütige Pause 🧘‍♀️\n\n"
            f"**Empfohlene Aktivitäten:**\n"
            f"• Kurzer Spaziergang 🚶‍♀️\n"
            f"• Fenster öffnen 🪟\n"
            f"• Wasser trinken 💧\n"
            f"• Augen entspannen 👀\n\n"
            f"👉 Drücke Button 2 um die Pause zu starten."
        )
        self.send(message, "work_finished", ping_user=True)
    
    def send_break_finished(self):
        """Pause vorbei (10 Min)"""
        message = (
            f"**Deine Pause ist abgelaufen!**\n\n"
            f"Bereit für die nächste Lernphase? 💪\n\n"
            f"👉 Drücke Button 1 um weiterzumachen."
        )
        self.send(message, "break_finished", ping_user=True)
    
    def send_co2_alert(self, co2_level, tvoc_level, is_critical=False):
        """CO2-Warnung"""
        if is_critical:
            message = (
                f"**Die Luftqualität ist kritisch!**\n\n"
                f"📊 **Aktuelle Werte:**\n"
                f"• eCO2: **{co2_level} ppm** 🚨\n"
                f"• TVOC: {tvoc_level} ppb\n\n"
                f"🚪 **Bitte SOFORT lüften!**\n"
                f"Zu viel CO2 beeinträchtigt deine Konzentration.\n\n"
                f"🔴 Rote LED ist an + Buzzer hat gepiept"
            )
            self.send(message, "co2_critical", ping_user=True)
        else:
            message = (
                f"**Die Luftqualität verschlechtert sich**\n\n"
                f"📊 **Aktuelle Werte:**\n"
                f"• eCO2: {co2_level} ppm ⚠️\n"
                f"• TVOC: {tvoc_level} ppb\n\n"
                f"💡 Bitte bald lüften für optimale Konzentration.\n\n"
                f"🔴 Rote LED ist an"
            )
            self.send(message, "co2_warning", ping_user=False)
    
    def send_session_report(self, stats):
        """
        Sendet ausführlichen Session-Report
        
        Args:
            stats: Dict mit session, co2, movement Daten
        """
        
        session = stats.get('session', {})
        co2 = stats.get('co2', {})
        movement = stats.get('movement', {})
        
        # ===== ZEITEN =====
        start_time = session.get('start_time', '')
        end_time = session.get('end_time', '')
        
        # Zeiten formatieren
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            start_str = start_dt.strftime('%H:%M Uhr')
        else:
            start_str = "N/A"
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            end_str = end_dt.strftime('%H:%M Uhr')
        else:
            end_str = "N/A"
        
        # Dauer
        total_work_secs = session.get('total_work_time', 0)
        total_break_secs = session.get('total_pause_time', 0)
        
        work_mins = total_work_secs // 60
        work_hours = work_mins // 60
        work_mins_rest = work_mins % 60
        
        break_mins = total_break_secs // 60
        pause_count = session.get('pause_count', 0)
        
        # Arbeitszeit formatieren
        if work_hours > 0:
            work_time_str = f"{work_hours}h {work_mins_rest} Min"
        else:
            work_time_str = f"{work_mins} Min"
        
        # ===== CO2 =====
        avg_co2 = co2.get('avg_co2', 0)
        min_co2 = co2.get('min_co2', 0)
        max_co2 = co2.get('max_co2', 0)
        alarm_count = co2.get('alarm_count', 0)
        
        # CO2 Bewertung
        if avg_co2 < 600:
            co2_rating = "💚 Ausgezeichnet"
        elif avg_co2 < 800:
            co2_rating = "💛 Gut"
        elif avg_co2 < 1000:
            co2_rating = "🧡 Mäßig"
        else:
            co2_rating = "❤️ Schlecht"
        
        # ===== BEWEGUNG =====
        steps = movement.get('step_count', 0)
        calories = movement.get('calories_burned', 0)
        distance = movement.get('distance_meters', 0)
        distance_km = distance / 1000
        
        # Schritte-Ziel
        step_goal = 10000
        step_percentage = min(100, (steps / step_goal) * 100) if steps > 0 else 0
        
        # ===== NACHRICHT ZUSAMMENSTELLEN =====
        message = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**⏰ ZEITÜBERSICHT**\n\n"
            f"🕐 Start: {start_str}\n"
            f"🕐 Ende: {end_str}\n"
            f"⏱️ **Gesamte Lernzeit:** {work_time_str}\n"
            f"☕ **Gesamte Pausenzeit:** {break_mins} Min\n"
            f"📚 **Anzahl Pausen:** {pause_count}\n\n"
            f"**🌡️ LUFTQUALITÄT**\n\n"
            f"{co2_rating}\n"
            f"📊 Durchschnitt: {avg_co2} ppm\n"
            f"📉 Minimum: {min_co2} ppm\n"
            f"📈 Maximum: {max_co2} ppm\n"
            f"⚠️ Alarm-Perioden: {alarm_count}x\n\n"
            f"**👣 BEWEGUNG IN PAUSEN**\n\n"
            f"🚶‍♀️ Schritte: {steps:,}\n"
            f"🔥 Kalorien: {calories} kcal\n"
            f"📏 Distanz: {distance_km:.2f} km\n"
            f"🎯 Tagesziel (10.000): {step_percentage:.0f}% erreicht\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Tolle Arbeit, {self.user_name}!** 🎉\n"
            f"Bis zur nächsten Session! 👋"
        )
        
        self.send(message, "session_report", ping_user=True)
    
    def print_terminal_report(self, stats):
        """
        Gibt schönen Report im Terminal aus
        
        Args:
            stats: Dict mit session, co2, movement Daten
        """
        session = stats.get('session', {})
        co2 = stats.get('co2', {})
        movement = stats.get('movement', {})
        
        # Zeiten
        work_secs = session.get('total_work_time', 0)
        break_secs = session.get('total_pause_time', 0)
        pause_count = session.get('pause_count', 0)
        
        work_mins = work_secs // 60
        break_mins = break_secs // 60
        
        # CO2
        avg_co2 = co2.get('avg_co2', 0)
        min_co2 = co2.get('min_co2', 0)
        max_co2 = co2.get('max_co2', 0)
        alarms = co2.get('alarm_count', 0)
        
        # Bewegung
        steps = movement.get('step_count', 0)
        calories = movement.get('calories_burned', 0)
        distance = movement.get('distance_meters', 0)
        
        print("\n")
        print("┌─────────────────────────────────────────────┐")
        print("│         📊 SESSION REPORT                   │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ ⏱️  Lernzeit:      {work_mins:3d} Min            │")
        print(f"│ ☕ Pausenzeit:    {break_mins:3d} Min            │")
        print(f"│ 📚 Pausen:        {pause_count:3d}                 │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ 🌡️  eCO2 Ø:       {avg_co2:4d} ppm         │")
        print(f"│ 📉 eCO2 Min:     {min_co2:4d} ppm         │")
        print(f"│ 📈 eCO2 Max:     {max_co2:4d} ppm         │")
        print(f"│ ⚠️  Alarme:       {alarms:3d}                 │")
        print("├─────────────────────────────────────────────┤")
        print(f"│ 👣 Schritte:     {steps:5,}               │")
        print(f"│ 🔥 Kalorien:     {calories:3d} kcal           │")
        print(f"│ 📏 Distanz:      {distance:4d} m             │")
        print("└─────────────────────────────────────────────┘")
        print("\n")