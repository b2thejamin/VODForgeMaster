import requests
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

class TwitchAPI:
    """Handle Twitch API interactions."""
    
    def __init__(self):
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.access_token = None
        self.base_url = 'https://api.twitch.tv/helix'
        
    def get_access_token(self):
        """Get an OAuth access token from Twitch."""
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.access_token = data['access_token']
            return True
        except Exception as e:
            print(f"Error getting access token: {e}")
            return False
    
    def get_headers(self):
        """Get headers for API requests."""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def get_user_id(self, username):
        """Get Twitch user ID from username."""
        headers = self.get_headers()
        if not headers:
            return None
        
        url = f'{self.base_url}/users'
        params = {'login': username}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                return data['data'][0]['id']
            return None
        except Exception as e:
            print(f"Error getting user ID for {username}: {e}")
            return None
    
    def get_vods(self, user_id):
        """Get VODs for a user."""
        headers = self.get_headers()
        if not headers:
            return []
        
        url = f'{self.base_url}/videos'
        params = {
            'user_id': user_id,
            'type': 'archive',
            'first': 20
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            vods = []
            for video in data.get('data', []):
                # Parse duration string (e.g., "1h30m45s" to seconds)
                duration_seconds = self.parse_duration(video['duration'])
                
                # Parse created_at timestamp
                created_at = datetime.fromisoformat(video['created_at'].replace('Z', '+00:00'))
                
                # Calculate ended_at based on created_at + duration
                ended_at = created_at + timedelta(seconds=duration_seconds)
                
                vods.append({
                    'id': video['id'],
                    'title': video['title'],
                    'url': video['url'],
                    'duration_seconds': duration_seconds,
                    'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'ended_at': ended_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return vods
        except Exception as e:
            print(f"Error getting VODs for user {user_id}: {e}")
            return []
    
    def parse_duration(self, duration_str):
        """Parse Twitch duration string (e.g., '1h30m45s') to seconds."""
        total_seconds = 0
        current_num = ''
        
        for char in duration_str:
            if char.isdigit():
                current_num += char
            elif char == 'h':
                if current_num:
                    total_seconds += int(current_num) * 3600
                current_num = ''
            elif char == 'm':
                if current_num:
                    total_seconds += int(current_num) * 60
                current_num = ''
            elif char == 's':
                if current_num:
                    total_seconds += int(current_num)
                current_num = ''
        
        return total_seconds
