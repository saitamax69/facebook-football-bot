"""
News fetching module.
STRICT FILTER: ONLY TOP 5 LEAGUES + UCL.
"""

import logging
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)

class NewsFetcher:
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # IDs for TheSportsDB:
    # 4328: Premier League, 4335: La Liga, 4331: Bundesliga, 
    # 4332: Serie A, 4334: Ligue 1, 4480: Champions League
    TOP_LEAGUE_IDS = ["4328", "4335", "4331", "4332", "4334", "4480"]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballBot/1.0"})
    
    @api_retry
    def fetch(self):
        logger.info("Fetching ONLY Top League news...")
        
        # 1. Check Yesterday (For Results - Best Content)
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        news = self._get_best_match(yesterday, is_result=True)
        if news: return news
        
        # 2. Check Today (Live/Upcoming)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        news = self._get_best_match(today, is_result=False)
        if news: return news
        
        # 3. Check Tomorrow (Previews)
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        news = self._get_best_match(tomorrow, is_result=False)
        if news: return news
            
        logger.warning("No Top League matches found in +/- 1 day window.")
        return None

    def _get_best_match(self, date_str, is_result):
        try:
            response = self.session.get(
                f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                params={"d": date_str, "s": "Soccer"},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()
            events = data.get("events")
            
            if not events: return None
            
            # STRICT FILTER: Only keep events from our Top League list
            top_events = [e for e in events if e.get("idLeague") in self.TOP_LEAGUE_IDS]
            
            if not top_events:
                return None
            
            # Pick the best one (prioritize matches with scores if looking for results)
            for event in top_events:
                home = event.get("strHomeTeam", "")
                away = event.get("strAwayTeam", "")
                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                league = event.get("strLeague", "Football")
                
                if not home or not away: continue
                
                # Format Data
                if home_score is not None and away_score is not None:
                    # It's a Result
                    headline = f"{home} {home_score}-{away_score} {away}"
                    summary = f"FULL TIME in the {league}. {home} vs {away} ended {home_score}-{away_score}."
                    return {"headline": headline, "summary": summary, "source_name": league}
                
                elif not is_result:
                    # It's a Preview
                    headline = f"{home} vs {away}"
                    summary = f"BIG MATCH PREVIEW: {home} take on {away} in the {league}."
                    return {"headline": headline, "summary": summary, "source_name": league}
            
            return None

        except Exception as e:
            logger.error(f"Error fetching: {e}")
            return None

def fetch_football_news():
    return NewsFetcher().fetch()
