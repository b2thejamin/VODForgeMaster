# VODForge Master - Setup Guide

## Quick Start (5 minutes)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Twitch API Credentials

1. Go to https://dev.twitch.tv/console/apps
2. Click "Register Your Application"
3. Fill in:
   - **Name**: VODForge Master
   - **OAuth Redirect URLs**: http://localhost
   - **Category**: Application Integration
4. Click "Create"
5. Copy your **Client ID** and **Client Secret**

### Step 3: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

Add your Twitch credentials:
```env
TWITCH_CLIENT_ID=paste_your_client_id_here
TWITCH_CLIENT_SECRET=paste_your_client_secret_here
FLASK_SECRET_KEY=generate_a_random_string_here
FLASK_DEBUG=False
```

### Step 4: Run the Application

```bash
python run.py
```

You should see:
```
============================================================
VODForge Master is running!
============================================================
Dashboard: http://127.0.0.1:5000
Press Ctrl+C to stop
============================================================
```

### Step 5: Open Dashboard

Open your browser and go to: **http://127.0.0.1:5000**

### Step 6: Add Streamers

1. Click "Streamers" tab
2. Enter a Twitch username (e.g., "shroud", "pokimane")
3. Click "Add Streamer"
4. Wait 120 seconds for the first poll
5. New VODs will appear on the Dashboard

## How It Works

- **Automatic Polling**: Background worker checks Twitch every 120 seconds
- **VOD Detection**: New VODs are automatically saved to database
- **Time Calculation**: Accurately computes when each VOD ended
- **Status Tracking**: Mark VODs as you work on them (new → in progress → clipped)

## Features

✅ Manual streamer management  
✅ Automatic VOD detection (120s intervals)  
✅ Accurate "time since ended" display  
✅ Status tracking (new/in_progress/clipped)  
✅ Beautiful dashboard with statistics  
✅ Local SQLite database  
✅ No server costs  

## Troubleshooting

### "Failed to get access token"
- Check your Client ID and Client Secret in `.env`
- Ensure you created the app at https://dev.twitch.tv/console/apps

### "Could not find Twitch user"
- Verify the username is correct
- The user must exist on Twitch

### No VODs appearing
- Wait at least 120 seconds for first poll
- Check that streamer has recent VODs
- Look at console output for errors

### Port 5000 already in use
- Change port in `run.py`: `app.run(host='127.0.0.1', port=5001)`

## Technical Details

- **Language**: Python 3.11+
- **Framework**: Flask 3.0.0
- **Database**: SQLite (vodforge.db)
- **API**: Twitch Helix API
- **Polling**: Every 120 seconds
- **Deployment**: Local only

## Security Notes

⚠️ This is designed for local use only  
⚠️ Keep your `.env` file private  
⚠️ Don't commit `.env` to git  
⚠️ Debug mode is OFF by default

## Support

For issues, check:
1. Console output for error messages
2. Twitch credentials are correct
3. Internet connection is working
4. Python version is 3.11+

## License

MIT License - Free to use and modify
