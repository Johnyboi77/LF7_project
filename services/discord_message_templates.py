"""
Discord Message Templates
Alle Nachrichten-Vorlagen zentral verwaltbar
"""

class MessageTemplates:
    """Alle Discord-Nachrichts-Vorlagen"""
    
    # ===== SESSION LIFECYCLE =====
    
    @staticmethod
    def session_start(user_name):
        return {
            "title": f"👋 Hey {user_name}!",
            "description": (
                f"**Deine Lerneinheit wurde gestartet!** 📚\n\n"
                f"🟦 **30 Minuten Arbeitszeit**\n"
                f"Konzentriert arbeiten, du schaffst das! 💪\n\n"
                f"⏱️ Der Timer läuft..."
            ),
            "color": 5763719,
            "emoji": "📚"
        }
    
    @staticmethod
    def work_finished(user_name):
        return {
            "title": f"⏰ Hey {user_name}!",
            "description": (
                f"**Deine 30-Minuten Lernphase ist vorbei!** 🎉\n\n"
                f"⏸️ **Zeit für eine 10-minütige Pause**\n\n"
                f"**Empfohlene Aktivitäten:**\n"
                f"🚶‍♀️ Kurzer Spaziergang\n"
                f"🪟 Fenster öffnen & lüften\n"
                f"💧 Wasser trinken\n"
                f"👉 Drücke **Button 2** um Pause zu starten"
            ),
            "color": 3447003,
            "emoji": "⏰"
        }
    
    @staticmethod
    def break_finished(user_name):
        return {
            "title": f"🔔 Pause vorbei!",
            "description": (
                f"Hallo {user_name}! ☕\n\n"
                f"**Deine 10-Minuten Pause ist abgelaufen!**\n\n"
                f"🚀 Bereit für die nächste Lernphase?\n\n"
                f"👉 Drücke **Button 1** um weiterzumachen"
            ),
            "color": 3066993,
            "emoji": "☕"
        }
    
    @staticmethod
    def break_stats(user_name, pause_number, steps, calories, distance):
        return {
            "title": f"📊 Pause #{pause_number} Statistik",
            "description": (
                f"Super, {user_name}! 🏃‍♀️\n\n"
                f"**Bewegung in der Pause:**\n"
                f"👣 Schritte: **{steps:,}**\n"
                f"🔥 Kalorien: **~{calories} kcal**\n"
                f"📏 Distanz: **~{distance}m**\n\n"
                f"{MessageTemplates._get_motivation(steps)}"
            ),
            "color": 10181046,
            "emoji": "👣"
        }
    
    # ===== CO2 ALERTS =====
    
    @staticmethod
    def co2_warning(user_name, co2_level, tvoc_level):
        return {
            "title": f"⚠️ Luftqualität warnen",
            "description": (
                f"Hey {user_name}! 🌡️\n\n"
                f"**Die Luftqualität verschlechtert sich!**\n\n"
                f"📊 **Aktuelle Werte:**\n"
                f"• eCO2: **{co2_level} ppm** ⚠️\n"
                f"• TVOC: **{tvoc_level} ppb**\n\n"
                f"💡 Bitte bald lüften!\n"
                f"Bessere Luftqualität = bessere Konzentration 🧠"
            ),
            "color": 16776960,  # Gelb
            "emoji": "⚠️"
        }
    
    @staticmethod
    def co2_critical(user_name, co2_level, tvoc_level):
        return {
            "title": f"🚨 KRITISCHE LUFTQUALITÄT!",
            "description": (
                f"{user_name}, Achtung! 🚨\n\n"
                f"**Die Luftqualität ist kritisch!**\n\n"
                f"📊 **Aktuelle Werte:**\n"
                f"• eCO2: **{co2_level} ppm** 🚨\n"
                f"• TVOC: **{tvoc_level} ppb**\n\n"
                f"🚪 **SOFORT LÜFTEN!**\n"
                f"Zu viel CO2 beeinträchtigt deine Konzentration ernsthaft.\n\n"
                f"🔴 Rote LED blinkt | Buzzer piept"
            ),
            "color": 15158332,  # Rot
            "emoji": "🚨"
        }
    
    # ===== SESSION REPORT =====
    
    @staticmethod
    def session_report(user_name, stats):
        """
        Erstellt ausführlichen Session-Report
        
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
            f"⚠️ Alarm-Perioden: **{alarm_count}x**\n\n"
            
            f"**👣 BEWEGUNG IN PAUSEN**\n"
            f"🚶 Schritte: **{steps:,}**\n"
            f"🔥 Kalorien: **{calories} kcal**\n"
            f"📏 Distanz: **{distance_km:.2f} km**\n"
            f"🎯 Tagesziel (10.000): **{step_percentage:.0f}%**\n\n"
            
            f"**Tolle Arbeit, {user_name}!** 🎉\n"
            f"Bis zur nächsten Session! 👋"
        )
        
        return {
            "title": f"📊 Session-Report für {user_name}",
            "description": description,
            "color": 10181046,
            "emoji": "📊",
            "fields": [
                {
                    "name": "🎯 Zusammenfassung",
                    "value": f"**{work_time_str}** gelernt | **{pause_count}** Pausen | **{steps:,}** Schritte",
                    "inline": False
                }
            ]
        }
    
    # ===== HILFSFUNKTIONEN =====
    
    @staticmethod
    def _get_motivation(steps):
        """Motivierende Nachricht basierend auf Schritten"""
        if steps >= 1000:
            return "🏆 Wow, super aktive Pause!"
        elif steps >= 500:
            return "💪 Gute Bewegung!"
        elif steps >= 200:
            return "👍 Schön bewegt!"
        elif steps > 0:
            return "🚶 Jeder Schritt zählt!"
        else:
            return "💤 Nächstes Mal etwas mehr Bewegung?"