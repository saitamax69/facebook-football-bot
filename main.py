#!/usr/bin/env python3
"""
Main orchestrator for the Facebook Football News Bot.

This script coordinates the full workflow:
    1. Fetch latest football news
    2. Generate engaging social media content using LLM
    3. Download a relevant football image
    4. Publish everything to Facebook

Usage:
    python main.py

Environment Variables Required:
    - FB_PAGE_ID: Facebook Page ID
    - FB_PAGE_ACCESS_TOKEN: Page Access Token with posting permissions
    
Optional (but recommended):
    - NEWSAPI_KEY: API key for NewsAPI.org
    - UNSPLASH_ACCESS_KEY: API key for Unsplash
    - PEXELS_API_KEY: API key for Pexels
    - OPENAI_API_KEY: API key for OpenAI
    - HUGGINGFACE_TOKEN: Token for Hugging Face Inference API
    - DRY_RUN: Set to 'true' for testing without posting
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.news_fetcher import fetch_football_news
from src.content_generator import generate_engaging_post
from src.image_handler import get_football_image
from src.facebook_publisher import publish_photo_post, publish_text_post
from src.utils import setup_logging, is_dry_run, strip_all_urls

# Initialize logging
logger = setup_logging()


def cleanup_temp_file(file_path: str) -> None:
    """
    Safely remove a temporary file.
    
    Args:
        file_path: Path to the file to remove
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


def main() -> int:
    """
    Main entry point for the Football News Bot.
    
    Returns:
        0 on success, 1 on failure
    """
    logger.info("=" * 60)
    logger.info("🚀 Football News Bot Starting")
    logger.info("=" * 60)
    
    if is_dry_run():
        logger.info("⚠️  DRY RUN MODE ENABLED - No actual posts will be made")
    
    image_path = None
    
    try:
        # ========================================
        # Step 1: Fetch latest football news
        # ========================================
        logger.info("")
        logger.info("📰 Step 1: Fetching latest football news...")
        
        news = fetch_football_news()
        
        if not news:
            logger.warning("❌ No news found today. Skipping post.")
            logger.info("This is not an error - sometimes there's simply no news available.")
            return 0
        
        logger.info(f"✅ News fetched: {news['headline'][:60]}...")
        logger.info(f"   Source: {news['source_name']}")
        
        # ========================================
        # Step 2: Generate engaging content
        # ========================================
        logger.info("")
        logger.info("✍️  Step 2: Generating engaging post content...")
        
        content = generate_engaging_post(
            headline=news["headline"],
            summary=news["summary"]
        )
        
        logger.info(f"✅ Content generated:")
        logger.info(f"   Post: {content['post_text'][:80]}...")
        logger.info(f"   Hashtags: {content['hashtags'][:60]}...")
        
        # ========================================
        # Step 3: Download football image
        # ========================================
        logger.info("")
        logger.info("📸 Step 3: Fetching football image...")
        
        image_path, photo_credit = get_football_image()
        
        logger.info(f"✅ Image downloaded: {image_path}")
        logger.info(f"   Credit: {photo_credit}")
        
        # ========================================
        # Step 4: Compose final caption
        # ========================================
        logger.info("")
        logger.info("📝 Step 4: Composing final caption...")
        
        # Add photo credit and source
        final_caption = (
            f"{content['caption']}\n\n"
            f"📷: {strip_all_urls(photo_credit)}\n"
            f"📰: {strip_all_urls(news['source_name'])}"
        )
        
        # Final safety check - strip any URLs
        final_caption = strip_all_urls(final_caption)
        
        logger.info("Final caption preview:")
        logger.info("-" * 40)
        for line in final_caption.split('\n'):
            logger.info(f"  {line}")
        logger.info("-" * 40)
        
        # ========================================
        # Step 5: Publish to Facebook
        # ========================================
        logger.info("")
        logger.info("📤 Step 5: Publishing to Facebook...")
        
        try:
            result = publish_photo_post(image_path, final_caption)
        except Exception as e:
            logger.warning(f"Photo post failed, trying text-only: {e}")
            result = publish_text_post(final_caption)
        
        # ========================================
        # Success!
        # ========================================
        logger.info("")
        logger.info("=" * 60)
        
        if result.get("dry_run"):
            logger.info("✅ DRY RUN COMPLETE - No post was actually made")
        else:
            logger.info(f"✅ Successfully posted to Facebook!")
            logger.info(f"   Post ID: {result['post_id']}")
        
        logger.info("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        return 1
        
    except Exception as e:
        logger.error("")
        logger.error("=" * 60)
        logger.error(f"❌ Critical error: {str(e)}")
        logger.error("=" * 60)
        
        # Log full traceback for debugging
        import traceback
        logger.debug(traceback.format_exc())
        
        return 1
        
    finally:
        # Cleanup temporary files
        if image_path:
            cleanup_temp_file(image_path)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
