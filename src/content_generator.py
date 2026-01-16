"""
Content generation module for the Facebook Football News Bot.

This module uses LLM APIs to transform raw news into engaging social media posts:
    - Primary: OpenAI GPT-3.5-turbo (cost-effective, reliable)
    - Fallback: Hugging Face Inference API (free tier available)

All generated content is automatically stripped of URLs for safety.
"""

import os
import logging
import json
from typing import Dict, Optional, List
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import strip_all_urls, get_env_var, sanitize_for_facebook, truncate_text

logger = logging.getLogger(__name__)


# Prompt templates
REWRITE_PROMPT = """You are a social media manager for a popular football fan page. 
Rewrite the following news into an exciting, engaging Facebook post.

RULES:
- Use an enthusiastic, fan-friendly tone
- Add 2-4 relevant emojis (⚽🔥🏆⭐💪🎯 etc.)
- Keep it under 280 characters
- DO NOT include any URLs, links, or website references
- DO NOT make up facts—only use the provided info
- DO NOT mention reading more or visiting any website
- End with a call to action (e.g., "What do you think? 👇" or "Drop your predictions! 👇")

NEWS HEADLINE: {headline}
NEWS SUMMARY: {summary}

Write ONLY the Facebook post text, nothing else:"""


HASHTAG_PROMPT = """Generate 5-8 relevant hashtags for this football news post.
Include a mix of general (#Football #Soccer #FootballNews) and specific (team/player/league names if mentioned).

RULES:
- Use CamelCase for multi-word hashtags (#PremierLeague not #premierleague)
- Include at least 2 general hashtags (#Football #Soccer)
- Do NOT include URLs in hashtags
- Return ONLY the hashtags separated by spaces, nothing else

Post content: {post_content}

Hashtags:"""


class ContentGeneratorError(Exception):
    """Custom exception for content generation errors."""
    pass


class ContentGenerator:
    """
    Generates engaging social media content using LLM APIs.
    
    Supports multiple LLM providers with automatic fallback.
    """
    
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"
    
    # Hugging Face model options (in order of preference)
    HF_MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "HuggingFaceH4/zephyr-7b-beta",
        "microsoft/DialoGPT-large"
    ]
    
    def __init__(self):
        """Initialize the content generator with API credentials."""
        self.openai_key = get_env_var("OPENAI_API_KEY", required=False)
        self.hf_token = get_env_var("HUGGINGFACE_TOKEN", required=False)
        self.session = requests.Session()
    
    def _call_openai(self, prompt: str, max_tokens: int = 300) -> Optional[str]:
        """
        Call OpenAI API to generate content.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated text or None if failed
        """
        if not self.openai_key:
            return None
        
        logger.info("Generating content with OpenAI...")
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional social media manager specializing in football/soccer content. You create engaging, emoji-rich posts that fans love."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1
        }
        
        try:
            response = self.session.post(
                self.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            logger.info("OpenAI content generated successfully")
            return content
            
        except requests.RequestException as e:
            logger.warning(f"OpenAI API call failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.warning(f"Failed to parse OpenAI response: {e}")
            return None
    
    def _call_huggingface(self, prompt: str) -> Optional[str]:
        """
        Call Hugging Face Inference API to generate content.
        
        Args:
            prompt: The prompt to send to the model
        
        Returns:
            Generated text or None if failed
        """
        if not self.hf_token:
            return None
        
        logger.info("Generating content with Hugging Face...")
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        # Format prompt for instruction-tuned models
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        # Try each model until one works
        for model in self.HF_MODELS:
            try:
                response = self.session.post(
                    f"{self.HUGGINGFACE_API_URL}/{model}",
                    headers=headers,
                    json=payload,
                    timeout=120  # HF can be slow
                )
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    logger.info(f"Model {model} is loading, trying next...")
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    content = data[0].get("generated_text", "").strip()
                    if content:
                        logger.info(f"Hugging Face ({model}) content generated successfully")
                        return content
                        
            except requests.RequestException as e:
                logger.warning(f"Hugging Face API call failed for {model}: {e}")
                continue
        
        return None
    
    def _generate_fallback_post(self, headline: str, summary: str) -> str:
        """
        Generate a fallback post without LLM when APIs are unavailable.
        
        Args:
            headline: News headline
            summary: News summary
        
        Returns:
            Formatted post text
        """
        logger.warning("Using template-based fallback for post generation")
        
        # Clean inputs
        headline = strip_all_urls(headline)
        summary = strip_all_urls(summary)
        
        # Template-based post
        templates = [
            "⚽ {headline}\n\n{summary}\n\nWhat do you think? 👇",
            "🔥 BREAKING: {headline}\n\n{summary}\n\nShare your thoughts! 💬",
            "🏆 {headline}\n\n{summary}\n\nDrop your reaction below! ⬇️",
            "⚽💥 {headline}\n\n{summary}\n\nAgree or disagree? Let us know! 👇"
        ]
        
        import random
        template = random.choice(templates)
        
        post = template.format(
            headline=truncate_text(headline, 100),
            summary=truncate_text(summary, 150)
        )
        
        return post
    
    def _generate_fallback_hashtags(self, content: str) -> str:
        """
        Generate fallback hashtags without LLM.
        
        Args:
            content: Post content
        
        Returns:
            String of hashtags
        """
        logger.warning("Using template-based fallback for hashtag generation")
        
        # Base hashtags
        hashtags = ["#Football", "#Soccer", "#FootballNews"]
        
        # Add contextual hashtags based on keywords
        content_lower = content.lower()
        
        keyword_hashtags = {
            "premier league": "#PremierLeague #EPL",
            "champions league": "#ChampionsLeague #UCL",
            "la liga": "#LaLiga",
            "bundesliga": "#Bundesliga",
            "serie a": "#SerieA",
            "world cup": "#WorldCup #FIFA",
            "manchester": "#MUFC #MCFC",
            "liverpool": "#LFC",
            "chelsea": "#CFC",
            "arsenal": "#AFC",
            "barcelona": "#FCBarcelona #Barca",
            "real madrid": "#RealMadrid #HalaMadrid",
            "goal": "#Goal #GoalOfTheDay",
            "transfer": "#TransferNews #TransferWindow",
            "messi": "#Messi",
            "ronaldo": "#Ronaldo #CR7",
            "haaland": "#Haaland",
            "mbappe": "#Mbappe"
        }
        
        for keyword, tag in keyword_hashtags.items():
            if keyword in content_lower:
                hashtags.append(tag)
        
        # Add generic engagement hashtags
        hashtags.extend(["#MatchDay", "#FootballFans"])
        
        # Deduplicate and limit
        unique_hashtags = list(dict.fromkeys(hashtags))[:8]
        
        return " ".join(unique_hashtags)
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=10))
    def generate_post(self, headline: str, summary: str) -> str:
        """
        Generate an engaging social media post from news content.
        
        Args:
            headline: News headline
            summary: News summary
        
        Returns:
            Engaging post text (URL-free)
        """
        prompt = REWRITE_PROMPT.format(
            headline=strip_all_urls(headline),
            summary=strip_all_urls(summary)
        )
        
        # Try OpenAI first
        result = self._call_openai(prompt)
        
        # Fall back to Hugging Face
        if not result:
            result = self._call_huggingface(prompt)
        
        # Fall back to template
        if not result:
            result = self._generate_fallback_post(headline, summary)
        
        # Safety: Strip any URLs that might have slipped through
        return strip_all_urls(result)
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=10))
    def generate_hashtags(self, post_content: str) -> str:
        """
        Generate relevant hashtags for a post.
        
        Args:
            post_content: The post text to generate hashtags for
        
        Returns:
            String of hashtags
        """
        prompt = HASHTAG_PROMPT.format(post_content=strip_all_urls(post_content))
        
        # Try OpenAI first
        result = self._call_openai(prompt, max_tokens=100)
        
        # Fall back to Hugging Face
        if not result:
            result = self._call_huggingface(prompt)
        
        # Fall back to template
        if not result:
            result = self._generate_fallback_hashtags(post_content)
        
        # Clean up hashtags
        hashtags = result.strip()
        
        # Ensure hashtags start with #
        if hashtags and not hashtags.startswith("#"):
            # Try to extract hashtags from the response
            import re
            found_hashtags = re.findall(r'#\w+', hashtags)
            if found_hashtags:
                hashtags = " ".join(found_hashtags)
            else:
                # Add # to words
                words = hashtags.split()
                hashtags = " ".join(f"#{w}" if not w.startswith("#") else w for w in words[:8])
        
        return strip_all_urls(hashtags)
    
    def generate(self, headline: str, summary: str) -> Dict[str, str]:
        """
        Generate complete post content including text and hashtags.
        
        Args:
            headline: News headline
            summary: News summary
        
        Returns:
            Dict containing:
                - post_text: The engaging post text
                - hashtags: Relevant hashtags
                - caption: Combined post_text + hashtags
        """
        # Generate main post
        post_text = self.generate_post(headline, summary)
        
        # Generate hashtags
        hashtags = self.generate_hashtags(post_text)
        
        # Combine into final caption
        caption = f"{post_text}\n\n{hashtags}"
        
        # Final safety sanitization
        caption = sanitize_for_facebook(caption)
        
        return {
            "post_text": post_text,
            "hashtags": hashtags,
            "caption": caption
        }


def generate_engaging_post(headline: str, summary: str) -> Dict[str, str]:
    """
    Main entry point for generating engaging Facebook post content.
    
    This function creates a ContentGenerator instance and generates
    a complete post with text and hashtags.
    
    Args:
        headline: News headline to rewrite
        summary: News summary to incorporate
    
    Returns:
        Dict with post_text, hashtags, and combined caption
    
    Example:
        >>> content = generate_engaging_post(
        ...     "Manchester United wins match",
        ...     "Manchester United defeated Liverpool 2-1 in an exciting Premier League clash."
        ... )
        >>> print(content["caption"])
        "⚽🔥 What a match! Manchester United edges past Liverpool 2-1... #Football #PremierLeague"
    """
    generator = ContentGenerator()
    return generator.generate(headline, summary)
