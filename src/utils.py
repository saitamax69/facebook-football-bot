"""
Utility functions
"""
from datetime import datetime
import pytz


def format_date(dt):
    """Format: Monday, 15 January 2025"""
    return dt.strftime('%A, %d %B %Y')


def format_time(dt):
    """Format: HH:MM"""
    return dt.strftime('%H:%M')


def odds_to_probability(odds):
    """Convert decimal odds to probability"""
    return round((1 / odds) * 100, 1) if odds > 0 else 0


def calculate_profit(odds, stake, won):
    """Calculate profit/loss"""
    return round(stake * odds - stake, 2) if won else -stake


def get_current_utc():
    """Get current UTC time"""
    return datetime.now(pytz.UTC)
