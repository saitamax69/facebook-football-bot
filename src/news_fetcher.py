"""
News fetching module.
SMART HUNTER: Scans 7 days window for Top Leagues OR Big Teams.
"""

import logging
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)

class NewsFetcher:
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # 1. TOP LEAGUES (EPL, La Liga, Bundesliga, Serie A, Ligue 1, UCL)
    TOP_LEAGUE_IDS = ["4328", "4335", "4331", "4332", "4334", "4480"]
    
    # 2. BIG TEAMS (Keywords to catch Cup games: FA Cup, Copa del Rey, etc.)
    BIG_TEAMS = [
        "Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Man Utd", "Newcastle", # England
        "Real Madrid", "Barcelona", "Girona", "Atlético", # Spain
        "Leverkusen", "Bayern", "Dortmund", # Germany
        "Inter", "Milan", "Juventus", "Napoli", "Roma", # Italy
        "PSG", # France
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballBot/1.0"})
    
    @api_retry
    def fetch(self):
        logger.info("Hunting for BIG Football News (7-Day Scan)...")
        
        # Priority Order: 
        # 1. Yesterday (Result) -> 2. Today (Live) -> 3. Tomorrow (Hype)
        # 4. 2 Days Ago (Recap) -> 5. 2 Days Future -> 6. 3 Days Ago -> 7. 3 Days Future
        offsets = [-1, 0, 1, -2, 2, -3, 3]
        
        for offset in offsets:
            check_date = (datetime.utcnow() + timedelta(days=offset)).strftime("%Y-%m-%d")
            logger.info(f"Checking {check_date}...")
            
            news = self._check_date(check_date, is_result=(offset < 0))
            if news:
                logger.info(f"✅ Found news from {check_date}!")
                return news
            
        logger.warning("❌ No big matches found in the last/next 3 days.")
        return None

    def _check_date(self, date_str, is_result):
        try:
            response = self.session.get(
                f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                params={"d": date_str, "s": "Soccer"},
                timeout=10
            )
            data = response.json()
            events = data.get("events")
            
            if not events: return None
            
            # Filter Logic
            for event in events:
                league_id = event.get("idLeague")
                home = event.get("strHomeTeam", "")
                away = event.get("strAwayTeam", "")
                league = event.get("strLeague", "Football")
                
                # CHECK 1: Is it a Top League?
                is_top_league = league_id in self.TOP_LEAGUE_IDS
                
                # CHECK 2: Is a Big Team playing? (Even in a Cup match)
                is_big_team = any(team in home for team in self.BIG_TEAMS) or \
                              any(team in away for team in self.BIG_TEAMS)
                
                if not (is_top_league or is_big_team):
                    continue
                
                # We found a relevant match!
                
                # If checking past dates, strictly look for finished games
                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                
                if is_result:
                    if home_score is not None and away_score is not None:
                        # Found a Big Result
                        headline = f"{home} {home_score}-{away_score} {away}"
                        summary = f"FULL TIME: {home} vs {away} in the {league} ended {home_score}-{away_score}."
                        return {"headline": headline, "summary": summary, "source_name": league}
                else:
                    # Found a Big Upcoming Game
                    headline = f"{home} vs {away}"
                    summary = f"UPCOMING BIG MATCH: {home} take on {away} in the {league}."
                    return {"headline": headline, "summary": summary, "source_name": league}
            
            return None

        except Exception as e:
            logger.error(f"Error checking date {date_str}: {e}")
            return None

def fetch_football_news():
    return NewsFetcher().fetch()
