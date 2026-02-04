import sqlite3
from datetime import datetime, timedelta
from config import Config

class Database:
    """Database manager for VODForge"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Streamers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streamers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                handle TEXT UNIQUE NOT NULL,
                twitch_user_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP
            )
        ''')
        
        # VODs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                streamer_id INTEGER NOT NULL,
                twitch_vod_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                duration_seconds INTEGER,
                created_at TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'new',
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (streamer_id) REFERENCES streamers (id)
            )
        ''')
        
        conn.commit()
        conn.close()

class StreamerModel:
    """Model for managing streamers"""
    
    def __init__(self, db):
        self.db = db
    
    def add_streamer(self, handle):
        """Add a new streamer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO streamers (handle) VALUES (?)',
                (handle,)
            )
            conn.commit()
            streamer_id = cursor.lastrowid
            return streamer_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_all_streamers(self):
        """Get all streamers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM streamers ORDER BY added_at DESC')
        streamers = cursor.fetchall()
        conn.close()
        return streamers
    
    def get_streamer_by_id(self, streamer_id):
        """Get streamer by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM streamers WHERE id = ?', (streamer_id,))
        streamer = cursor.fetchone()
        conn.close()
        return streamer
    
    def update_twitch_user_id(self, streamer_id, twitch_user_id):
        """Update Twitch user ID for streamer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE streamers SET twitch_user_id = ? WHERE id = ?',
            (twitch_user_id, streamer_id)
        )
        conn.commit()
        conn.close()
    
    def update_last_checked(self, streamer_id):
        """Update last checked timestamp"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE streamers SET last_checked = ? WHERE id = ?',
            (datetime.utcnow(), streamer_id)
        )
        conn.commit()
        conn.close()
    
    def delete_streamer(self, streamer_id):
        """Delete a streamer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM streamers WHERE id = ?', (streamer_id,))
        conn.commit()
        conn.close()

class VODModel:
    """Model for managing VODs"""
    
    def __init__(self, db):
        self.db = db
    
    def add_vod(self, streamer_id, twitch_vod_id, url, title, duration_seconds, created_at, ended_at):
        """Add a new VOD"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO vods 
                   (streamer_id, twitch_vod_id, url, title, duration_seconds, created_at, ended_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (streamer_id, twitch_vod_id, url, title, duration_seconds, created_at, ended_at)
            )
            conn.commit()
            vod_id = cursor.lastrowid
            return vod_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_vods_by_streamer(self, streamer_id):
        """Get all VODs for a streamer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM vods WHERE streamer_id = ? ORDER BY ended_at DESC',
            (streamer_id,)
        )
        vods = cursor.fetchall()
        conn.close()
        return vods
    
    def get_all_vods(self):
        """Get all VODs"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT v.*, s.handle as streamer_handle 
               FROM vods v 
               JOIN streamers s ON v.streamer_id = s.id 
               ORDER BY v.ended_at DESC'''
        )
        vods = cursor.fetchall()
        conn.close()
        return vods
    
    def update_status(self, vod_id, status):
        """Update VOD status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE vods SET status = ? WHERE id = ?',
            (status, vod_id)
        )
        conn.commit()
        conn.close()
    
    def vod_exists(self, twitch_vod_id):
        """Check if VOD already exists"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM vods WHERE twitch_vod_id = ?', (twitch_vod_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def delete_old_vods(self, days=7):
        """Delete VODs older than specified days"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            '''SELECT v.id, v.title, s.handle 
               FROM vods v 
               JOIN streamers s ON v.streamer_id = s.id 
               WHERE v.ended_at < ?''',
            (cutoff_str,)
        )
        vods_to_delete = cursor.fetchall()

        cursor.execute('DELETE FROM vods WHERE ended_at < ?', (cutoff_str,))
        delete_count = cursor.rowcount

        conn.commit()
        conn.close()

        return delete_count, vods_to_delete
