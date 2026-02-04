#!/usr/bin/env python3
"""
VODForge Master - Main entry point
Run this script to start the Flask app and background worker
"""

#Add vod deletion after 1 week
#Change style to vodforge colors
#make it so there is a desktop app that you can click to launch the app

from app import start_app
from config import Config

if __name__ == '__main__':
    app = start_app()
    print("=" * 60)
    print("VODForge Master is running!")
    print("=" * 60)
    print("Dashboard: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    if Config.DEBUG:
        print("⚠️  WARNING: Debug mode is ON - Do not use in production!")
    print("=" * 60)
    app.run(debug=Config.DEBUG, host='127.0.0.1', port=5000)
