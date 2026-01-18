# VODForge Master 🎬

A Python 3.11 Flask application for tracking Twitch VODs (Video On Demand) on your local PC. Automatically polls Twitch API every 120 seconds to detect new VODs, calculate accurate end times, and display time since ended.

## Features

- ✅ **Manual Streamer Management**: Add/remove Twitch streamers via web interface
- ✅ **Automatic VOD Detection**: Background worker polls Twitch API every 120 seconds
- ✅ **Accurate Timing**: Computes VOD end time from start time + duration
- ✅ **Time Since Ended**: Shows how long ago each VOD ended (e.g., "2h ago", "3d ago")
- ✅ **Status Tracking**: Mark VODs as "new", "in_progress", or "clipped"
- ✅ **Beautiful Dashboard**: Clean, modern UI to view streamers and VODs
- ✅ **Local SQLite Database**: No external database required
- ✅ **No Paid Server Needed**: Runs entirely on your local PC

## Requirements

- Python 3.11+
- Twitch API credentials (free from https://dev.twitch.tv/console/apps)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/b2thejamin/VODForgeMaster.git
   cd VODForgeMaster
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Twitch API credentials**
   - Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
   - Click "Register Your Application"
   - Fill in the form:
     - Name: VODForge Master (or any name)
     - OAuth Redirect URLs: http://localhost
     - Category: Application Integration
   - Click "Create"
   - Copy your **Client ID** and **Client Secret**
   
5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_CLIENT_SECRET=your_client_secret_here
   FLASK_SECRET_KEY=your_random_secret_key_here
   FLASK_DEBUG=True
   ```

## Usage

1. **Start the application**
   ```bash
   python run.py
   ```

2. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

3. **Add streamers**
   - Click on "Streamers" tab
   - Enter Twitch username (e.g., "shroud", "pokimane")
   - Click "Add Streamer"

4. **Monitor VODs**
   - The background worker automatically polls Twitch every 120 seconds
   - New VODs appear on the Dashboard
   - Update VOD status as you work on them

## Project Structure

```
VODForgeMaster/
├── app.py              # Flask application and routes
├── config.py           # Configuration management
├── models.py           # Database models (Streamer, VOD)
├── twitch_client.py    # Twitch API integration
├── worker.py           # Background polling worker
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── templates/          # HTML templates
    ├── base.html       # Base template
    ├── dashboard.html  # Dashboard view
    └── streamers.html  # Streamer management
```

## How It Works

1. **Background Worker**: Runs in a separate thread, polling Twitch API every 120 seconds
2. **VOD Detection**: For each streamer, fetches recent VODs from Twitch
3. **Time Calculation**: Computes accurate `ended_at` time using `created_at + duration`
4. **Database Storage**: Saves VOD metadata to SQLite database
5. **Dashboard Display**: Shows all VODs with "time since ended" information
6. **Status Management**: Track VOD processing status (new/in_progress/clipped)

## Database Schema

### Streamers Table
- `id`: Primary key
- `handle`: Twitch username
- `twitch_user_id`: Twitch user ID (fetched from API)
- `added_at`: When the streamer was added
- `last_checked`: Last time VODs were checked

### VODs Table
- `id`: Primary key
- `streamer_id`: Foreign key to streamers
- `twitch_vod_id`: Unique VOD ID from Twitch
- `url`: VOD URL
- `title`: VOD title
- `duration_seconds`: Duration in seconds
- `created_at`: When the VOD was created (stream started)
- `ended_at`: When the VOD ended (calculated)
- `status`: "new", "in_progress", or "clipped"
- `discovered_at`: When we discovered the VOD

## API Endpoints

- `GET /` - Dashboard
- `GET /streamers` - Streamer management
- `POST /streamers/add` - Add new streamer
- `POST /streamers/delete/<id>` - Delete streamer
- `POST /vods/<id>/status` - Update VOD status
- `GET /api/vods` - JSON API for VODs

## Troubleshooting

**"Failed to get access token"**
- Verify your Twitch Client ID and Client Secret in `.env`
- Make sure you created the app at https://dev.twitch.tv/console/apps

**"Could not find Twitch user"**
- Check that the username is correct
- The user must exist on Twitch

**No VODs appearing**
- Wait at least 120 seconds for the first poll
- Check that the streamer has recent VODs on their channel
- Check the console output for any errors

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
