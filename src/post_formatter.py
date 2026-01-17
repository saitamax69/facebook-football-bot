"""
🏆 Sports Prediction Bot - Post Formatter
==========================================

Formats predictions into beautiful Facebook posts using templates.
"""

from datetime import datetime, date
from typing import List, Dict, Optional
import json
import random

from src.config import (
    TELEGRAM_LINK, HASHTAGS, RISK_LEVELS,
    logger
)
from src.match_analyzer import MatchAnalysis
from src.database import Prediction, DailyStats


# ═══════════════════════════════════════════════════════════════════
# 🎨 UNICODE TEXT HELPERS
# ═══════════════════════════════════════════════════════════════════

def to_bold_unicode(text: str) -> str:
    """Convert text to bold unicode characters"""
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    
    result = ""
    for char in text:
        idx = normal.find(char)
        if idx != -1:
            result += bold[idx]
        else:
            result += char
    return result


# ═══════════════════════════════════════════════════════════════════
# 📝 POST FORMATTER CLASS
# ═══════════════════════════════════════════════════════════════════

class PostFormatter:
    """
    Formats predictions into beautiful Facebook posts.
    Uses predefined templates with dynamic data.
    """
    
    def __init__(self):
        """Initialize the formatter"""
        logger.info("📝 Post Formatter initialized")
    
    def _get_confidence_bar(self, risk_level: str, confidence: int) -> str:
        """Generate visual confidence bar"""
        if risk_level == 'SAFE':
            filled = '🟢'
            empty = '⚪'
            count = 5
        elif risk_level == 'VALUE':
            filled = '🟡'
            empty = '⚪'
            count = 4
        else:
            filled = '🔴'
            empty = '⚪'
            count = 3
        
        return filled * count + empty * (5 - count)
    
    def _format_datetime(self, fixture: Dict) -> tuple:
        """Extract and format date and time from fixture"""
        commence_time = fixture.get('commence_time', '')
        
        try:
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            date_str = dt.strftime('%d %B %Y')
            time_str = dt.strftime('%H:%M')
            return date_str, time_str
        except (ValueError, TypeError):
            return date.today().strftime('%d %B %Y'), '15:00'
    
    def _get_hashtags(self, analysis: MatchAnalysis, risk_level: str) -> str:
        """Generate hashtags for post"""
        tags = []
        
        # Add general tags
        tags.extend(random.sample(HASHTAGS['GENERAL'], 3))
        
        # Add risk-specific tags
        if risk_level in HASHTAGS:
            tags.extend(random.sample(HASHTAGS[risk_level], 2))
        
        # Add football tags
        tags.extend(random.sample(HASHTAGS['FOOTBALL'], 2))
        
        # Add team-specific tags
        home_team = analysis.fixture.get('home_team', '').replace(' ', '')
        away_team = analysis.fixture.get('away_team', '').replace(' ', '')
        
        if home_team:
            tags.append(f"#{home_team[:15]}")
        if away_team:
            tags.append(f"#{away_team[:15]}")
        
        # Add league tag
        league = analysis.fixture.get('league_name', '').replace(' ', '')
        if league:
            tags.append(f"#{league[:15]}")
        
        return ' '.join(tags[:12])
    
    def _get_bookmaker_odds(self, analysis: MatchAnalysis) -> tuple:
        """Get Pinnacle and Bet365 odds"""
        specific = analysis.bookmaker_odds
        
        p_odds = specific.get('pinnacle', {}).get('home', analysis.home_odds)
        b_odds = specific.get('bet365', {}).get('home', analysis.home_odds)
        
        return f"{p_odds:.2f}" if p_odds else "N/A", f"{b_odds:.2f}" if b_odds else "N/A"
    
    # ═══════════════════════════════════════════════════════════════
    # 🟢 SAFE BET TEMPLATE
    # ═══════════════════════════════════════════════════════════════
    
    def format_safe_bet(
        self,
        analysis: MatchAnalysis,
        post_number: int
    ) -> str:
        """
        Format a safe bet post.
        
        Args:
            analysis: Match analysis data
            post_number: Post number (1 or 2)
            
        Returns:
            Formatted post string
        """
        fixture = analysis.fixture
        date_str, time_str = self._format_datetime(fixture)
        p_odds, b_odds = self._get_bookmaker_odds(analysis)
        hashtags = self._get_hashtags(analysis, 'SAFE')
        conf_bar = self._get_confidence_bar('SAFE', analysis.confidence)
        
        post = f"""🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

🔒 {to_bold_unicode('SAFE BET')} #{post_number} 🔒

━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 {fixture.get('league_name', 'Football')}
📅 {date_str} | ⏰ {time_str}

━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 {fixture.get('home_team', 'Home')}
        ⚔️
✈️ {fixture.get('away_team', 'Away')}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 {to_bold_unicode('ODDS')}
│ 🏠 Home:  {analysis.home_odds:.2f}
│ 🤝 Draw:  {analysis.draw_odds:.2f}
│ ✈️ Away:  {analysis.away_odds:.2f}

🏦 {to_bold_unicode('BOOKIES')}
Pinnacle: {p_odds} │ Bet365: {b_odds}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 {to_bold_unicode('OUR PICK')}

✅ {to_bold_unicode('PREDICTION')}: {analysis.prediction}
💰 {to_bold_unicode('ODDS')}: {analysis.selected_odds:.2f}
🎚️ {to_bold_unicode('CONFIDENCE')}: {conf_bar} {analysis.confidence}%

━━━━━━━━━━━━━━━━━━━━━━━━━

📈 {to_bold_unicode('WHY THIS PICK?')}
• {analysis.analysis_points[0]}
• {analysis.analysis_points[1]}
• {analysis.analysis_points[2]}

━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 {to_bold_unicode('RISK')}: {to_bold_unicode('LOW')} 🟢
💎 {to_bold_unicode('TYPE')}: {to_bold_unicode('SAFE BET')}

━━━━━━━━━━━━━━━━━━━━━━━━━

📲 {to_bold_unicode('MORE FREE TIPS DAILY')} 👇
🔗 {TELEGRAM_LINK}
🎁 Join us for EXCLUSIVE predictions!

🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

{hashtags}"""
        
        return post
    
    # ═══════════════════════════════════════════════════════════════
    # 🟡 VALUE BET TEMPLATE
    # ═══════════════════════
