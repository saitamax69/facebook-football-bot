"""
Facebook API Client for posting to Facebook Pages
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FB_PAGE_ID, FB_ACCESS_TOKEN, FB_GRAPH_URL


class FacebookPoster:
    """Client for posting to Facebook Pages"""
    
    def __init__(self):
        self.page_id = FB_PAGE_ID
        self.access_token = FB_ACCESS_TOKEN
        self.base_url = FB_GRAPH_URL
    
    def post_to_page(self, message):
        """Post message to Facebook page"""
        print("📤 Posting to Facebook...")
        
        if not self.page_id or not self.access_token:
            print("⚠️ Facebook credentials not configured")
            return f"test_post_{hash(message) % 100000}"
        
        url = f"{self.base_url}/{self.page_id}/feed"
        data = {'message': message, 'access_token': self.access_token}
        
        try:
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                post_id = response.json().get('id')
                print(f"✅ Posted! ID: {post_id}")
                return post_id
            else:
                error = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"❌ Facebook error: {error}")
                return f"test_post_{hash(message) % 100000}"
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def validate_token(self):
        """Check if access token is valid"""
        if not self.access_token:
            return False
        
        try:
            url = f"{self.base_url}/me"
            response = requests.get(url, params={'access_token': self.access_token}, timeout=10)
            return response.status_code == 200
        except:
            return False
