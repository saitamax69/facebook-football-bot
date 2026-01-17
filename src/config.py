"""
🏆 Sports Prediction Bot - Configuration Module
================================================

Loads environment variables and defines all configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import logging

# Load environment variables
load_dotenv()

# ═══════════════════════════════════════════════════════════════════
# 📁 PATH CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# 🔐 API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RapidAPIConfig:
    """RapidAPI Odds API Configuration"""
    key: str = field(default_factory=lambda: os.getenv("RAPIDAPI_KEY", ""))
    host: str = field(default_factory=lambda: os.getenv("RAPIDAPI_HOST", "odds-api1.p.rapidapi.com"))
    base_url: str = "https://odds-api1.p.rapidapi.com"
    monthly_limit: int = 200
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "x-rapidapi-key": self.key,
            "x-rapidapi-host": self.host
        }


@dataclass
class FacebookConfig:
    """Facebook Graph API Configuration"""
    page_id: str = field(default_factory=lambda: os.getenv("FB_PAGE_ID", ""))
    access_token: str = field(default_factory=lambda: os.getenv("FB_ACCESS_TOKEN", ""))
    api_version: str = "v18.0"
    
    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"
    
    @property
    def post_url(self) -> str:
        return f"{self.base_url}/{self.page_id}/feed"


# ═══════════════════════════════════════════════════════════════════
# 📊 RISK LEVEL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RiskLevel:
    """Configuration for each risk level"""
    name: str
    emoji: str
    color: str
    odds_min: float
    odds_max: float
    confidence_min: int
    confidence_max: int
    description: str


RISK_LEVELS = {
    "SAFE": RiskLevel(
        name="SAFE BET",
        emoji="🟢",
        color="green",
        odds_min=1.20,
        odds_max=1.60,
        confidence_min=85,
        confidence_max=95,
        description="Low risk, high probability"
    ),
    "VALUE": RiskLevel(
        name="VALUE BET",
        emoji="🟡",
        color="yellow",
        odds_min=1.65,
        odds_max=2.30,
        confidence_min=65,
        confidence_max=80,
        description="Medium risk, good value"
    ),
    "RISKY": RiskLevel(
        name="HIGH ODDS",
        emoji="🔴",
        color="red",
        odds_min=2.50,
        odds_max=5.00,
        confidence_min=45,
        confidence_max=60,
        description="High risk, high reward"
    )
}


# ═══════════════════════════════════════════════════════════════════
# 🕐 SCHEDULE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PostSchedule:
    """Single post schedule configuration"""
    time: str  # HH:MM format
    risk_level: str
    post_number: int
    job_id: str


POSTING_SCHEDULE: List[PostSchedule] = [
    PostSchedule(
        time=os.getenv("POST_TIME_1", "08:00"),
        risk_level="SAFE",
        post_number=1,
        job_id="safe_bet_1"
    ),
    PostSchedule(
        time=os.getenv("POST_TIME_2", "11:00"),
        risk_level="SAFE",
        post_number=2,
        job_id="safe_bet_2"
    ),
    PostSchedule(
        time=os.getenv("POST_TIME_3", "14:00"),
        risk_level="VALUE",
        post_number=3,
        job_id="value_bet_3"
    ),
    PostSchedule(
        time=os.getenv("POST_TIME_4", "17:00"),
        risk_level="VALUE",
        post_number=4,
        job_id="value_bet_4"
    ),
    PostSchedule(
        time=os.getenv("POST_TIME_5", "20:00"),
        risk_level="RISKY",
        post_number=5,
        job_id="risky_bet_5"
    ),
    PostSchedule(
        time=os.getenv("POST_TIME_RESULTS", "00:00"),
        risk_level="RESULTS",
        post_number=6,
        job_id="results_summary"
    ),
]


# ═══════════════════════════════════════════════════════════════════
# ⚽ SPORTS & LEAGUES CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

# Top leagues to focus on (avoid friendlies)
TOP_LEAGUES = {
    "soccer": [
        {"id": "soccer_epl", "name": "Premier League", "country": "England"},
        {"id": "soccer_spain_la_liga", "name": "La Liga", "country": "Spain"},
        {"id": "soccer_germany_bundesliga", "name": "Bundesliga", "country": "Germany"},
        {"id": "soccer_italy_serie_a", "name": "Serie A", "country": "Italy"},
        {"id": "soccer_france_ligue_one", "name": "Ligue 1", "country": "France"},
        {"id": "soccer_uefa_champs_league", "name": "Champions League", "country": "Europe"},
        {"id": "soccer_uefa_europa_league", "name": "Europa League", "country": "Europe"},
        {"id": "soccer_netherlands_eredivisie", "name": "Eredivisie", "country": "Netherlands"},
        {"id": "soccer_portugal_primeira_liga", "name": "Primeira Liga", "country": "Portugal"},
        {"id": "soccer_brazil_campeonato", "name": "Brasileirão", "country": "Brazil"},
    ]
}

# Preferred bookmakers for odds comparison
PREFERRED_BOOKMAKERS = ["pinnacle", "bet365", "williamhill", "unibet", "betfair"]


# ═══════════════════════════════════════════════════════════════════
# 🔗 SOCIAL LINKS
# ═══════════════════════════════════════════════════════════════════

TELEGRAM_LINK = os.getenv("TELEGRAM_LINK", "https://t.me/+xAQ3DCVJa8A2ZmY8")


# ═══════════════════════════════════════════════════════════════════
# 📊 DATABASE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/predictions.db")


# ═══════════════════════════════════════════════════════════════════
# 📝 LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "bot.log"


def setup_logging() -> logging.Logger:
    """Configure and return the main logger"""
    logger = logging.getLogger("sports_bot")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s │ %(levelname)-8s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s │ %(levelname)-8s │ %(name)s │ %(funcName)s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# ═══════════════════════════════════════════════════════════════════
# 🌍 TIMEZONE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

TIMEZONE = os.getenv("TIMEZONE", "UTC")


# ═══════════════════════════════════════════════════════════════════
# #️⃣ HASHTAG LIBRARY
# ═══════════════════════════════════════════════════════════════════

HASHTAGS = {
    "GENERAL": [
        "#FreeTips", "#BettingTips", "#SportsBetting", "#FreePicks",
        "#Predictions", "#Tipster", "#BetOfTheDay", "#DailyPicks"
    ],
    "SAFE": [
        "#SafeBet", "#LowRisk", "#EasyWin", "#BankBuilder", "#SureBet"
    ],
    "VALUE": [
        "#ValueBet", "#SmartBet", "#GoodOdds", "#ProfitPick"
    ],
    "RISKY": [
        "#HighOdds", "#JackpotBet", "#RiskyPick", "#BigOdds", "#Underdog"
    ],
    "FOOTBALL": [
        "#Football", "#Soccer", "#PremierLeague", "#LaLiga",
        "#SerieA", "#Bundesliga", "#ChampionsLeague", "#UCL"
    ],
    "RESULTS": [
        "#Winner", "#WeWin", "#CashOut", "#Profit", "#DailyResults"
    ]
}


# ═══════════════════════════════════════════════════════════════════
# ✅ CONFIGURATION VALIDATION
# ═══════════════════════════════════════════════════════════════════

def validate_config() -> Tuple[bool, List[str]]:
    """Validate all required configuration is present"""
    errors = []
    
    rapidapi = RapidAPIConfig()
    facebook = FacebookConfig()
    
    if not rapidapi.key:
        errors.append("RAPIDAPI_KEY is not set")
    if not facebook.page_id:
        errors.append("FB_PAGE_ID is not set")
    if not facebook.access_token:
        errors.append("FB_ACCESS_TOKEN is not set")
    
    return len(errors) == 0, errors


# Create singleton instances
rapidapi_config = RapidAPIConfig()
facebook_config = FacebookConfig()
logger = setup_logging()
