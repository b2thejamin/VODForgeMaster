import sqlite3
from datetime import datetime

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect('vodforge.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create streamers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streamers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT UNIQUE NOT NULL,
            twitch_user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create VODs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            streamer_id INTEGER NOT NULL,
            twitch_vod_id TEXT UNIQUE NOT NULL,
            title TEXT,
            url TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            ended_at TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'new',
            FOREIGN KEY (streamer_id) REFERENCES streamers (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_streamer(handle):
    """Add a new streamer to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO streamers (handle) VALUES (?)', (handle,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_streamers():
    """Get all streamers from the database."""
    conn = get_db_connection()
    streamers = conn.execute('SELECT * FROM streamers ORDER BY created_at DESC').fetchall()
    conn.close()
    return streamers

def update_streamer_twitch_id(streamer_id, twitch_user_id):
    """Update the Twitch user ID for a streamer."""
    conn = get_db_connection()
    conn.execute('UPDATE streamers SET twitch_user_id = ? WHERE id = ?', 
                 (twitch_user_id, streamer_id))
    conn.commit()
    conn.close()

def add_vod(streamer_id, twitch_vod_id, title, url, duration_seconds, created_at, ended_at):
    """Add a new VOD to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO vods (streamer_id, twitch_vod_id, title, url, duration_seconds, created_at, ended_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (streamer_id, twitch_vod_id, title, url, duration_seconds, created_at, ended_at))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_vods():
    """Get all VODs with streamer information."""
    conn = get_db_connection()
    vods = conn.execute('''
        SELECT vods.*, streamers.handle as streamer_handle
        FROM vods
        JOIN streamers ON vods.streamer_id = streamers.id
        ORDER BY vods.ended_at DESC
    ''').fetchall()
    conn.close()
    return vods

def get_vods_for_streamer(streamer_id):
    """Get all VODs for a specific streamer."""
    conn = get_db_connection()
    vods = conn.execute('''
        SELECT * FROM vods
        WHERE streamer_id = ?
        ORDER BY ended_at DESC
    ''', (streamer_id,)).fetchall()
    conn.close()
    return vods

def get_existing_vod_ids(streamer_id):
    """Get all existing Twitch VOD IDs for a streamer."""
    conn = get_db_connection()
    vods = conn.execute('''
        SELECT twitch_vod_id FROM vods WHERE streamer_id = ?
    ''', (streamer_id,)).fetchall()
    conn.close()
    return {vod['twitch_vod_id'] for vod in vods}

def update_vod_status(vod_id, status):
    """Update the status of a VOD."""
    conn = get_db_connection()
    conn.execute('UPDATE vods SET status = ? WHERE id = ?', (status, vod_id))
    conn.commit()
    conn.close()
