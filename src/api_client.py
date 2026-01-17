"""
🏆 Sports Prediction Bot - Odds API Client
============================================

Handles all interactions with the RapidAPI Odds API.
Includes rate limiting, caching, and error handling.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import time
import json

from src.config import rapidapi_config, TOP_LEAGUES, PREFERRED_BOOKMAKERS, logger
from src.database import db


# ═══════════════════════════════════════════════════════════════════
# 📡 ODDS API CLIENT
# ═══════════════════════════════════════════════════════════════════

class OddsAPIClient:
    """
    Client for interacting with the RapidAPI Odds API.
    Implements caching and rate limiting to stay under 200 requests/month.
    """
    
    def __init__(self):
        """Initialize the API client"""
        self.base_url = rapidapi_config.base_url
        self.headers = rapidapi_config.headers
        self.monthly_limit = rapidapi_config.monthly_limit
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info("📡 Odds API Client initialized")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within the monthly API limit"""
        usage = db.get_monthly_api_usage()
        remaining = self.monthly_limit - usage
        
        if remaining <= 0:
            logger.warning(f"⚠️ Monthly API limit reached ({self.monthly_limit} calls)")
            return False
        
        if remaining <= 20:
            logger.warning(f"⚠️ Low API calls remaining: {remaining}")
        
        return True
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict = None,
        cache_key: str = None,
        cache_ttl: int = 6
    ) -> Optional[Dict]:
        """
        Make an API request with caching and error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            cache_key: Key for caching (if None, no caching)
            cache_ttl: Cache TTL in hours
            
        Returns:
            API response data or None on error
        """
        # Check cache first
        if cache_key:
            cached = db.get_cached_match(cache_key)
            if cached:
                logger.debug(f"📦 Cache hit: {cache_key}")
                return cached
        
        # Check rate limit
        if not self._check_rate_limit():
            return None
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"📡 API Request: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            # Track API usage
            db.increment_api_usage()
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache the response
                if cache_key and data:
                    db.cache_match_data(cache_key, data, cache_ttl)
                    logger.debug(f"💾 Cached: {cache_key}")
                
                return data
            
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limited by API, waiting...")
                time.sleep(60)
                return None
            
            else:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ API request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            return None
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON response from API")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # 🏆 SPORTS & LEAGUES
    # ═══════════════════════════════════════════════════════════════
    
    def get_sports(self) -> Optional[List[Dict]]:
        """Get list of available sports"""
        return self._make_request(
            "/v4/sports",
            cache_key="sports_list",
            cache_ttl=24
        )
    
    # ═══════════════════════════════════════════════════════════════
    # ⚽ FIXTURES & MATCHES
    # ═══════════════════════════════════════════════════════════════
    
    def get_upcoming_fixtures(
        self,
        sport: str = "soccer",
        hours: int = 24,
        leagues: List[str] = None
    ) -> List[Dict]:
        """
        Get upcoming fixtures for specified sport and leagues.
        
        Args:
            sport: Sport type (soccer, basketball, etc.)
            hours: Hours ahead to look for fixtures
            leagues: List of league IDs to filter
            
        Returns:
            List of fixture data
        """
        if leagues is None:
            leagues = [l['id'] for l in TOP_LEAGUES.get(sport, [])]
        
        all_fixtures = []
        
        for league_id in leagues:
            cache_key = f"fixtures_{league_id}_{datetime.now().strftime('%Y%m%d')}"
            
            fixtures = self._make_request(
                f"/v4/sports/{league_id}/odds",
                params={
                    "regions": "eu,uk",
                    "markets": "h2h,totals",
                    "oddsFormat": "decimal"
                },
                cache_key=cache_key,
                cache_ttl=4  # Cache for 4 hours
            )
            
            if fixtures:
                # Filter for fixtures within the time window
                cutoff_time = datetime.now() + timedelta(hours=hours)
                
                for fixture in fixtures:
                    try:
                        commence_time = datetime.fromisoformat(
                            fixture.get('commence_time', '').replace('Z', '+00:00')
                        )
                        if commence_time <= cutoff_time:
                            fixture['league_id'] = league_id
                            fixture['league_name'] = self._get_league_name(league_id)
                            all_fixtures.append(fixture)
                    except (ValueError, TypeError):
                        continue
        
        logger.info(f"⚽ Found {len(all_fixtures)} upcoming fixtures")
        return all_fixtures
    
    def _get_league_name(self, league_id: str) -> str:
        """Get human-readable league name from ID"""
        for sport_leagues in TOP_LEAGUES.values():
            for league in sport_leagues:
                if league['id'] == league_id:
                    return league['name']
        return league_id.replace('_', ' ').title()
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 ODDS DATA
    # ═══════════════════════════════════════════════════════════════
    
    def get_match_odds(self, fixture_id: str, league_id: str) -> Optional[Dict]:
        """
        Get detailed odds for a specific match.
        
        Args:
            fixture_id: Unique fixture identifier
            league_id: League identifier
            
        Returns:
            Odds data with all available markets
        """
        cache_key = f"odds_{fixture_id}"
        
        data = self._make_request(
            f"/v4/sports/{league_id}/odds",
            params={
                "eventIds": fixture_id,
                "regions": "eu,uk",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "decimal",
                "bookmakers": ",".join(PREFERRED_BOOKMAKERS)
            },
            cache_key=cache_key,
            cache_ttl=2  # Shorter cache for odds
        )
        
        if data and len(data) > 0:
            return data[0]
        return None
    
    def extract_best_odds(self, fixture: Dict) -> Dict[str, Any]:
        """
        Extract the best odds from all bookmakers for a fixture.
        
        Args:
            fixture: Fixture data with bookmaker odds
            
        Returns:
            Dictionary with best odds for each outcome
        """
        bookmakers = fixture.get('bookmakers', [])
        
        best_odds = {
            'home': {'odds': 0, 'bookmaker': ''},
            'draw': {'odds': 0, 'bookmaker': ''},
            'away': {'odds': 0, 'bookmaker': ''},
            'over_2_5': {'odds': 0, 'bookmaker': ''},
            'under_2_5': {'odds': 0, 'bookmaker': ''},
            'btts_yes': {'odds': 0, 'bookmaker': ''},
            'btts_no': {'odds': 0, 'bookmaker': ''},
        }
        
        # Also track specific bookmaker odds
        specific_odds = {
            'pinnacle': {},
            'bet365': {}
        }
        
        for bookmaker in bookmakers:
            bookie_name = bookmaker.get('key', '').lower()
            
            for market in bookmaker.get('markets', []):
                market_key = market.get('key', '')
                outcomes = market.get('outcomes', [])
                
                if market_key == 'h2h':
                    for outcome in outcomes:
                        name = outcome.get('name', '')
                        price = outcome.get('price', 0)
                        
                        # Determine outcome type
                        if name == fixture.get('home_team'):
                            if price > best_odds['home']['odds']:
                                best_odds['home'] = {'odds': price, 'bookmaker': bookie_name}
                            if bookie_name in specific_odds:
                                specific_odds[bookie_name]['home'] = price
                                
                        elif name == fixture.get('away_team'):
                            if price > best_odds['away']['odds']:
                                best_odds['away'] = {'odds': price, 'bookmaker': bookie_name}
                            if bookie_name in specific_odds:
                                specific_odds[bookie_name]['away'] = price
                                
                        elif name == 'Draw':
                            if price > best_odds['draw']['odds']:
                                best_odds['draw'] = {'odds': price, 'bookmaker': bookie_name}
                            if bookie_name in specific_odds:
                                specific_odds[bookie_name]['draw'] = price
                
                elif market_key == 'totals':
                    for outcome in outcomes:
                        name = outcome.get('name', '')
                        price = outcome.get('price', 0)
                        point = outcome.get('point', 0)
                        
                        if point == 2.5:
                            if name == 'Over' and price > best_odds['over_2_5']['odds']:
                                best_odds['over_2_5'] = {'odds': price, 'bookmaker': bookie_name}
                            elif name == 'Under' and price > best_odds['under_2_5']['odds']:
                                best_odds['under_2_5'] = {'odds': price, 'bookmaker': bookie_name}
        
        best_odds['specific'] = specific_odds
        return best_odds
    
    # ═══════════════════════════════════════════════════════════════
    # 📈 RESULTS
    # ═══════════════════════════════════════════════════════════════
    
    def get_match_result(self, fixture_id: str, league_id: str) -> Optional[Dict]:
        """
        Get the result of a completed match.
        
        Args:
            fixture_id: Unique fixture identifier
            league_id: League identifier
            
        Returns:
            Match result data
        """
        # Results endpoint - may vary by API
        data = self._make_request(
            f"/v4/sports/{league_id}/scores",
            params={
                "daysFrom": 1,
                "eventIds": fixture_id
            },
            cache_key=f"result_{fixture_id}",
            cache_ttl=24
        )
        
        if data and len(data) > 0:
            return data[0]
        return None
    
    def get_completed_matches(self, league_id: str, days: int = 1) -> List[Dict]:
        """
        Get completed matches for result updates.
        
        Args:
            league_id: League identifier
            days: Number of days back to look
            
        Returns:
            List of completed match data
        """
        data = self._make_request(
            f"/v4/sports/{league_id}/scores",
            params={"daysFrom": days},
            cache_key=f"scores_{league_id}_{days}d",
            cache_ttl=1
        )
        
        if data:
            return [m for m in data if m.get('completed', False)]
        return []
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 API STATUS
    # ═══════════════════════════════════════════════════════════════
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        monthly_usage = db.get_monthly_api_usage()
        daily_usage = db.get_api_usage_count()
        
        return {
            'monthly_usage': monthly_usage,
            'monthly_limit': self.monthly_limit,
            'monthly_remaining': self.monthly_limit - monthly_usage,
            'daily_usage': daily_usage,
            'percentage_used': round((monthly_usage / self.monthly_limit) * 100, 1)
        }


# Create singleton instance
odds_api = OddsAPIClient()
