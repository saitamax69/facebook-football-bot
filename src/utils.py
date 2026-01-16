"""
Utility functions shared across the Facebook Football News Bot.

This module provides:
    - URL stripping for content safety
    - Logging configuration
    - Common retry decorators
    - Environment variable helpers
"""

import re
import os
import logging
from typing import Optional, Any
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import requests


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging for GitHub Actions visibility.
    
    Args:
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logging.getLogger("FootballBot")


def strip_all_urls(text: str) -> str:
    """
    Remove ALL URLs from text. This is critical for compliance.
    Apply this to ALL text before posting to Facebook.
    
    Args:
        text: Input text that may contain URLs
    
    Returns:
        Cleaned text with all URLs removed
    
    Examples:
        >>> strip_all_urls("Check out https://example.com for more!")
        'Check out for more!'
        >>> strip_all_urls("Visit www.test.org today")
        'Visit today'
    """
    if not text:
        return ""
    
    # Comprehensive URL pattern
    url_patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard URLs
        r'www\.[^\s<>"{}|\\^`\[\]]+',  # www URLs
        r'bit\.ly/[^\s]+',  # Short URLs
        r'[^\s]+\.(com|org|net|io|co|uk|de|fr|es|it|ru|jp|cn|in|br|au)/[^\s]*',  # Domain paths
        r'\b[a-zA-Z0-9.-]+\.(com|org|net|io|co\.uk|edu|gov)\b',  # Bare domains
    ]
    
    cleaned = text
    for pattern in url_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+([.,!?])', r'\1', cleaned)  # Fix spacing before punctuation
    cleaned = cleaned.strip()
    
    return cleaned


def get_env_var(name: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with optional requirement enforcement.
    
    Args:
        name: Environment variable name
        required: If True, raise error when variable is missing
        default: Default value if variable is not set
    
    Returns:
        Environment variable value or default
    
    Raises:
        EnvironmentError: If required variable is missing
    """
    value = os.environ.get(name, default)
    
    if required and not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Please add it to your GitHub Secrets."
        )
    
    return value


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    logger: Optional[logging.Logger] = None
):
    """
    Create a retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        logger: Logger for retry messages
    
    Returns:
        Configured retry decorator
    """
    log = logger or logging.getLogger(__name__)
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((requests.RequestException, TimeoutError)),
        before_sleep=before_sleep_log(log, logging.WARNING),
        reraise=True
    )


# Pre-configured retry decorator for API calls
api_retry = create_retry_decorator(max_attempts=3, min_wait=2, max_wait=30)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, preserving word boundaries.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    # Try to break at a word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    
    return truncated.rstrip() + suffix


def is_dry_run() -> bool:
    """
    Check if the bot is running in dry-run mode.
    
    Returns:
        True if DRY_RUN environment variable is set to 'true'
    """
    return os.environ.get("DRY_RUN", "false").lower() == "true"


def sanitize_for_facebook(text: str) -> str:
    """
    Sanitize text for Facebook posting.
    Removes URLs, excessive emojis, and ensures proper formatting.
    
    Args:
        text: Raw text content
    
    Returns:
        Sanitized text safe for Facebook posting
    """
    # First, strip all URLs
    text = strip_all_urls(text)
    
    # Remove any remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limit consecutive emojis (max 4 in a row)
    emoji_pattern = r'([\U0001F300-\U0001F9FF]){5,}'
    text = re.sub(emoji_pattern, r'\1\1\1\1', text)
    
    # Remove zero-width characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    # Normalize newlines (max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
