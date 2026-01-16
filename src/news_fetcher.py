"""
News fetching module.
Primary: ESPN public scoreboard (no key).
Fallback: TheSportsDB (free).
Strictly targets top European competitions, with optional AFCON.

Environment (optional):
  INCLUDE_AFCON=true|false   # default true
  DAYS_SCAN=3                # days window in each direction (default 3 -> ±3 days)
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any

import requests
from .utils import strip_all_urls, api_retry

logger = logging.getLogger(__name__)


class NewsFetcher:
    """
    Fetch high-signal football news (match result or preview) from ESPN first,
    then fall back to TheSportsDB if ESPN returns nothing.

    Prefers: Results from yesterday, then today live/preview, then tomorrow.
    Scans a configurable ±N day window.
    """

    # ESPN public endpoints (no key)
    ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

    # Target competitions (code, friendly name) in priority order
    TARGET_LEAGUES: List[Tuple[str, str]] = [
        ("uefa.champions", "UEFA Champions League"),
        ("eng.1", "English Premier League"),
        ("esp.1", "Spanish La Liga"),
        ("ita.1", "Italian Serie A"),
        ("ger.1", "German Bundesliga"),
        ("fra.1", "French Ligue 1"),
        ("uefa.europa", "UEFA Europa League"),
        ("uefa.europa.conf", "UEFA Europa Conference League"),
        # AFCON added conditionally below
    ]

    # Fallback match whitelist for TheSportsDB (by league name contains)
    EURO_LEAGUES_WHITELIST = [
        "Premier League",
        "La Liga",
        "Bundesliga",
        "Serie A",
        "Ligue 1",
        "Champions League",
        "Europa League",
        "Europa Conference",
    ]

    def __init__(self) -> None:
        include_afcon = os.environ.get("INCLUDE_AFCON", "true").lower() == "true"
        if include_afcon:
            self.TARGET_LEAGUES.append(("africa.cup", "Africa Cup of Nations"))

        self.days_scan = int(os.environ.get("DAYS_SCAN", "3"))
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "FootballNewsBot/1.0"})

    # ---------------------- ESPN primary ----------------------

    @api_retry
    def _espn_scoreboard(
        self, league_code: str, date_yyyymmdd: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get ESPN scoreboard events for a league and date (YYYYMMDD).
        Returns a list of events or None.
        """
        url = f"{self.ESPN_BASE}/{league_code}/scoreboard"
        params = {"dates": date_yyyymmdd}
        resp = self.session.get(url, params=params, timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        events = data.get("events", [])
        return events or None

    def _espn_pick_best(
        self, events: List[Dict[str, Any]], prefer_results: bool
    ) -> Optional[Dict[str, str]]:
        """
        From ESPN events, pick a single high-signal match and format headline/summary.
        prefer_results: True when scanning past dates.
        """
        if not events:
            return None

        def parse_event(evt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            try:
                comp = evt["competitions"][0]
                comps = comp["competitors"]
                home = next(c for c in comps if c.get("homeAway") == "home")
                away = next(c for c in comps if c.get("homeAway") == "away")

                state = evt["status"]["type"]["state"]  # "post", "in", "pre"
                short_detail = evt["status"]["type"].get("shortDetail") or ""
                kickoff_iso = evt.get("date")  # ISO datetime
                # names
                home_name = home["team"].get("displayName") or home["team"].get("shortDisplayName") or home["team"]["name"]
                away_name = away["team"].get("displayName") or away["team"].get("shortDisplayName") or away["team"]["name"]
                # scores as strings; set None unless match finished or live
                home_score = home.get("score")
                away_score = away.get("score")
                # league name (may vary), use competition text if present
                league_name = comp.get("league", {}).get("name") or evt.get("league", {}).get("name")

                return {
                    "state": state,
                    "home_name": home_name,
                    "away_name": away_name,
                    "home_score": home_score,
                    "away_score": away_score,
                    "short_detail": short_detail,
                    "kickoff_iso": kickoff_iso,
                    "league_name": league_name or "",
                }
            except Exception:
                return None

        parsed: List[Dict[str, Any]] = [p for e in events if (p := parse_event(e))]

        # Sort preference: post (finished) > in (live) > pre (upcoming)
        state_rank = {"post": 3, "in": 2, "pre": 1}
        parsed.sort(key=lambda x: state_rank.get(x["state"], 0), reverse=True)

        # If we prefer results, require 'post'
        for p in parsed:
            if prefer_results and p["state"] != "post":
                continue

            # Build headline/summary
            if p["state"] == "post" and p["home_score"] is not None and p["away_score"] is not None:
                headline = f"{p['home_name']} {p['home_score']}-{p['away_score']} {p['away_name']}"
                summary = p["short_detail"] or "Full time."
            else:
                # Upcoming/live
                # Format kickoff time (UTC)
                kick_str = ""
                if p["kickoff_iso"]:
                    try:
                        dt = datetime.fromisoformat(p["kickoff_iso"].replace("Z", "+00:00"))
                        kick_str = f"Kickoff {dt.strftime('%H:%M')} UTC."
                    except Exception:
                        pass
                headline = f"{p['home_name']} vs {p['away_name']}"
                summary = p["short_detail"] or kick_str or "Match update."

            return {
                "headline": strip_all_urls(headline),
                "summary": strip_all_urls(summary),
                "source_name": strip_all_urls(p["league_name"]),
            }

        return None

    def _scan_espn(self) -> Optional[Dict[str, str]]:
        """
        Scan ±days_scan window across target leagues (priority order).
        Prefer results for past days; otherwise allow upcoming/live.
        """
        offsets = (
            [-1, 0, 1]
            + [i for i in (-2, 2) if self.days_scan >= 2]
            + [i for i in (-3, 3) if self.days_scan >= 3]
        )

        for offset in offsets:
            prefer_results = offset < 0
            day = (datetime.utcnow() + timedelta(days=offset))
            d_yyyymmdd = day.strftime("%Y%m%d")

            for code, friendly in self.TARGET_LEAGUES:
                try:
                    events = self._espn_scoreboard(code, d_yyyymmdd)
                except Exception as e:
                    logger.debug(f"ESPN fetch failed for {code} {d_yyyymmdd}: {e}")
                    events = None

                if not events:
                    continue

                pick = self._espn_pick_best(events, prefer_results=prefer_results)
                if pick:
                    # Use our friendly league label if ESPN's name is missing/weird
                    if not pick.get("source_name"):
                        pick["source_name"] = friendly
                    return pick

        return None

    # ------------------ TheSportsDB fallback (filtered) ------------------

    @api_retry
    def _sportsdb_day(self, date_str: str) -> Optional[List[Dict[str, Any]]]:
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php"
        resp = self.session.get(url, params={"d": date_str, "s": "Soccer"}, timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("events") or None

    def _scan_sportsdb(self) -> Optional[Dict[str, str]]:
        """
        Fallback: scan TheSportsDB for the same window, but only accept
        leagues whose names contain our Euro whitelist (or AFCON if enabled).
        """
        include_afcon = os.environ.get("INCLUDE_AFCON", "true").lower() == "true"
        offsets = (
            [-1, 0, 1]
            + [i for i in (-2, 2) if self.days_scan >= 2]
            + [i for i in (-3, 3) if self.days_scan >= 3]
        )

        for offset in offsets:
            prefer_results = offset < 0
            date_str = (datetime.utcnow() + timedelta(days=offset)).strftime("%Y-%m-%d")
            events = self._sportsdb_day(date_str)
            if not events:
                continue

            for e in events:
                league = e.get("strLeague", "") or ""
                # filter to Euro whitelist (and AFCON if allowed)
                is_euro = any(k.lower() in league.lower() for k in self.EURO_LEAGUES_WHITELIST)
                is_afcon = include_afcon and ("africa" in league.lower() or "afcon" in league.lower())
                if not (is_euro or is_afcon):
                    continue

                home = e.get("strHomeTeam") or ""
                away = e.get("strAwayTeam") or ""
                hs = e.get("intHomeScore")
                as_ = e.get("intAwayScore")

                if prefer_results and (hs is None or as_ is None):
                    continue

                if hs is not None and as_ is not None:
                    headline = f"{home} {hs}-{as_} {away}"
                    summary = f"Full time in the {league}."
                else:
                    headline = f"{home} vs {away}"
                    venue = e.get("strVenue") or ""
                    summary = f"{league} clash at {venue}." if venue else f"{league} clash."

                return {
                    "headline": strip_all_urls(headline),
                    "summary": strip_all_urls(summary),
                    "source_name": strip_all_urls(league),
                }

        return None

    # ------------------ Public entrypoint ------------------

    def fetch(self) -> Optional[Dict[str, str]]:
        """
        Try ESPN first, then TheSportsDB. Returns:
        {"headline": str, "summary": str, "source_name": str} or None.
        """
        logger.info("🔎 Scanning ESPN for top European (and optional AFCON) matches...")
        pick = self._scan_espn()
        if pick:
            return pick

        logger.info("↘️ ESPN empty — trying TheSportsDB fallback (EU-only filter).")
        pick = self._scan_sportsdb()
        if pick:
            return pick

        logger.warning("No suitable matches found in scan window.")
        return None


def fetch_football_news() -> Optional[Dict[str, str]]:
    """
    Convenience wrapper used by main.py
    """
    return NewsFetcher().fetch()
