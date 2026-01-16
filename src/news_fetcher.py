"""
News fetching module for the Facebook Football News Bot.

This module retrieves football/soccer news from multiple sources:
    - Primary: NewsAPI.org (requires API key)
    - Fallback: TheSportsDB (free, no key required)

All returned content is automatically stripped of URLs for safety.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import strip_all_urls, get_env_var, api_retry

logger = logging.getLogger(__name__)


class NewsAPIError(Exception):
    """Custom exception for News API errors."""
    pass


class NewsFetcher:
    """
    Fetches football news from multiple sources with automatic fallback.
    
    Attributes:
        newsapi_key: API key for NewsAPI.org
        session: Requests session for connection pooling
    """
    
    NEWSAPI_BASE_URL = "https://newsapi.org/v2"
    SPORTSDB_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # Keywords to search for football news
    FOOTBALL_KEYWORDS = [
        "football",
        "soccer", 
        "Premier League",
        "Champions League",
        "La Liga",
        "Bundesliga",
        "Serie A",
        "World Cup",
        "UEFA",
        "FIFA"
    ]
    
    def __init__(self):
        """Initialize the news fetcher with API credentials."""
        self.newsapi_key = get_env_var("NEWSAPI_KEY", required=False)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FootballNewsBot/1.0"
        })
    
    @api_retry
    def _fetch_from_newsapi(self) -> Optional[Dict[str, str]]:
        """
        Fetch football news from NewsAPI.org.
        
        Returns:
            Dict with headline, summary, and source_name, or None if failed
        """
        if not self.newsapi_key:
            logger.info("NewsAPI key not configured, skipping...")
            return None
        
        logger.info("Fetching news from NewsAPI...")
        
        # Build query string
        query = " OR ".join(self.FOOTBALL_KEYWORDS[:5])  # Use top 5 keywords
        
        params = {
            "apiKey": self.newsapi_key,
            "category": "sports",
            "q": query,
            "language": "en",
            "pageSize": 10,
            "sortBy": "publishedAt"
        }
        
        try:
            response = self.session.get(
                f"{self.NEWSAPI_BASE_URL}/top-headlines",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.warning(f"NewsAPI returned error: {data.get('message')}")
                return None
            
            articles = data.get("articles", [])
            if not articles:
                logger.warning("No articles found from NewsAPI")
                return None
            
            # Find the best article (prioritize those with descriptions)
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                source_name = article.get("source", {}).get("name", "Unknown")
                
                # Skip articles with missing content or "[Removed]" placeholders
                if not title or "[Removed]" in title:
                    continue
                if not description or "[Removed]" in description:
                    continue
                
                # Clean the content
                clean_title = strip_all_urls(title)
                clean_description = strip_all_urls(description)
                
                if clean_title and clean_description:
                    logger.info(f"Selected article: {clean_title[:50]}...")
                    return {
                        "headline": clean_title,
                        "summary": clean_description,
                        "source_name": strip_all_urls(source_name)
                    }
            
            logger.warning("No suitable articles found after filtering")
            return None
            
        except requests.RequestException as e:
            logger.error(f"NewsAPI request failed: {e}")
            raise
    
    @api_retry
    def _fetch_from_sportsdb(self) -> Optional[Dict[str, str]]:
        """
        Fetch football events from TheSportsDB (free, no API key needed).
        
        Returns:
            Dict with headline, summary, and source_name, or None if failed
        """
        logger.info("Fetching events from TheSportsDB...")
        
        # Get today's date and format for API
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        try:
            # Fetch today's soccer events
            response = self.session.get(
                f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                params={"d": today, "s": "Soccer"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            events = data.get("events")
            if not events:
                # Try yesterday if today has no events
                yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
                response = self.session.get(
                    f"{self.SPORTSDB_BASE_URL}/eventsday.php",
                    params={"d": yesterday, "s": "Soccer"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                events = data.get("events")
            
            if not events:
                logger.warning("No soccer events found from TheSportsDB")
                return None
            
            # Find an interesting event (preferably with scores)
            for event in events:
                home_team = event.get("strHomeTeam", "")
                away_team = event.get("strAwayTeam", "")
                league = event.get("strLeague", "Soccer Match")
                home_score = event.get("intHomeScore")
                away_score = event.get("intAwayScore")
                venue = event.get("strVenue", "")
                
                if not home_team or not away_team:
                    continue
                
                # Build headline
                if home_score is not None and away_score is not None:
                    headline = f"{home_team} {home_score} - {away_score} {away_team}"
                    summary = f"In today's {league} match, {home_team} faced {away_team}"
                    if venue:
                        summary += f" at {venue}"
                    summary += f". Final score: {home_score}-{away_score}."
                else:
                    headline = f"{home_team} vs {away_team} - {league}"
                    summary = f"Upcoming {league} match: {home_team} takes on {away_team}"
                    if venue:
                        summary += f" at {venue}"
                    summary += "."
                
                return {
                    "headline": strip_all_urls(headline),
                    "summary": strip_all_urls(summary),
                    "source_name": "TheSportsDB"
                }
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"TheSportsDB request failed: {e}")
            raise
    
    def _generate_fallback_content(self) -> Dict[str, str]:
        """
        Generate fallback content when all APIs fail.
        
        Returns:
            Dict with generic football content
        """
        logger.warning("Using fallback content generation")
        
        # Day-specific content
        day_of_week = datetime.utcnow().strftime("%A")
        
        headlines = {
            "Monday": "Football Week Kicks Off!",
            "Tuesday": "Champions League Action Continues",
            "Wednesday": "Midweek Football Fever",
            "Thursday": "Europa League Excitement",
            "Friday": "Weekend Football Preview",
            "Saturday": "It's Matchday!",
            "Sunday": "Super Sunday Football"
        }
        
        summaries = {
            "Monday": "A new week of football begins! What matches are you looking forward to?",
            "Tuesday": "Champions League nights are always special. Who's your pick to win?",
            "Wednesday": "Midweek football is the best! So many great matches happening.",
            "Thursday": "Europa League action tonight! Which team will shine?",
            "Friday": "The weekend is almost here! Time to preview all the big matches.",
            "Saturday": "Matchday vibes! Nothing beats live football action.",
            "Sunday": "Super Sunday football! The perfect way to end the weekend."
        }
        
        return {
            "headline": headlines.get(day_of_week, "Football News Update"),
            "summary": summaries.get(day_of_week, "Stay tuned for the latest football news and updates!"),
            "source_name": "Football Bot"
        }
    
    def fetch(self) -> Optional[Dict[str, str]]:
        """
        Fetch football news with automatic fallback between sources.
        
        Returns:
            Dict containing:
                - headline: News headline (URL-free)
                - summary: News summary (URL-free)
                - source_name: Name of the source
            
            Returns None only if all sources fail AND fallback is disabled.
        """
        # Try primary source (NewsAPI)
        try:
            result = self._fetch_from_newsapi()
            if result:
                return result
        except Exception as e:
            logger.warning(f"NewsAPI failed, trying fallback: {e}")
        
        # Try fallback source (TheSportsDB)
        try:
            result = self._fetch_from_sportsdb()
            if result:
                return result
        except Exception as e:
            logger.warning(f"TheSportsDB failed: {e}")
        
        # Use generated fallback content
        return self._generate_fallback_content()


def fetch_football_news() -> Optional[Dict[str, str]]:
    """
    Main entry point for fetching football news.
    
    This function creates a NewsFetcher instance and retrieves news
    from the configured sources with automatic fallback.
    
    Returns:
        Dict with headline, summary, and source_name
        Returns None if no news is available (rare, due to fallback)
    
    Example:
        >>> news = fetch_football_news()
        >>> print(news["headline"])
        "Manchester United defeats Liverpool in thrilling match"
    """
    fetcher = NewsFetcher()
    return fetcher.fetch()
