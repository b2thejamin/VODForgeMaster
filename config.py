import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE_PATH = 'vodforge.db'
    
    # Twitch API
    TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID', '')
    TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET', '')
    
    # Worker
    POLL_INTERVAL = 120  # seconds
