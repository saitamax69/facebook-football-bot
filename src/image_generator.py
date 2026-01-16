"""
Professional Image Generator for Football Bot.
Generates sleek, dark-themed social media cards when stock photos fail.
"""

import os
import textwrap
import logging
import requests
import tempfile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

class ImageGenerator:
    # Google Font URL (Roboto Bold for professional look)
    FONT_URL = "https://github.com/google/fonts/raw/main/apache/robotoslab/RobotoSlab-Bold.ttf"
    
    def __init__(self):
        self.width = 1200
        self.height = 630
        self.font_path = self._download_font()

    def _download_font(self):
        """Downloads a professional font to a temp file."""
        try:
            response = requests.get(self.FONT_URL, timeout=10)
            f = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf")
            f.write(response.content)
            f.close()
            return f.name
        except Exception as e:
            logger.warning(f"Could not download font: {e}")
            return None

    def _create_background(self):
        """Creates a modern dark gradient background."""
        # Create base dark blue/black image
        base = Image.new('RGB', (self.width, self.height), color=(10, 25, 47))
        draw = ImageDraw.Draw(base)
        
        # Add subtle gradient overlay
        for y in range(self.height):
            # Fade from dark blue to slightly lighter blue
            r, g, b = 10, 25 + (y // 40), 47 + (y // 30)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
            
        return base

    def generate(self, headline: str, subtext: str = "Daily Football Update") -> str:
        """
        Generates a professional news card.
        """
        img = self._create_background()
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_size_header = 70
            font_size_sub = 40
            
            if self.font_path:
                title_font = ImageFont.truetype(self.font_path, font_size_header)
                sub_font = ImageFont.truetype(self.font_path, font_size_sub)
            else:
                title_font = ImageFont.load_default()
                sub_font = ImageFont.load_default()
        except:
            title_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()

        # WRAP TEXT LOGIC
        # Remove scores from headline for cleaner look if it's too long
        display_text = headline.split("In today's")[0].strip() # Clean up SportsDB raw text
        
        lines = textwrap.wrap(display_text, width=25) # Wrap text to fit
        
        # Calculate vertical center
        total_text_height = len(lines) * (font_size_header + 10) + (font_size_sub + 20)
        current_y = (self.height - total_text_height) // 2

        # Draw "BREAKING NEWS" or "MATCH RESULT" badge
        badge_text = "MATCH UPDATE" if any(char.isdigit() for char in display_text) else "FOOTBALL NEWS"
        draw.rectangle(
            [(self.width//2 - 100, current_y - 60), (self.width//2 + 100, current_y - 10)], 
            fill=(220, 20, 60) # Crimson Red
        )
        w_badge = draw.textlength(badge_text, font=sub_font)
        draw.text(
            (self.width//2 - w_badge//2, current_y - 55),
            badge_text,
            font=sub_font,
            fill=(255, 255, 255)
        )

        # Draw Headline
        for line in lines:
            line_w = draw.textlength(line, font=title_font)
            draw.text(
                ((self.width - line_w) / 2, current_y), 
                line, 
                font=title_font, 
                fill=(255, 255, 255)
            )
            current_y += font_size_header + 10

        # Draw Footer/Subtext
        current_y += 30
        # Draw a horizontal divider line
        draw.line(
            [(self.width//2 - 100, current_y), (self.width//2 + 100, current_y)], 
            fill=(100, 200, 255), 
            width=3
        )
        
        current_y += 30
        sub_w = draw.textlength(subtext, font=sub_font)
        draw.text(
            ((self.width - sub_w) / 2, current_y), 
            subtext, 
            font=sub_font, 
            fill=(150, 170, 190)
        )

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_file.name, quality=95)
        return temp_file.name

def create_pro_image(headline: str, source: str) -> str:
    generator = ImageGenerator()
    return generator.generate(headline, source)
