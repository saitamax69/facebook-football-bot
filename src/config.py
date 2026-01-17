"""
Configuration settings for Sports Prediction Bot
"""
import os

# =============================================================================
# API CONFIGURATION (UPDATED FOR V4)
# =============================================================================
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'odds-api1.p.rapidapi.com'
# IMPORTANT: This is the correct V4 base URL structure for RapidAPI
API_BASE_URL = 'https://odds-api1.p.rapidapi.com/v4/sports'

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
# PRIORITY LEAGUES (For display/reference)
# =============================================================================
PRIORITY_LEAGUES = [
    'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
    'Eredivisie', 'Primeira Liga', 'Champions League', 'Europa League',
    'Championship', 'Super Lig', 'Scottish Premiership', 'Belgian Pro League',
    'MLS', 'Brasileirao', 'Saudi Pro League', 'A-League', 'J1 League'
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
