"""
Configuration settings for Sports Prediction Bot
"""
import os

# =============================================================================
# API CONFIGURATION
# =============================================================================
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'odds-api1.p.rapidapi.com'
# FIX: Point to root, we will append /v4/sports/... in the code
API_BASE_URL = 'https://odds-api1.p.rapidapi.com'

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
# LEAGUE KEYS (For Fallback)
# =============================================================================
# Since 'upcoming' is 404ing, we will check these keys in order
LEAGUE_KEYS = [
    'soccer_epl',             # Premier League
    'soccer_spain_la_liga',   # La Liga
    'soccer_uefa_champs_league', # Champions League
    'soccer_germany_bundesliga', # Bundesliga
    'soccer_italy_serie_a',   # Serie A
    'soccer_france_ligue_one', # Ligue 1
    'soccer_usa_mls',         # MLS (Good for evenings)
    'soccer_brazil_campeonato' # Brasileirao
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
