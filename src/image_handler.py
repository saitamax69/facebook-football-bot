"""
Image handling module.
OPTIMIZED FOR FREE MODE (Generator Only).
"""

import logging
from typing import Tuple
from .image_generator import create_pro_image

logger = logging.getLogger(__name__)

def get_football_image(headline: str = "Football Updates", source_name: str = "Football News") -> Tuple[str, str]:
    """
    Always generates a professional graphic based on the headline.
    Ignores API keys since we are in Free Mode.
    """
    logger.info("🎨 Generating professional scoreboard graphic...")
    try:
        # Generate the image
        # We pass the league name (source_name) to the generator
        path = create_pro_image(headline, source_name)
        return path, "Generated Graphic"
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        # Re-raise to trigger error logs if something is truly broken
        raise e
