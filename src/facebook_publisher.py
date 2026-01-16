"""
Facebook publishing module for the Football News Bot.

This module handles posting content to Facebook Pages via the Graph API:
    - Photo posts with captions
    - Proper error handling and validation
    - Rate limit awareness

Requires a Page Access Token with pages_manage_posts permission.
"""

import os
import logging
from typing import Dict, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import get_env_var, sanitize_for_facebook, is_dry_run, api_retry

logger = logging.getLogger(__name__)


class FacebookPublishError(Exception):
    """Custom exception for Facebook publishing errors."""
    pass


class FacebookPublisher:
    """
    Handles publishing content to a Facebook Page via the Graph API.
    
    Attributes:
        page_id: Facebook Page ID
        access_token: Page Access Token with posting permissions
    """
    
    GRAPH_API_VERSION = "v19.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    
    # Maximum caption length for Facebook posts
    MAX_CAPTION_LENGTH = 63206  # Facebook's limit
    
    def __init__(self):
        """Initialize the Facebook publisher with credentials."""
        self.page_id = get_env_var("FB_PAGE_ID", required=True)
        self.access_token = get_env_var("FB_PAGE_ACCESS_TOKEN", required=True)
        self.session = requests.Session()
    
    def _validate_credentials(self) -> bool:
        """
        Validate the Facebook credentials by making a test API call.
        
        Returns:
            True if credentials are valid
        
        Raises:
            FacebookPublishError: If credentials are invalid
        """
        logger.info("Validating Facebook credentials...")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{self.page_id}",
                params={
                    "fields": "id,name,access_token",
                    "access_token": self.access_token
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Authenticated as page: {data.get('name', 'Unknown')}")
                return True
            else:
                error = response.json().get("error", {})
                raise FacebookPublishError(
                    f"Facebook authentication failed: {error.get('message', 'Unknown error')}"
                )
                
        except requests.RequestException as e:
            raise FacebookPublishError(f"Failed to validate Facebook credentials: {e}")
    
    @api_retry
    def publish_photo(self, image_path: str, caption: str) -> Dict[str, str]:
        """
        Upload a photo with caption to the Facebook Page.
        
        Args:
            image_path: Local path to the image file
            caption: The complete post text (message + hashtags)
        
        Returns:
            Dict with post_id and success status
        
        Raises:
            FacebookPublishError: If publishing fails
        """
        # Validate inputs
        if not os.path.exists(image_path):
            raise FacebookPublishError(f"Image file not found: {image_path}")
        
        # Sanitize caption one more time
        caption = sanitize_for_facebook(caption)
        
        # Truncate if needed
        if len(caption) > self.MAX_CAPTION_LENGTH:
            caption = caption[:self.MAX_CAPTION_LENGTH - 3] + "..."
            logger.warning("Caption was truncated to fit Facebook's limit")
        
        # Check for dry run mode
        if is_dry_run():
            logger.info("DRY RUN MODE - Would post:")
            logger.info(f"Caption: {caption[:200]}...")
            logger.info(f"Image: {image_path}")
            return {
                "post_id": "DRY_RUN_123",
                "success": True,
                "dry_run": True
            }
        
        # Validate credentials
        self._validate_credentials()
        
        logger.info("Publishing photo to Facebook...")
        
        url = f"{self.BASE_URL}/{self.page_id}/photos"
        
        try:
            with open(image_path, "rb") as image_file:
                files = {
                    "source": (os.path.basename(image_path), image_file, "image/jpeg")
                }
                data = {
                    "message": caption,
                    "access_token": self.access_token
                }
                
                response = self.session.post(
                    url,
                    files=files,
                    data=data,
                    timeout=120  # Longer timeout for file upload
                )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                
                if "id" in result:
                    post_id = result["id"]
                    logger.info(f"Photo published successfully! Post ID: {post_id}")
                    
                    return {
                        "post_id": post_id,
                        "success": True,
                        "dry_run": False
                    }
                else:
                    raise FacebookPublishError(f"Unexpected response: {result}")
            
            else:
                error_data = response.json()
                error = error_data.get("error", {})
                error_message = error.get("message", "Unknown error")
                error_code = error.get("code", "Unknown")
                
                # Handle specific error codes
                if error_code == 190:
                    raise FacebookPublishError(
                        "Access token expired or invalid. Please generate a new token."
                    )
                elif error_code == 10:
                    raise FacebookPublishError(
                        "Permission denied. Ensure the token has 'pages_manage_posts' permission."
                    )
                elif error_code == 100:
                    raise FacebookPublishError(
                        f"Invalid parameter: {error_message}"
                    )
                elif error_code == 4:
                    raise FacebookPublishError(
                        "Rate limit reached. Try again later."
                    )
                else:
                    raise FacebookPublishError(
                        f"Facebook API error ({error_code}): {error_message}"
                    )
                    
        except requests.RequestException as e:
            raise FacebookPublishError(f"Network error while publishing: {e}")
    
    def publish_text_only(self, message: str) -> Dict[str, str]:
        """
        Publish a text-only post (without image).
        
        This is a fallback if image posting fails.
        
        Args:
            message: The post text
        
        Returns:
            Dict with post_id and success status
        """
        # Sanitize message
        message = sanitize_for_facebook(message)
        
        if is_dry_run():
            logger.info("DRY RUN MODE - Would post text:")
            logger.info(f"Message: {message[:200]}...")
            return {
                "post_id": "DRY_RUN_TEXT_123",
                "success": True,
                "dry_run": True
            }
        
        self._validate_credentials()
        
        logger.info("Publishing text post to Facebook...")
        
        url = f"{self.BASE_URL}/{self.page_id}/feed"
        
        try:
            response = self.session.post(
                url,
                data={
                    "message": message,
                    "access_token": self.access_token
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "id" in result:
                logger.info(f"Text post published! Post ID: {result['id']}")
                return {
                    "post_id": result["id"],
                    "success": True,
                    "dry_run": False
                }
            else:
                raise FacebookPublishError(f"Unexpected response: {result}")
                
        except requests.RequestException as e:
            raise FacebookPublishError(f"Failed to publish text post: {e}")


def publish_photo_post(image_path: str, caption: str) -> Dict[str, str]:
    """
    Main entry point for publishing a photo post to Facebook.
    
    This function creates a FacebookPublisher instance and uploads
    the photo with caption to the configured Facebook Page.
    
    Args:
        image_path: Local path to the image file
        caption: Complete post caption (text + hashtags + credit)
    
    Returns:
        Dict containing:
            - post_id: Facebook's post ID
            - success: Boolean indicating success
            - dry_run: True if this was a dry run (no actual post)
    
    Raises:
        FacebookPublishError: If publishing fails
    
    Example:
        >>> result = publish_photo_post("/tmp/image.jpg", "Great match! ⚽ #Football")
        >>> print(f"Posted! ID: {result['post_id']}")
        "Posted! ID: 123456789"
    """
    publisher = FacebookPublisher()
    return publisher.publish_photo(image_path, caption)


def publish_text_post(message: str) -> Dict[str, str]:
    """
    Fallback function to publish a text-only post.
    
    Use this if image posting fails.
    
    Args:
        message: Post text content
    
    Returns:
        Dict with post_id and success status
    """
    publisher = FacebookPublisher()
    return publisher.publish_text_only(message)
