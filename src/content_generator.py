"""
Content generation module.
Free Mode - Template Based.
"""

import logging
import random

logger = logging.getLogger(__name__)

class ContentGenerator:
    def generate(self, headline: str, summary: str) -> dict:
        
        # Detect context
        is_result = any(char.isdigit() for char in headline) and "-" in headline
        
        if is_result:
            # It's a score (e.g., Man City 3-1 Man Utd)
            templates = [
                f"🚨 FINAL SCORE UPDATE\n\n{headline}\n\nWhat a game! 🔥\n\n👇 Drop your thoughts in the comments!",
                f"⚽ FULL TIME\n\n{headline}\n\nWho was your Man of the Match? ⭐",
                f"🔥 MATCH RESULT\n\n{headline}\n\nRate this match from 1-10! 👇"
            ]
            hashtags = "#Football #Soccer #PremierLeague #UCL #Results"
        else:
            # It's a preview (e.g. Man City vs Man Utd)
            templates = [
                f"📅 BIG MATCH COMING UP\n\n{headline}\n\n👇 Who are you backing to win?",
                f"⚽ MATCHDAY\n\n{headline}\n\n🔮 Predict the score below!",
                f"🔥 UPCOMING CLASH\n\n{headline}\n\nAre you ready? 💪"
            ]
            hashtags = "#Football #Soccer #MatchDay #Predictions"

        post_text = random.choice(templates)
        
        # Simple clean caption
        caption = f"{post_text}\n\n{hashtags}"
        
        return {
            "post_text": post_text,
            "hashtags": hashtags,
            "caption": caption
        }

def generate_engaging_post(headline: str, summary: str) -> dict:
    generator = ContentGenerator()
    return generator.generate(headline, summary)
