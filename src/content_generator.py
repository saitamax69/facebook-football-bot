"""
Content generation module.
OPTIMIZED FOR FREE MODE (No OpenAI).
"""

import logging
import random
from .utils import strip_all_urls

logger = logging.getLogger(__name__)

class ContentGenerator:
    def generate(self, headline: str, summary: str) -> dict:
        """
        Generate post content using smart templates.
        """
        headline = strip_all_urls(headline)
        summary = strip_all_urls(summary)
        
        # Detect if it's a Score or a Preview
        is_result = any(char.isdigit() for char in headline) and "-" in headline
        
        if is_result:
            # Result Templates
            templates = [
                f"⚽ FULL TIME!\n\n{headline}\n\n{summary}\n\n👇 What did you think of the performance?",
                f"🔥 MATCH RESULT\n\n{headline}\n\n{summary}\n\n💬 Drop your reaction below!",
                f"🏆 FINAL SCORE\n\n{headline}\n\n{summary}\n\n⭐ Who was your Man of the Match?"
            ]
            hashtags = "#Football #Soccer #MatchDay #Results #FullTime"
        else:
            # News/Preview Templates
            templates = [
                f"📅 MATCH PREVIEW\n\n{headline}\n\n{summary}\n\n👇 Who do you think will win?",
                f"⚽ UPCOMING MATCH\n\n{headline}\n\n{summary}\n\n🔮 Predict the score in the comments!",
                f"📢 FOOTBALL NEWS\n\n{headline}\n\n{summary}\n\n🔥 Are you ready for this match?"
            ]
            hashtags = "#Football #Soccer #UpcomingMatch #Predictions"

        post_text = random.choice(templates)
        caption = f"{post_text}\n\n{hashtags}"
        
        return {
            "post_text": post_text,
            "hashtags": hashtags,
            "caption": caption
        }

def generate_engaging_post(headline: str, summary: str) -> dict:
    generator = ContentGenerator()
    return generator.generate(headline, summary)
