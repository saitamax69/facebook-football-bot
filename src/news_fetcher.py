"""
News fetching module.
STRICT EURO MODE: Scans 7 days. Rejects everything except Top 5 Leagues + Europe.
"""

import logging
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)

class NewsFetcher:
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # STRICT WHITELIST. If it's not here, we don't want it.
    EURO_LEAGUES = [
        "English Premier League", 
        "Spanish La Liga", 
        "German Bundesliga", 
        "Italian Serie A", 
        "French Ligue 1", 
        "UEFA Champions League", 
        "UEFA Europa League"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballBot/1.0"})
    
    @api_retry
    def fetch(self):
        logger.info("🇪🇺 Hunting for TOP EUROPEAN News (7-Day Scan)...")
        
        # Priority: Yesterday -> Today -> Tomorrow -> 2 Days Ago -> 2 Days Future...
        # We search specifically for a "Big Match" within a week range.
        offsets = [-1, 0, 1, -2, 2, -3, 3]
        
        for offset in offsets:
            check_date = (datetime.utcnow() + timedelta(days=offset)).strftime("%Y-%m-%d")
            is_result = offset < 0
            
            logger.info(f"Scanning {check_date} for Top Euro Matches...")
            
            news = self._check_date(check_date, is_result)
            if news:
                logger.info(f"✅ Found Top Euro Match: {news['headline']}")
                return news
            
        logger.warning("❌ No Top European matches found in the 7-day window.")
        return None

    def _check_date(self, date_str, is_result):
        try:
            response = self.session.get(
                f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                params={"d": date_str, "s": "Soccer"},
                timeout=15
            )
            data = response.json()
            events = data.get("events")
            
            if not events: return None
            
            for event in events:
                league = event.get("strLeague", "")
                home = event.get("strHomeTeam", "")
                away = event.get("strAwayTeam", "")
                
                # --- THE STRICT FILTER ---
                # Check if the league matches our European whitelist
                # We use partial matching (e.g., "Premier League" matches "English Premier League")
                is_euro_top = any(l.lower() in league.lower() for l in self.EURO_LEAGUES) or \
                              "champions league" in league.lower()
                
                if not is_euro_top:
                    continue # Skip A-League, MLS, etc.
                # -------------------------

                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                
                # Logic to format the headline
                if is_result:
                    if home_score is not None and away_score is not None:
                        # Found a Result
                        headline = f"{home} {home_score}-{away_score} {away}"
                        summary = f"FULL TIME in the {league}.\n{home} vs {away} ended {home_score}-{away_score}."
                        return {"headline": headline, "summary": summary, "source_name": league}
                else:
                    # Found Upcoming
                    headline = f"{home} vs {away}"
                    summary = f"BIG MATCH PREVIEW: {home} take on {away} in the {league}."
                    return {"headline": headline, "summary": summary, "source_name": league}
            
            return None

        except Exception as e:
            logger.error(f"Error checking date {date_str}: {e}")
            return None

def fetch_football_news():
    return NewsFetcher().fetch()
