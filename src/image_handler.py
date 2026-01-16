"""
Image handling module for the Facebook Football News Bot.

This module downloads relevant football images from stock photo APIs:
    - Primary: Unsplash API (50 free requests/hour)
    - Fallback: Pexels API (200 free requests/hour)

Images are downloaded to temporary files for upload to Facebook.
"""

import os
import logging
import tempfile
from typing import Tuple, Optional
from pathlib import Path
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import get_env_var, api_retry

logger = logging.getLogger(__name__)


class ImageHandlerError(Exception):
    """Custom exception for image handling errors."""
    pass


class ImageHandler:
    """
    Handles downloading football-related images from stock photo APIs.
    
    Supports Unsplash and Pexels with automatic fallback.
    """
    
    UNSPLASH_API_URL = "https://api.unsplash.com"
    PEXELS_API_URL = "https://api.pexels.com/v1"
    
    # Search queries for football images (varied for diversity)
    SEARCH_QUERIES = [
        "football soccer stadium",
        "soccer match",
        "football players",
        "soccer ball field",
        "football stadium crowd",
        "soccer goal celebration",
        "football pitch",
        "soccer game action"
    ]
    
    def __init__(self):
        """Initialize the image handler with API credentials."""
        self.unsplash_key = get_env_var("UNSPLASH_ACCESS_KEY", required=False)
        self.pexels_key = get_env_var("PEXELS_API_KEY", required=False)
        self.session = requests.Session()
        
        # Track query index for variety
        self._query_index = 0
    
    def _get_search_query(self) -> str:
        """Get the next search query (rotates through list)."""
        query = self.SEARCH_QUERIES[self._query_index % len(self.SEARCH_QUERIES)]
        self._query_index += 1
        return query
    
    @api_retry
    def _fetch_from_unsplash(self) -> Optional[Tuple[str, str]]:
        """
        Fetch a random football image from Unsplash.
        
        Returns:
            Tuple of (image_url, photographer_credit) or None if failed
        """
        if not self.unsplash_key:
            logger.info("Unsplash API key not configured, skipping...")
            return None
        
        logger.info("Fetching image from Unsplash...")
        
        headers = {
            "Authorization": f"Client-ID {self.unsplash_key}",
            "Accept-Version": "v1"
        }
        
        params = {
            "query": self._get_search_query(),
            "orientation": "landscape",
            "content_filter": "high"  # Safe content only
        }
        
        try:
            response = self.session.get(
                f"{self.UNSPLASH_API_URL}/photos/random",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Get the regular size URL (1080px width)
            image_url = data["urls"]["regular"]
            
            # Get photographer credit
            photographer = data["user"]["name"]
            username = data["user"]["username"]
            credit = f"{photographer} (@{username}) via Unsplash"
            
            logger.info(f"Unsplash image found: {photographer}")
            return (image_url, credit)
            
        except requests.RequestException as e:
            logger.warning(f"Unsplash API call failed: {e}")
            raise
        except KeyError as e:
            logger.warning(f"Failed to parse Unsplash response: {e}")
            return None
    
    @api_retry
    def _fetch_from_pexels(self) -> Optional[Tuple[str, str]]:
        """
        Fetch a football image from Pexels.
        
        Returns:
            Tuple of (image_url, photographer_credit) or None if failed
        """
        if not self.pexels_key:
            logger.info("Pexels API key not configured, skipping...")
            return None
        
        logger.info("Fetching image from Pexels...")
        
        headers = {
            "Authorization": self.pexels_key
        }
        
        params = {
            "query": self._get_search_query(),
            "per_page": 15,
            "orientation": "landscape",
            "size": "large"
        }
        
        try:
            response = self.session.get(
                f"{self.PEXELS_API_URL}/search",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            photos = data.get("photos", [])
            
            if not photos:
                logger.warning("No photos found from Pexels")
                return None
            
            # Select a random photo from results
            import random
            photo = random.choice(photos)
            
            # Get the large size URL
            image_url = photo["src"]["large"]
            
            # Get photographer credit
            photographer = photo["photographer"]
            credit = f"{photographer} via Pexels"
            
            logger.info(f"Pexels image found: {photographer}")
            return (image_url, credit)
            
        except requests.RequestException as e:
            logger.warning(f"Pexels API call failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.warning(f"Failed to parse Pexels response: {e}")
            return None
    
    @api_retry
    def _download_image(self, url: str) -> str:
        """
        Download an image from URL to a temporary file.
        
        Args:
            url: Image URL to download
        
        Returns:
            Path to the downloaded temporary file
        
        Raises:
            ImageHandlerError: If download fails
        """
        logger.info(f"Downloading image...")
        
        try:
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Determine file extension from content type
            content_type = response.headers.get("Content-Type", "image/jpeg")
            extension = ".jpg"
            if "png" in content_type:
                extension = ".png"
            elif "webp" in content_type:
                extension = ".webp"
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=extension,
                delete=False
            )
            
            # Download in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            
            temp_file.close()
            
            # Verify file size
            file_size = os.path.getsize(temp_file.name)
            if file_size < 1000:  # Less than 1KB is suspicious
                os.unlink(temp_file.name)
                raise ImageHandlerError("Downloaded image is too small")
            
            logger.info(f"Image downloaded: {temp_file.name} ({file_size / 1024:.1f} KB)")
            return temp_file.name
            
        except requests.RequestException as e:
            logger.error(f"Failed to download image: {e}")
            raise ImageHandlerError(f"Image download failed: {e}")
    
    def _get_placeholder_image(self) -> Tuple[str, str]:
        """
        Generate a placeholder image when APIs are unavailable.
        
        Uses Pillow to create a simple branded image.
        
        Returns:
            Tuple of (image_path, credit_text)
        """
        logger.warning("Using placeholder image generation")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a gradient-like background
            width, height = 1200, 630
            image = Image.new('RGB', (width, height), color=(34, 139, 34))  # Forest green
            draw = ImageDraw.Draw(image)
            
            # Add a darker rectangle
            draw.rectangle([50, 50, width-50, height-50], fill=(0, 100, 0))
            
            # Add text
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            except:
                font_large = ImageFont.load_default()
                font_small = font_large
            
            # Add football emoji and text
            draw.text((width//2, height//2 - 50), "⚽ FOOTBALL NEWS", 
                      fill=(255, 255, 255), font=font_large, anchor="mm")
            draw.text((width//2, height//2 + 50), "Daily Updates", 
                      fill=(200, 200, 200), font=font_small, anchor="mm")
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            image.save(temp_file.name, "PNG")
            temp_file.close()
            
            return (temp_file.name, "Football News Bot")
            
        except ImportError:
            logger.error("Pillow not available for placeholder image")
            raise ImageHandlerError("No image APIs available and Pillow not installed")
    
    def fetch(self) -> Tuple[str, str]:
        """
        Fetch a football image with automatic fallback.
        
        Returns:
            Tuple containing:
                - image_path: Local path to downloaded image file
                - credit: Photographer/source credit string
        
        Raises:
            ImageHandlerError: If all image sources fail
        """
        image_url = None
        credit = None
        
        # Try Unsplash first
        try:
            result = self._fetch_from_unsplash()
            if result:
                image_url, credit = result
        except Exception as e:
            logger.warning(f"Unsplash failed: {e}")
        
        # Fall back to Pexels
        if not image_url:
            try:
                result = self._fetch_from_pexels()
                if result:
                    image_url, credit = result
            except Exception as e:
                logger.warning(f"Pexels failed: {e}")
        
        # Download the image if we got a URL
        if image_url:
            image_path = self._download_image(image_url)
            return (image_path, credit)
        
        # Fall back to placeholder
        return self._get_placeholder_image()


def get_football_image() -> Tuple[str, str]:
    """
    Main entry point for fetching a football image.
    
    This function creates an ImageHandler instance and retrieves
    an image from the configured sources with automatic fallback.
    
    Returns:
        Tuple containing:
            - image_path: Path to local image file (temporary)
            - credit: Photographer/source credit to include in post
    
    Example:
        >>> path, credit = get_football_image()
        >>> print(f"Image at {path}, credit: {credit}")
        "Image at /tmp/xyz123.jpg, credit: John Doe via Unsplash"
    
    Note:
        The caller is responsible for cleaning up the temporary file
        after uploading to Facebook.
    """
    handler = ImageHandler()
    return handler.fetch()
