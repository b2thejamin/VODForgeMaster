import threading
import time
from datetime import datetime
from twitch_api import TwitchAPI
from database import (
    get_all_streamers, 
    update_streamer_twitch_id, 
    add_vod, 
    get_existing_vod_ids
)

class BackgroundWorker:
    """Background worker to poll Twitch API for new VODs."""
    
    def __init__(self, interval=120):
        self.interval = interval
        self.running = False
        self.thread = None
        self.twitch_api = TwitchAPI()
        
    def start(self):
        """Start the background worker."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"Background worker started (polling every {self.interval}s)")
    
    def stop(self):
        """Stop the background worker."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Background worker stopped")
    
    def _run(self):
        """Main worker loop."""
        while self.running:
            try:
                self._poll_vods()
            except Exception as e:
                print(f"Error in background worker: {e}")
            
            # Sleep in small increments to allow for quick shutdown
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _poll_vods(self):
        """Poll Twitch API for new VODs."""
        streamers = get_all_streamers()
        
        for streamer in streamers:
            try:
                # Get Twitch user ID if we don't have it
                if not streamer['twitch_user_id']:
                    user_id = self.twitch_api.get_user_id(streamer['handle'])
                    if user_id:
                        update_streamer_twitch_id(streamer['id'], user_id)
                        print(f"Updated Twitch user ID for {streamer['handle']}: {user_id}")
                    else:
                        print(f"Could not find Twitch user ID for {streamer['handle']}")
                        continue
                else:
                    user_id = streamer['twitch_user_id']
                
                # Get VODs for this streamer
                vods = self.twitch_api.get_vods(user_id)
                
                # Get existing VOD IDs
                existing_vod_ids = get_existing_vod_ids(streamer['id'])
                
                # Add new VODs to database
                new_vods_count = 0
                for vod in vods:
                    if vod['id'] not in existing_vod_ids:
                        result = add_vod(
                            streamer['id'],
                            vod['id'],
                            vod['title'],
                            vod['url'],
                            vod['duration_seconds'],
                            vod['created_at'],
                            vod['ended_at']
                        )
                        if result:
                            new_vods_count += 1
                            print(f"Added new VOD: {vod['title']} for {streamer['handle']}")
                
                if new_vods_count > 0:
                    print(f"Added {new_vods_count} new VOD(s) for {streamer['handle']}")
                    
            except Exception as e:
                print(f"Error polling VODs for {streamer['handle']}: {e}")
