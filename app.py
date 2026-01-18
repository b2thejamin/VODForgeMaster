from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timezone
from database import (
    init_db, 
    add_streamer, 
    get_all_streamers, 
    get_all_vods,
    update_vod_status
)
from worker import BackgroundWorker
import atexit

app = Flask(__name__)

# Initialize database
init_db()

# Start background worker
worker = BackgroundWorker(interval=120)
worker.start()

# Stop worker on shutdown
atexit.register(worker.stop)

def format_time_since(ended_at_str):
    """Format time since VOD ended."""
    try:
        ended_at = datetime.strptime(ended_at_str, '%Y-%m-%d %H:%M:%S')
        ended_at = ended_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - ended_at
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h ago"
        elif hours > 0:
            return f"{hours}h {minutes}m ago"
        else:
            return f"{minutes}m ago"
    except:
        return "Unknown"

def format_duration(seconds):
    """Format duration in seconds to human readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

@app.route('/')
def index():
    """Main dashboard."""
    streamers = get_all_streamers()
    vods = get_all_vods()
    
    # Enhance VOD data with formatted information
    enhanced_vods = []
    for vod in vods:
        enhanced_vod = dict(vod)
        enhanced_vod['time_since_ended'] = format_time_since(vod['ended_at'])
        enhanced_vod['duration_formatted'] = format_duration(vod['duration_seconds'])
        enhanced_vods.append(enhanced_vod)
    
    return render_template('index.html', 
                         streamers=streamers, 
                         vods=enhanced_vods)

@app.route('/add_streamer', methods=['POST'])
def add_streamer_route():
    """Add a new streamer."""
    handle = request.form.get('handle', '').strip()
    
    if not handle:
        return redirect(url_for('index'))
    
    # Remove @ if present
    if handle.startswith('@'):
        handle = handle[1:]
    
    result = add_streamer(handle)
    
    return redirect(url_for('index'))

@app.route('/update_status/<int:vod_id>/<status>', methods=['POST'])
def update_status(vod_id, status):
    """Update VOD status."""
    if status in ['new', 'in_progress', 'clipped']:
        update_vod_status(vod_id, status)
    return jsonify({'success': True})

@app.template_filter('datetimeformat')
def datetimeformat(value):
    """Format datetime for display."""
    try:
        dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %I:%M %p')
    except:
        return value

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
