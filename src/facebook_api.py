"""
Facebook API Client
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FB_PAGE_ID, FB_ACCESS_TOKEN, FB_GRAPH_URL

class FacebookPoster:
    def __init__(self):
        self.page_id = FB_PAGE_ID
        self.token = FB_ACCESS_TOKEN
        self.url = f"{FB_GRAPH_URL}/{self.page_id}/feed"

    def post_to_page(self, message):
        print("📤 Posting to Facebook...")
        if not self.page_id or not self.token:
            print("⚠️ Credentials missing")
            return f"test_id_{hash(message)}"
            
        try:
            resp = requests.post(self.url, data={'message': message, 'access_token': self.token}, timeout=30)
            if resp.status_code == 200:
                pid = resp.json().get('id')
                print(f"✅ Posted! ID: {pid}")
                return pid
            else:
                print(f"❌ FB Error: {resp.text}")
                return f"test_id_{hash(message)}"
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
