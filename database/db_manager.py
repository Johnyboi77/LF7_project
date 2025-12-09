# database/db_manager.py
import sqlite3
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # CO2 Messwerte
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS co2_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    co2_level INTEGER
                )
            ''')
            
            # Button Events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS button_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    button_id INTEGER,
                    action TEXT
                )
            ''')
            
            # Schritte
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    step_count INTEGER
                )
            ''')
            
            # Benachrichtigungen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    type TEXT,
                    message TEXT,
                    sent BOOLEAN
                )
            ''')
    
    def log_co2(self, co2_level):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO co2_readings (co2_level) VALUES (?)', (co2_level,))
    
    def log_button(self, button_id, action="pressed"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO button_events (button_id, action) VALUES (?, ?)', 
                          (button_id, action))
    
    def log_steps(self, step_count):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO steps (step_count) VALUES (?)', (step_count,))
    
    def log_notification(self, type, message, sent):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO notifications (type, message, sent) VALUES (?, ?, ?)',
                          (type, message, sent))
    
    def get_latest_co2(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT co2_level FROM co2_readings ORDER BY timestamp DESC LIMIT 1')
            result = cursor.fetchone()
            return result['co2_level'] if result else None