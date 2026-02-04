import time
import threading
from datetime import datetime
from models import Database, StreamerModel, VODModel
from twitch_client import TwitchClient
from config import Config

class VODWorker:
    """Background worker that polls Twitch API for new VODs"""
    
    def __init__(self):
        self.db = Database()
        self.streamer_model = StreamerModel(self.db)
        self.vod_model = VODModel(self.db)
        self.twitch_client = TwitchClient()
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background worker"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("VOD Worker started")
    
    def stop(self):
        """Stop the background worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("VOD Worker stopped")
    
    def _run(self):
        """Main worker loop"""
        while self.running:
            try:
                self.poll_streamers()
                self.cleanup_old_vods()
            except Exception as e:
                print(f"Error in worker: {e}")
            
            # Sleep for the configured interval
            for _ in range(Config.POLL_INTERVAL):
                if not self.running:
                    break
                time.sleep(1)
    
    def poll_streamers(self):
        """Poll all streamers for new VODs"""
        streamers = self.streamer_model.get_all_streamers()
        
        if not streamers:
            return
        
        print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Polling {len(streamers)} streamer(s) for VODs...")
        
        for streamer in streamers:
            try:
                self.poll_streamer(streamer)
            except Exception as e:
                print(f"Error polling streamer {streamer['handle']}: {e}")
    
    def poll_streamer(self, streamer):
        """Poll a single streamer for new VODs"""
        # Get Twitch user ID if we don't have it
        if not streamer['twitch_user_id']:
            user = self.twitch_client.get_user_by_login(streamer['handle'])
            if user:
                self.streamer_model.update_twitch_user_id(streamer['id'], user['id'])
                streamer = dict(streamer)
                streamer['twitch_user_id'] = user['id']
            else:
                print(f"Could not find Twitch user: {streamer['handle']}")
                return
        
        # Get videos from Twitch
        videos = self.twitch_client.get_videos(streamer['twitch_user_id'])
        
        new_vod_count = 0
        for video in videos:
            # Check if we already have this VOD
            if self.vod_model.vod_exists(video['id']):
                continue
            
            # Calculate ended_at from created_at + duration
            ended_at, duration_seconds = self.twitch_client.calculate_ended_at(
                video['created_at'],
                video['duration']
            )
            
            # Add the VOD to database
            vod_id = self.vod_model.add_vod(
                streamer_id=streamer['id'],
                twitch_vod_id=video['id'],
                url=video['url'],
                title=video['title'],
                duration_seconds=duration_seconds,
                created_at=video['created_at'],
                ended_at=ended_at.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if vod_id:
                new_vod_count += 1
                print(f"  → New VOD found: {streamer['handle']} - {video['title'][:50]}...")
        
        if new_vod_count > 0:
            print(f"  Added {new_vod_count} new VOD(s) for {streamer['handle']}")
        
        # Update last checked timestamp
        self.streamer_model.update_last_checked(streamer['id'])

    def cleanup_old_vods(self):
        """Delete VODs older than retention period"""
        try:
            deleted_count, deleted_vods = self.vod_model.delete_old_vods(Config.VOD_RETENTION_DAYS)
            
            if deleted_count > 0:
                print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Cleaned up {deleted_count} VOD(s) older than {Config.VOD_RETENTION_DAYS} days")
                for vod in deleted_vods:
                    print(f"  → Deleted: {vod['handle']} - {vod['title'][:50]}...")
        except Exception as e:
            print(f"Error cleaning up old VODs: {e}")

