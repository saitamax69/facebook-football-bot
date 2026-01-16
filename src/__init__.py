"""
Facebook Football News Bot - Source Package

A fully automated bot that fetches football news, generates engaging content,
and posts to a Facebook Page using the Graph API.

Modules:
    - news_fetcher: Retrieves football news from NewsAPI or TheSportsDB
    - content_generator: Uses LLM to create engaging social media posts
    - image_handler: Downloads relevant football images from Unsplash/Pexels
    - facebook_publisher: Publishes content to Facebook via Graph API
    - utils: Shared utility functions (URL stripping, retry logic, etc.)
"""

__version__ = "1.0.0"
__author__ = "Football News Bot"

from .news_fetcher import fetch_football_news
from .content_generator import generate_engaging_post
from .image_handler import get_football_image
from .facebook_publisher import publish_photo_post
from .utils import strip_all_urls, setup_logging

__all__ = [
    "fetch_football_news",
    "generate_engaging_post",
    "get_football_image",
    "publish_photo_post",
    "strip_all_urls",
    "setup_logging",
]
