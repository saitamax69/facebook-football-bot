"""
Post Generator for creating formatted Facebook posts.
Generates prediction and results posts with proper formatting.
"""

from datetime import datetime
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import TELEGRAM_LINK, HASHTAGS
except ImportError:
    from config import TELEGRAM_LINK, HASHTAGS


class PostGenerator:
    """
    Generator for creating formatted Facebook posts for predictions and results.
    """
    
    def __init__(self):
        """Initialize the post generator."""
        self.telegram_link = TELEGRAM_LINK
    
    def generate_safe_bet_post(self, match: Dict, analysis: Dict, post_number: int) -> str:
        """
        Generate a Safe Bet prediction post.
        
        Args:
            match: Match data dictionary
            analysis: Analysis data dictionary
            post_number: Post number (1 or 2)
            
        Returns:
            Formatted post string
        """
        hashtags = self._get_hashtags('SAFE', match['league'], 
                                       match['home_team'], match['away_team'])
        
        # Get bookmaker odds with fallbacks
        pinnacle = analysis.get('bookmaker_odds', {}).get('pinnacle', 'N/A')
        bet365 = analysis.get('bookmaker_odds', {}).get('bet365', 'N/A')
        betfair = analysis.get('bookmaker_odds', {}).get('betfair', 'N/A')
        
        # Format bookmaker odds
        if pinnacle == '0' or pinnacle == 0:
            pinnacle = 'N/A'
        if bet365 == '0' or bet365 == 0:
            bet365 = 'N/A'
        if betfair == '0' or betfair == 0:
            betfair = 'N/A'
        
        # Get odds display
        odds_display = analysis.get('odds_display', {})
        home_odds = odds_display.get('home', 'N/A')
        draw_odds = odds_display.get('draw', 'N/A')
        away_odds = odds_display.get('away', 'N/A')
        
        post = f"""🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

🔒 𝗦𝗔𝗙𝗘 𝗕𝗘𝗧 #{post_number} 🔒

━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 {match['league']}
📅 {match['date']} | ⏰ {match['time']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 {match['home_team']}
        ⚔️
✈️ {match['away_team']}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 𝗢𝗗𝗗𝗦 𝗖𝗢𝗠𝗣𝗔𝗥𝗜𝗦𝗢𝗡
┌─────────────────────────┐
│ 🏠 Home Win:  {home_odds:<8} │
│ 🤝 Draw:      {draw_odds:<8} │
│ ✈️ Away Win:  {away_odds:<8} │
└─────────────────────────┘

🏦 𝗕𝗢𝗢𝗞𝗠𝗔𝗞𝗘𝗥𝗦
├─ Pinnacle:  {pinnacle}
├─ Bet365:    {bet365}
└─ Betfair:   {betfair}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 𝗢𝗨𝗥 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 𝗣𝗜𝗖𝗞: {analysis['prediction']}
💰 𝗢𝗗𝗗𝗦: {analysis['odds']}
🎚️ 𝗖𝗢𝗡𝗙𝗜𝗗𝗘𝗡𝗖𝗘: 🟢🟢🟢🟢🟢 {analysis['confidence']}%

━━━━━━━━━━━━━━━━━━━━━━━━━

📈 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦
• {analysis['reasons'][0]}
• {analysis['reasons'][1]}
• {analysis['reasons'][2]}

━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 𝗥𝗜𝗦𝗞: 𝗟𝗢𝗪 🟢
💎 𝗧𝗬𝗣𝗘: 𝗦𝗔𝗙𝗘 𝗕𝗘𝗧

━━━━━━━━━━━━━━━━━━━━━━━━━

📲 𝗠𝗢𝗥𝗘 𝗙𝗥𝗘𝗘 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡𝗦 👇
🔗 {self.telegram_link}
🎁 We post more FREE predictions on Telegram daily!

🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

{hashtags}"""
        
        return post
    
    def generate_value_bet_post(self, match: Dict, analysis: Dict, post_number: int) -> str:
        """
        Generate a Value Bet prediction post.
        
        Args:
            match: Match data dictionary
            analysis: Analysis data dictionary
            post_number: Post number (3 or 4)
            
        Returns:
            Formatted post string
        """
        hashtags = self._get_hashtags('MODERATE', match['league'],
                                       match['home_team'], match['away_team'])
        
        # Get bookmaker odds with fallbacks
        pinnacle = analysis.get('bookmaker_odds', {}).get('pinnacle', 'N/A')
        bet365 = analysis.get('bookmaker_odds', {}).get('bet365', 'N/A')
        
        if pinnacle == '0' or pinnacle == 0:
            pinnacle = 'N/A'
        if bet365 == '0' or bet365 == 
