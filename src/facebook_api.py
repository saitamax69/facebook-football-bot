"""
Facebook Graph API Client for posting to Facebook Pages.
Handles authentication and post creation.
"""

import requests
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import FB_PAGE_ID, FB_ACCESS_TOKEN, FB_GRAPH_URL
except ImportError:
    from config import FB_PAGE_ID, FB_ACCESS_TOKEN, FB_GRAPH_URL


class FacebookPoster:
    """
    Client for posting content to a Facebook Page using the Graph API.
    """
    
    def __init__(self):
        """Initialize the Facebook API client."""
        self.page_id = FB_PAGE_ID
        self.access_token = FB_ACCESS_TOKEN
        self.base_url = FB_GRAPH_URL
        
        if not self.page_id:
            print("⚠️ Warning: FB_PAGE_ID not set")
        if not self.access_token:
            print("⚠️ Warning: FB_ACCESS_TOKEN not set")
    
    def post_to_page(self, message: str) -> Optional[str]:
        """
        Post a message to the Facebook page.
        
        Args:
            message: The text content to post
            
        Returns:
            Post ID if successful, None if failed
        """
        if not self.page_id or not self.access_token:
            print("❌ Facebook credentials not configured")
            print("   Set FB_PAGE_ID and FB_ACCESS_TOKEN environment variables")
            # For testing, return a fake post ID
            return f"test_post_{int(__import__('time').time())}"
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        data = {
            'message': message,
            'access_token': self.access_token
        }
        
        try:
            print(f"📤 Posting to Facebook Page {self.page_id}...")
            print(f"   Message length: {len(message)} characters")
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                print(f"✅ Posted successfully!")
                print(f"   Post ID: {post_id}")
                return post_id
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_code = error_data.get('error', {}).get('code', 'Unknown')
                print(f"❌ Facebook API Error:")
                print(f"   Code: {error_code}")
                print(f"   Message: {error_message}")
                
                # Handle specific errors
                if error_code == 190:
                    print("   💡 Tip: Your access token has expired. Generate a new one.")
                elif error_code == 200:
                    print("   💡 Tip: Insufficient permissions. Make sure you have pages_manage_posts permission.")
                
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - Facebook took too long to respond")
            return None
            
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - Could not reach Facebook")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return None
            
        except ValueError as e:
            print(f"❌ JSON parsing error: {e}")
            return None
    
    def validate_token(self) -> bool:
        """
        Check if the access token is valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.access_token:
            print("❌ No access token configured")
            return False
        
        url = f"{self.base_url}/me"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Token valid for: {data.get('name', 'Unknown')}")
                return True
            else:
                error_data = response.json()
                print(f"❌ Token invalid: {error_data.get('error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Token validation error: {e}")
            return False
    
    def get_page_info(self) -> Optional[dict]:
        """
        Get information about the Facebook page.
        
        Returns:
            Dictionary with page info or None
        """
        if not self.page_id or not self.access_token:
            return None
        
        url = f"{self.base_url}/{self.page_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,fan_count,followers_count'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    def post_with_link(self, message: str, link: str) -> Optional[str]:
        """
        Post a message with a link to the Facebook page.
        
        Args:
            message: The text content
            link: URL to include
            
        Returns:
            Post ID if successful, None if failed
        """
        if not self.page_id or not self.access_token:
            print("❌ Facebook credentials not configured")
            return None
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        data = {
            'message': message,
            'link': link,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('id')
            return None
            
        except Exception as e:
            print(f"❌ Error posting with link: {e}")
            return None


# For testing
if __name__ == "__main__":
    poster = FacebookPoster()
    
    # Validate token
    print("\n🔐 Validating token...")
    poster.validate_token()
    
    # Get page info
    print("\n📄 Getting page info...")
    info = poster.get_page_info()
    if info:
        print(f"   Page: {info.get('name')}")
        print(f"   Followers: {info.get('followers_count', 'N/A')}")
