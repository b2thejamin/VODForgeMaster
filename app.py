from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import Database, StreamerModel, VODModel
from worker import VODWorker
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize database and models
db = Database()
streamer_model = StreamerModel(db)
vod_model = VODModel(db)

# Initialize and start worker
worker = VODWorker()

def format_time_since(ended_at_str):
    """Format time since VOD ended"""
    if not ended_at_str:
        return 'Unknown'
    
    try:
        ended_at = datetime.strptime(ended_at_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            ended_at = datetime.strptime(ended_at_str.replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return 'Unknown'
    
    now = datetime.utcnow()
    delta = now - ended_at
    
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
    else:
        return f"{delta.seconds}s ago"

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if not seconds:
        return 'Unknown'
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

@app.route('/')
def index():
    """Dashboard - main page"""
    streamers = streamer_model.get_all_streamers()
    vods = vod_model.get_all_vods()
    
    # Format VOD data
    formatted_vods = []
    for vod in vods:
        formatted_vods.append({
            'id': vod['id'],
            'streamer_handle': vod['streamer_handle'],
            'title': vod['title'],
            'url': vod['url'],
            'duration': format_duration(vod['duration_seconds']),
            'ended_at': vod['ended_at'],
            'time_since': format_time_since(vod['ended_at']),
            'status': vod['status']
        })
    
    return render_template('dashboard.html', streamers=streamers, vods=formatted_vods)

@app.route('/streamers')
def streamers():
    """Streamers management page"""
    streamers = streamer_model.get_all_streamers()
    return render_template('streamers.html', streamers=streamers)

@app.route('/streamers/add', methods=['POST'])
def add_streamer():
    """Add a new streamer"""
    handle = request.form.get('handle', '').strip()
    
    if not handle:
        flash('Streamer handle is required', 'error')
        return redirect(url_for('streamers'))
    
    streamer_id = streamer_model.add_streamer(handle)
    
    if streamer_id:
        flash(f'Streamer {handle} added successfully', 'success')
    else:
        flash(f'Streamer {handle} already exists', 'error')
    
    return redirect(url_for('streamers'))

@app.route('/streamers/delete/<int:streamer_id>', methods=['POST'])
def delete_streamer(streamer_id):
    """Delete a streamer"""
    streamer_model.delete_streamer(streamer_id)
    flash('Streamer deleted successfully', 'success')
    return redirect(url_for('streamers'))

@app.route('/vods/<int:vod_id>/status', methods=['POST'])
def update_vod_status(vod_id):
    """Update VOD status"""
    status = request.form.get('status')
    
    if status in ['new', 'in_progress', 'clipped']:
        vod_model.update_status(vod_id, status)
        flash('VOD status updated', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/vods')
def api_vods():
    """API endpoint to get VODs"""
    vods = vod_model.get_all_vods()
    
    formatted_vods = []
    for vod in vods:
        formatted_vods.append({
            'id': vod['id'],
            'streamer_handle': vod['streamer_handle'],
            'title': vod['title'],
            'url': vod['url'],
            'duration': format_duration(vod['duration_seconds']),
            'ended_at': vod['ended_at'],
            'time_since': format_time_since(vod['ended_at']),
            'status': vod['status']
        })
    
    return jsonify(formatted_vods)

def start_app():
    """Start the Flask app and worker"""
    worker.start()
    return app

if __name__ == '__main__':
    app = start_app()
    app.run(debug=Config.DEBUG, host='127.0.0.1', port=5000)
