"""
Configuration settings for the Sports Prediction Bot
All environment variables and constants are defined here.
"""

import os

# =============================================================================
# API Configuration
# =============================================================================

RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'odds-api1.p.rapidapi.com'
API_BASE_URL = 'https://odds-api1.p.rapidapi.com'

# =============================================================================
# Facebook Configuration
# =============================================================================

FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_GRAPH_URL = 'https://graph.facebook.com/v18.0'

# =============================================================================
# Telegram Configuration
# =============================================================================

TELEGRAM_LINK = 'https://t.me/+xAQ3DCVJa8A2ZmY8'

# =============================================================================
# Risk Level Configuration
# =============================================================================

RISK_LEVELS = {
    'SAFE': {
        'min_odds': 1.20,
        'max_odds': 1.55,
        'min_confidence': 85,
        'max_confidence': 95,
        'emoji': '🟢',
        'name': 'SAFE BET'
    },
    'MODERATE': {
        'min_odds': 1.60,
        'max_odds': 2.20,
        'min_confidence': 65,
        'max_confidence': 80,
        'emoji': '🟡',
        'name': 'VALUE BET'
    },
    'RISKY': {
        'min_odds': 2.30,
        'max_odds': 10.00,
        'min_confidence': 45,
        'max_confidence': 60,
        'emoji': '🔴',
        'name': 'HIGH ODDS'
    }
}

# =============================================================================
# Priority Leagues (fetch only from these)
# =============================================================================

PRIORITY_LEAGUES = [
    'Premier League',
    'La Liga',
    'Serie A',
    'Bundesliga',
    'Ligue 1',
    'Champions League',
    'Europa League',
    'Championship',
    'Eredivisie',
    'Primeira Liga',
    'English Premier League',
    'Spanish La Liga',
    'Italian Serie A',
    'German Bundesliga',
    'French Ligue 1',
    'UEFA Champions League',
    'UEFA Europa League',
    'English Championship',
    'Dutch Eredivisie',
    'Portuguese Primeira Liga',
    'MLS',
    'Scottish Premiership',
    'Belgian Pro League',
    'Turkish Super Lig',
    'Russian Premier League'
]

# =============================================================================
# League Name Normalization Map
# =============================================================================

LEAGUE_NORMALIZE = {
    'english premier league': 'Premier League',
    'epl': 'Premier League',
    'spanish la liga': 'La Liga',
    'italian serie a': 'Serie A',
    'german bundesliga': 'Bundesliga',
    'french ligue 1': 'Ligue 1',
    'uefa champions league': 'Champions League',
    'ucl': 'Champions League',
    'uefa europa league': 'Europa League',
    'uel': 'Europa League',
    'english championship': 'Championship',
    'dutch eredivisie': 'Eredivisie',
    'portuguese primeira liga': 'Primeira Liga'
}

# =============================================================================
# Hashtags by risk level
# =============================================================================

HASHTAGS = {
    'SAFE': [
        '#SafeBet', '#LowRisk', '#EasyWin', '#BankBuilder', 
        '#SureBet', '#FreeTips', '#BettingTips'
    ],
    'MODERATE': [
        '#ValueBet', '#SmartBet', '#GoodOdds', '#FootballTips', 
        '#FreePicks', '#BettingPicks'
    ],
    'RISKY': [
        '#HighOdds', '#JackpotBet', '#RiskyPick', '#BigOdds', 
        '#Underdog', '#ValueBets'
    ],
    'GENERAL': [
        '#Football', '#Soccer', '#SportsBetting', '#Tipster', 
        '#BetOfTheDay', '#Predictions'
    ]
}

# =============================================================================
# Data file paths
# =============================================================================

PREDICTIONS_FILE = 'data/predictions.json'
STATS_FILE = 'data/stats.json'

# =============================================================================
# Supported Markets
# =============================================================================

MARKETS = {
    '1X2': ['Home Win', 'Draw', 'Away Win'],
    'DOUBLE_CHANCE': ['Home or Draw', 'Away or Draw', 'Home or Away'],
    'OVER_UNDER': ['Over 2.5 Goals', 'Under 2.5 Goals', 'Over 1.5 Goals', 'Under 1.5 Goals'],
    'BTTS': ['BTTS Yes', 'BTTS No']
}

# =============================================================================
# Bookmaker Priority (for display)
# =============================================================================

BOOKMAKER_PRIORITY = [
    'pinnacle',
    'bet365',
    'betfair',
    '1xbet',
    'william hill',
    'unibet',
    'betway',
    'bwin'
]
