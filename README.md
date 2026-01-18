# VODForge Master

A Python 3.11 local application for tracking Twitch VODs. Built with Flask and SQLite, VODForge Master automatically monitors your favorite Twitch streamers and detects new VODs in real-time.

## Features

- **Manual Streamer Management**: Add Twitch streamer handles through a clean web interface
- **Automatic VOD Detection**: Background worker polls Twitch API every 120 seconds for new VODs
- **Accurate Timing**: Computes accurate `ended_at` timestamps and displays "time since ended"
- **Status Tracking**: Mark VODs as "new", "in_progress", or "clipped"
- **Beautiful Dashboard**: View all streamers and their VODs in an intuitive web interface
- **Local Only**: Runs entirely on your PC, no server required

## Prerequisites

- Python 3.11+
- Twitch Developer Account (for API credentials)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/b2thejamin/VODForgeMaster.git
   cd VODForgeMaster
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Twitch API Credentials**:
   - Go to https://dev.twitch.tv/console/apps
   - Click "Register Your Application"
   - Name: "VODForge Master" (or any name)
   - OAuth Redirect URL: `http://localhost` (required but not used)
   - Category: Application Integration
   - Click "Create"
   - Copy your **Client ID** and generate a **Client Secret**

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_CLIENT_SECRET=your_client_secret_here
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the dashboard**:
   - Open your browser to: http://localhost:5000
   - The background worker starts automatically and polls every 120 seconds

3. **Add streamers**:
   - Enter a Twitch username in the form (e.g., "shroud", "pokimane")
   - Click "Add Streamer"
   - The worker will automatically fetch their Twitch user ID and start monitoring for VODs

4. **Manage VODs**:
   - View all detected VODs in the VOD Library
   - Click status badges to cycle through: New → In Progress → Clipped
   - Click "Watch VOD" to open the VOD on Twitch

## How It Works

1. **Database**: SQLite database stores streamers and VODs locally in `vodforge.db`
2. **Background Worker**: Separate thread polls Twitch API every 120 seconds
3. **VOD Detection**: Compares API results with database to find new VODs
4. **Time Calculation**: 
   - Parses VOD duration (e.g., "1h30m45s")
   - Calculates `ended_at` = `created_at` + `duration`
   - Displays relative time (e.g., "2h 15m ago")

## Project Structure

```
VODForgeMaster/
├── app.py              # Flask application and routes
├── database.py         # SQLite database operations
├── twitch_api.py       # Twitch API integration
├── worker.py           # Background polling worker
├── templates/
│   └── index.html      # Dashboard UI
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md          # This file
```

## Development

The application runs in debug mode by default. File changes will automatically reload the server.

## Troubleshooting

**No VODs appearing?**
- Ensure your Twitch API credentials are correct in `.env`
- Check that streamers have recent VODs (archives) available
- Look at console output for API errors

**Background worker not running?**
- Check console for "Background worker started" message
- Worker runs in a daemon thread and starts automatically

**Database issues?**
- Delete `vodforge.db` to reset (will lose all data)
- Database is auto-created on first run

## License

MIT License - Feel free to use and modify as needed.
