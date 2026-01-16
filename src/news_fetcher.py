"""
News fetching module.
HYBRID MODE: Tries 'Big Leagues' first, then falls back to 'Any Match'.
"""

import logging
from datetime import datetime, timedelta
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)

class NewsFetcher:
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # Text-based matching is safer than IDs for the Free Tier
    TOP_LEAGUE_NAMES = [
        "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", 
        "Champions League", "Europa League", "FA Cup", "Copa del Rey"
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballBot/1.0"})
    
    @api_retry
    def fetch(self):
        logger.info("🔍 Hunting for Football News...")
        
        # 1. Try Strict Search (Top Leagues Only)
        logger.info("--- Phase 1: Checking Top Leagues ---")
        news = self._scan_days(strict_mode=True)
        if news: 
            return news
            
        # 2. Try Loose Search (Any Soccer Match)
        logger.info("⚠️ No Top Tier matches found. Switching to Fallback Mode.")
        logger.info("--- Phase 2: Grab ANY Match ---")
        news = self._scan_days(strict_mode=False)
        if news:
            return news
            
        logger.warning("❌ Absolutely no matches found (API might be down or date is wrong).")
        return None

    def _scan_days(self, strict_mode):
        # Check Yesterday (Results), Today (Live), Tomorrow (Upcoming)
        offsets = [-1, 0, 1]
        
        for offset in offsets:
            check_date = (datetime.utcnow() + timedelta(days=offset)).strftime("%Y-%m-%d")
            logger.info(f"Checking {check_date} (Strict: {strict_mode})...")
            
            news = self._check_date(check_date, is_result=(offset < 0), strict_mode=strict_mode)
            if news:
                logger.info(f"✅ Found news: {news['headline']}")
                return news
        return None

    def _check_date(self, date_str, is_result, strict_mode):
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
                league = event.get("strLeague", "Football Match")
                home = event.get("strHomeTeam", "")
                away = event.get("strAwayTeam", "")
                
                # Skip invalid data
                if not home or not away: continue
                
                # --- FILTERING LOGIC ---
                if strict_mode:
                    # Only accept if league name contains a Top League keyword
                    is_top = any(l.lower() in league.lower() for l in self.TOP_LEAGUE_NAMES)
                    if not is_top:
                        continue
                # -----------------------

                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                
                # Format the news
                if is_result:
                    if home_score is not None and away_score is not None:
                        # Found a Result
                        headline = f"{home} {home_score}-{away_score} {away}"
                        summary = f"FULL TIME: {home} vs {away} in the {league} ended {home_score}-{away_score}."
                        return {"headline": headline, "summary": summary, "source_name": league}
                else:
                    # Found Upcoming
                    headline = f"{home} vs {away}"
                    summary = f"UPCOMING: {home} takes on {away} in the {league}."
                    return {"headline": headline, "summary": summary, "source_name": league}
            
            return None

        except Exception as e:
            logger.error(f"Error checking date {date_str}: {e}")
            return None

def fetch_football_news():
    return NewsFetcher().fetch()
