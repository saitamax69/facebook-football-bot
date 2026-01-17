"""
Configuration settings for Sports Prediction Bot
"""
import os

# =============================================================================
# API CONFIGURATION (ESPN - NO KEY REQUIRED)
# =============================================================================
# We keep these variables so the rest of the code doesn't break, 
# but they are not used for fetching data anymore.
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'not_needed')
RAPIDAPI_HOST = 'site.api.espn.com'
API_BASE_URL = 'https://site.api.espn.com/apis/site/v2/sports/soccer'

# =============================================================================
# FACEBOOK CONFIGURATION
# =============================================================================
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_GRAPH_URL = 'https://graph.facebook.com/v18.0'

# =============================================================================
# TELEGRAM
# =============================================================================
TELEGRAM_LINK = 'https://t.me/+xAQ3DCVJa8A2ZmY8'

# =============================================================================
# RISK LEVELS
# =============================================================================
RISK_LEVELS = {
    'SAFE': { 'min_odds': 1.20, 'max_odds': 1.55, 'min_confidence': 85, 'max_confidence': 95, 'emoji': '🟢' },
    'MODERATE': { 'min_odds': 1.60, 'max_odds': 2.20, 'min_confidence': 65, 'max_confidence': 80, 'emoji': '🟡' },
    'RISKY': { 'min_odds': 2.30, 'max_odds': 10.00, 'min_confidence': 45, 'max_confidence': 60, 'emoji': '🔴' }
}

# =============================================================================
# ESPN LEAGUE KEYS
# =============================================================================
# These are the codes ESPN uses for their public API
PRIORITY_LEAGUES = [
    'eng.1',          # Premier League
    'esp.1',          # La Liga
    'ger.1',          # Bundesliga
    'ita.1',          # Serie A
    'fra.1',          # Ligue 1
    'uefa.champions', # Champions League
    'usa.1',          # MLS
    'por.1',          # Portuguese Liga
    'ned.1'           # Eredivisie
]

# =============================================================================
# HASHTAGS
# =============================================================================
HASHTAGS = {
    'SAFE': ['#SafeBet', '#LowRisk', '#EasyWin', '#BankBuilder', '#SureBet', '#FreeTips'],
    'MODERATE': ['#ValueBet', '#SmartBet', '#GoodOdds', '#FootballTips', '#FreePicks'],
    'RISKY': ['#HighOdds', '#JackpotBet', '#RiskyPick', '#BigOdds', '#Underdog'],
    'GENERAL': ['#Football', '#Soccer', '#SportsBetting', '#Tipster', '#BetOfTheDay']
}

# =============================================================================
# DATA FILES
# =============================================================================
PREDICTIONS_FILE = 'data/predictions.json'
STATS_FILE = 'data/stats.json'
