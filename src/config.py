"""
Configuration settings for Sports Prediction Bot
"""
import os

# =============================================================================
# API CONFIGURATION
# =============================================================================
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'odds-api1.p.rapidapi.com'

# CRITICAL FIX: Updated to V4 API URL
API_BASE_URL = 'https://odds-api1.p.rapidapi.com/v4/sports'

# =============================================================================
# FACEBOOK CONFIGURATION
# =============================================================================
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_GRAPH_URL = 'https://graph.facebook.com/v18.0'

# =============================================================================
# TELEGRAM LINK
# =============================================================================
TELEGRAM_LINK = 'https://t.me/+xAQ3DCVJa8A2ZmY8'

# =============================================================================
# RISK LEVELS
# =============================================================================
RISK_LEVELS = {
    'SAFE': { 'min_odds': 1.20, 'max_odds': 1.55, 'min_confidence': 85, 'max_confidence': 95, 'emoji': '🟢', 'name': 'SAFE BET' },
    'MODERATE': { 'min_odds': 1.60, 'max_odds': 2.20, 'min_confidence': 65, 'max_confidence': 80, 'emoji': '🟡', 'name': 'VALUE BET' },
    'RISKY': { 'min_odds': 2.30, 'max_odds': 10.00, 'min_confidence': 45, 'max_confidence': 60, 'emoji': '🔴', 'name': 'HIGH ODDS' }
}

# =============================================================================
# LEAGUE KEYS (API Specific Keys)
# =============================================================================
# This maps readable names to the specific keys required by The Odds API
LEAGUE_KEYS = {
    'Premier League': 'soccer_epl',
    'Championship': 'soccer_efl_champ',
    'La Liga': 'soccer_spain_la_liga',
    'Bundesliga': 'soccer_germany_bundesliga',
    'Serie A': 'soccer_italy_serie_a',
    'Ligue 1': 'soccer_france_ligue_one',
    'Eredivisie': 'soccer_netherlands_eredivisie',
    'Primeira Liga': 'soccer_portugal_primeira_liga',
    'Champions League': 'soccer_uefa_champs_league',
    'Europa League': 'soccer_uefa_europa_league',
    'MLS': 'soccer_usa_mls',
    'Brasileirao': 'soccer_brazil_campeonato',
    'Super Lig': 'soccer_turkey_super_lig',
    'A-League': 'soccer_australia_aleague'
}

# Priority list for filtering
PRIORITY_LEAGUES = list(LEAGUE_KEYS.keys())

# =============================================================================
# HASHTAGS
# =============================================================================
HASHTAGS = {
    'SAFE': ['#SafeBet', '#LowRisk', '#EasyWin', '#BankBuilder', '#SureBet'],
    'MODERATE': ['#ValueBet', '#SmartBet', '#GoodOdds', '#FootballTips'],
    'RISKY': ['#HighOdds', '#JackpotBet', '#RiskyPick', '#BigOdds', '#Underdog'],
    'GENERAL': ['#Football', '#Soccer', '#SportsBetting', '#Tipster', '#Predictions']
}

# =============================================================================
# DATA FILES
# =============================================================================
PREDICTIONS_FILE = 'data/predictions.json'
STATS_FILE = 'data/stats.json'
