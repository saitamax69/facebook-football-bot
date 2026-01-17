"""
Configuration settings for Sports Prediction Bot
"""
import os

# =============================================================================
# API CONFIGURATION
# =============================================================================
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'odds-api1.p.rapidapi.com'
API_BASE_URL = 'https://odds-api1.p.rapidapi.com'

# =============================================================================
# FACEBOOK CONFIGURATION
# =============================================================================
FB_PAGE_ID = os.environ.get('FB_PAGE_ID')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_GRAPH_URL = 'https://graph.facebook.com/v18.0'

# =============================================================================
# TELEGRAM LINK - INCLUDED IN EVERY POST
# =============================================================================
TELEGRAM_LINK = 'https://t.me/+xAQ3DCVJa8A2ZmY8'

# =============================================================================
# RISK LEVELS
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
# ALL TOP LEAGUES AND CUPS
# =============================================================================
PRIORITY_LEAGUES = [
    # ENGLAND
    'Premier League', 'Championship', 'League One', 'League Two',
    'FA Cup', 'EFL Cup', 'Carabao Cup', 'Community Shield',
    
    # SPAIN
    'La Liga', 'Segunda Division', 'Copa del Rey', 'Supercopa',
    
    # GERMANY
    'Bundesliga', '2. Bundesliga', 'DFB Pokal', 'DFL Supercup',
    
    # ITALY
    'Serie A', 'Serie B', 'Coppa Italia', 'Supercoppa Italiana',
    
    # FRANCE
    'Ligue 1', 'Ligue 2', 'Coupe de France', 'Trophee des Champions',
    
    # NETHERLANDS
    'Eredivisie', 'Eerste Divisie', 'KNVB Cup',
    
    # PORTUGAL
    'Primeira Liga', 'Liga Portugal', 'Taca de Portugal',
    
    # BELGIUM
    'Belgian Pro League', 'Jupiler Pro League', 'Belgian Cup',
    
    # TURKEY
    'Super Lig', 'Turkish Cup',
    
    # SCOTLAND
    'Scottish Premiership', 'Scottish Cup', 'Scottish League Cup',
    
    # OTHER EUROPE
    'Austrian Bundesliga', 'Swiss Super League', 'Greek Super League',
    'Russian Premier League', 'Ukrainian Premier League', 'Ekstraklasa',
    'Czech First League', 'Danish Superliga', 'Allsvenskan', 'Eliteserien',
    
    # UEFA
    'Champions League', 'UEFA Champions League',
    'Europa League', 'UEFA Europa League',
    'Conference League', 'UEFA Europa Conference League',
    'UEFA Super Cup',
    
    # INTERNATIONAL
    'World Cup', 'FIFA World Cup', 'World Cup Qualifiers',
    'Euro', 'European Championship', 'Euro Qualifiers',
    'UEFA Nations League', 'Nations League',
    'Copa America', 'Africa Cup of Nations', 'AFCON',
    'Asian Cup', 'Gold Cup', 'CONCACAF Gold Cup',
    
    # SOUTH AMERICA
    'Copa Libertadores', 'Copa Sudamericana',
    'Brasileirao', 'Campeonato Brasileiro', 'Copa do Brasil',
    'Argentine Primera Division', 'Liga Profesional', 'Copa Argentina',
    
    # NORTH AMERICA
    'MLS', 'Major League Soccer', 'Liga MX', 'US Open Cup',
    'CONCACAF Champions League',
    
    # ASIA
    'AFC Champions League', 'J1 League', 'K League 1',
    'Chinese Super League', 'Saudi Pro League', 'Roshn Saudi League',
    'Qatar Stars League', 'UAE Pro League', 'Indian Super League',
    
    # AFRICA
    'CAF Champions League', 'Egyptian Premier League',
    'South African Premier Division',
    
    # OCEANIA
    'A-League',
    
    # FRIENDLY
    'International Friendly', 'Club Friendly',
]

# =============================================================================
# HASHTAGS
# =============================================================================
HASHTAGS = {
    'SAFE': ['#SafeBet', '#LowRisk', '#EasyWin', '#BankBuilder', '#SureBet', '#FreeTips'],
    'MODERATE': ['#ValueBet', '#SmartBet', '#GoodOdds', '#FootballTips', '#FreePicks'],
    'RISKY': ['#HighOdds', '#JackpotBet', '#RiskyPick', '#BigOdds', '#Underdog'],
    'GENERAL': ['#Football', '#Soccer', '#SportsBetting', '#Tipster', '#BetOfTheDay', '#Predictions']
}

# =============================================================================
# DATA FILES
# =============================================================================
PREDICTIONS_FILE = 'data/predictions.json'
STATS_FILE = 'data/stats.json'
