"""
Image handling module.
OPTIMIZED FOR FREE MODE (Generator Only).
"""

import logging
from typing import Tuple
from .image_generator import create_pro_image

logger = logging.getLogger(__name__)

def get_football_image(headline: str = "Football Updates") -> Tuple[str, str]:
    """
    Always generates a professional graphic based on the headline.
    Ignores API keys since we are in Free Mode.
    """
    logger.info("🎨 Generating professional scoreboard graphic...")
    try:
        # Generate the image
        # We pass "Global Football" as the source text at the bottom
        path = create_pro_image(headline, "Global Football Updates")
        return path, "Generated Graphic"
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        # Return a failsafe if something breaks (should not happen)
        raise e
