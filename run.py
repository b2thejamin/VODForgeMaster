#!/usr/bin/env python3
"""
VODForge Master - Main entry point
Run this script to start the Flask app and background worker
"""

from app import start_app

if __name__ == '__main__':
    app = start_app()
    print("=" * 60)
    print("VODForge Master is running!")
    print("=" * 60)
    print("Dashboard: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
