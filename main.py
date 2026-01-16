#!/usr/bin/env python3
"""
Main orchestrator.
Updates: Passes League Name to Content Generator for correct hashtags.
"""

import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.news_fetcher import fetch_football_news
from src.content_generator import generate_engaging_post
from src.image_handler import get_football_image
from src.facebook_publisher import publish_photo_post
from src.utils import setup_logging

logger = setup_logging()

def cleanup_temp_file(file_path: str) -> None:
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass

def main() -> int:
    logger.info("🚀 Football News Bot Starting (EUROPE ONLY MODE)")
    image_path = None
    
    try:
        # 1. Fetch News
        news = fetch_football_news()
        if not news:
            logger.warning("❌ No Top European matches found (checked +/- 3 days). Exiting.")
            return 0
        
        logger.info(f"✅ Found: {news['headline']} ({news['source_name']})")
        
        # 2. Generate Content (Pass League Name for better hashtags)
        content = generate_engaging_post(
            headline=news["headline"], 
            summary=news["summary"],
            league_name=news["source_name"]
        )
        
        # 3. Get Image
        image_path, _ = get_football_image(
            headline=news["headline"], 
            source_name=news["source_name"]
        )
        
        # 4. Publish
        logger.info("📤 Publishing to Facebook...")
        result = publish_photo_post(image_path, content['caption'])
        
        logger.info(f"✅ Success! Post ID: {result['post_id']}")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Critical error: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
        
    finally:
        if image_path:
            cleanup_temp_file(image_path)

if __name__ == "__main__":
    sys.exit(main())
