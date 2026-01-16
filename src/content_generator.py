"""
Content generation module.
Smart Hashtags + Clean Formatting.
"""

import logging
import random

logger = logging.getLogger(__name__)

class ContentGenerator:
    def generate(self, headline: str, summary: str, league_name: str) -> dict:
        
        # 1. Generate Contextual Hashtags
        hashtags = "#Football #Soccer"
        
        # Add League Specific Tags
        l_lower = league_name.lower()
        if "premier" in l_lower: hashtags += " #PremierLeague #EPL #PL"
        elif "liga" in l_lower: hashtags += " #LaLiga #RealMadrid #Barcelona"
        elif "bundes" in l_lower: hashtags += " #Bundesliga"
        elif "serie" in l_lower: hashtags += " #SerieA"
        elif "champions" in l_lower: hashtags += " #UCL #ChampionsLeague"
        elif "europa" in l_lower: hashtags += " #UEL"
        
        # Add Team Tags (Basic Logic)
        if "man" in headline.lower(): hashtags += " #ManCity #ManUtd"
        if "arsenal" in headline.lower(): hashtags += " #Arsenal"
        if "liverpool" in headline.lower(): hashtags += " #LFC"
        if "real" in headline.lower(): hashtags += " #RealMadrid"
        if "barca" in headline.lower(): hashtags += " #FCBarcelona"
        
        # 2. Generate Caption Text
        is_result = any(char.isdigit() for char in headline) and "-" in headline
        
        if is_result:
            templates = [
                f"🚨 FINAL SCORE: {headline}\n\n{summary}\n\n👇 Who was your Man of the Match?",
                f"⚽ FULL TIME!\n\n{headline}\n\n🔥 What a game! Drop your thoughts below! 👇",
                f"🏆 RESULT UPDATE\n\n{headline}\n\nRate this performance 1-10! 👇"
            ]
            hashtags += " #Results #FullTime"
        else:
            templates = [
                f"📅 BIG MATCH COMING UP\n\n{headline}\n\n👇 Who are you backing to win?",
                f"⚽ MATCH PREVIEW\n\n{headline}\n\n🔮 Predict the score in the comments!",
                f"🔥 UPCOMING CLASH\n\n{headline}\n\nAre you ready for this one? 💪"
            ]
            hashtags += " #MatchDay"

        post_text = random.choice(templates)
        
        # Combine
        caption = f"{post_text}\n\n{hashtags}"
        
        return {
            "post_text": post_text,
            "hashtags": hashtags,
            "caption": caption
        }

# Update function signature to accept league_name
def generate_engaging_post(headline: str, summary: str, league_name: str = "Football") -> dict:
    generator = ContentGenerator()
    return generator.generate(headline, summary, league_name)
