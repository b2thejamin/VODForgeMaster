import requests
from datetime import datetime, timedelta
from config import Config

class TwitchClient:
    """Client for interacting with Twitch API"""
    
    def __init__(self):
        self.client_id = Config.TWITCH_CLIENT_ID
        self.client_secret = Config.TWITCH_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """Get OAuth access token from Twitch"""
        if self.access_token and self.token_expires_at and datetime.utcnow() < self.token_expires_at:
            return self.access_token
        
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            expires_in = data['expires_in']
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")
    
    def get_headers(self):
        """Get headers for API requests"""
        token = self.get_access_token()
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}'
        }
    
    def get_user_by_login(self, login):
        """Get user information by login name"""
        url = 'https://api.twitch.tv/helix/users'
        params = {'login': login}
        headers = self.get_headers()
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                return data['data'][0]
        return None
    
    def get_videos(self, user_id, first=20):
        """Get videos (VODs) for a user"""
        url = 'https://api.twitch.tv/helix/videos'
        params = {
            'user_id': user_id,
            'first': first,
            'type': 'archive'  # Only get VODs, not highlights or uploads
        }
        headers = self.get_headers()
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data['data']
        return []
    
    def parse_duration(self, duration_str):
        """Parse ISO 8601 duration string (e.g., '2h30m15s') to seconds"""
        # Duration format: 1h2m3s or 30m15s or 45s
        total_seconds = 0
        current_num = ''
        
        for char in duration_str:
            if char.isdigit():
                current_num += char
            elif char in ['h', 'm', 's']:
                if current_num:
                    num = int(current_num)
                    if char == 'h':
                        total_seconds += num * 3600
                    elif char == 'm':
                        total_seconds += num * 60
                    elif char == 's':
                        total_seconds += num
                    current_num = ''
        
        return total_seconds
    
    def calculate_ended_at(self, created_at_str, duration_str):
        """Calculate when the VOD ended based on created_at and duration"""
        # Parse created_at (ISO 8601 format)
        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%SZ')
        
        # Parse duration
        duration_seconds = self.parse_duration(duration_str)
        
        # Calculate ended_at
        ended_at = created_at + timedelta(seconds=duration_seconds)
        
        return ended_at, duration_seconds
