"""
News fetching module.
OPTIMIZED FOR FREE MODE (TheSportsDB).
"""

import logging
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)

class NewsFetcher:
    # Free API endpoint
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballBot/1.0"})
    
    @api_retry
    def fetch(self):
        """
        Fetch strictly from TheSportsDB (Free).
        """
        logger.info("Fetching events from TheSportsDB (Free Mode)...")
        
        # 1. Try Today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        data = self._get_events(today)
        
        # 2. If no events today, try Yesterday (for results)
        if not data:
            yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            data = self._get_events(yesterday)
            
        if not data:
            return None

        return data

    def _get_events(self, date_str):
        try:
            response = self.session.get(
                f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                params={"d": date_str, "s": "Soccer"},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            events = data.get("events")
            
            if not events:
                return None
            
            # Filter for a "Major" league if possible, or just take the first completed one
            # We prefer matches that have a score
            best_event = None
            
            for event in events:
                league = event.get("strLeague", "")
                home_team = event.get("strHomeTeam", "")
                away_team = event.get("strAwayTeam", "")
                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                
                if not home_team or not away_team:
                    continue

                # Clean strings
                home_team = strip_all_urls(home_team)
                away_team = strip_all_urls(away_team)
                
                # Format Headline Professionaly
                if home_score is not None and away_score is not None:
                    # Result: "Arsenal 2 - 1 Chelsea"
                    headline = f"{home_team} {home_score} - {away_score} {away_team}"
                    status = "FT" # Full Time
                    summary = f"FULL TIME in the {league}.\n{home_team} finishes with {home_score}, while {away_team} ends with {away_score}."
                    best_event = {"headline": headline, "summary": summary, "source_name": league, "status": status}
                    break # Stop at the first finished match (usually the most relevant)
                else:
                    # Upcoming: "Arsenal vs Chelsea"
                    headline = f"{home_team} vs {away_team}"
                    status = "UPCOMING"
                    summary = f"MATCH PREVIEW: {home_team} takes on {away_team} in the {league}."
                    # Keep searching for a finished match, but keep this as backup
                    if not best_event:
                        best_event = {"headline": headline, "summary": summary, "source_name": league, "status": status}

            return best_event

        except Exception as e:
            logger.error(f"SportsDB Error: {e}")
            return None

def fetch_football_news():
    fetcher = NewsFetcher()
    return fetcher.fetch()
