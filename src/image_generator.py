"""
Professional Scoreboard Generator.
Designed for high-quality output without stock photos.
"""

import logging
import textwrap
import tempfile
import requests
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class ImageGenerator:
    # Google Font: Roboto Condensed (Bold) - Looks like sports TV fonts
    FONT_URL = "https://github.com/google/fonts/raw/main/apache/robotocondensed/RobotoCondensed-Bold.ttf"
    
    def __init__(self):
        self.width = 1080
        self.height = 1080
        self.font_path = self._download_font()

    def _download_font(self):
        try:
            response = requests.get(self.FONT_URL, timeout=10)
            if response.status_code == 200:
                f = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf")
                f.write(response.content)
                f.close()
                return f.name
        except:
            pass
        return None

    def generate(self, headline: str, subtext: str = "Football Update") -> str:
        # 1. Background: Dark Navy Gradient
        img = Image.new('RGB', (self.width, self.height), color=(10, 25, 47))
        draw = ImageDraw.Draw(img)
        
        # Subtle gradient
        for y in range(self.height):
            r = 10 + int(y * 0.02)
            g = 25 + int(y * 0.02)
            b = 47 + int(y * 0.04)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Fonts
        try:
            if self.font_path:
                score_font = ImageFont.truetype(self.font_path, 140)
                team_font = ImageFont.truetype(self.font_path, 70)
                meta_font = ImageFont.truetype(self.font_path, 40)
            else:
                raise Exception
        except:
            score_font = ImageFont.load_default()
            team_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()

        center_x = self.width // 2
        center_y = self.height // 2

        # 2. PARSE HEADLINE (Team A 1 - 2 Team B)
        # We try to split by numbers or "vs"
        vs_text = "VS"
        top_text = ""
        bottom_text = ""
        
        if " - " in headline and any(char.isdigit() for char in headline):
            # It's a score: "Liverpool 2 - 1 Chelsea"
            parts = headline.split(" - ")
            # Try to separate score from team name
            # This is a bit rough but works for most SportsDB formats
            left_part = parts[0].rsplit(' ', 1) # ["Liverpool", "2"]
            right_part = parts[1].split(' ', 1) # ["1", "Chelsea"]
            
            if len(left_part) == 2 and len(right_part) == 2:
                top_text = left_part[0]
                bottom_text = right_part[1]
                vs_text = f"{left_part[1]} - {right_part[0]}" # "2 - 1"
            else:
                top_text = headline
                vs_text = "FT"
        elif " vs " in headline:
            parts = headline.split(" vs ")
            top_text = parts[0]
            bottom_text = parts[1]
            vs_text = "VS"
        else:
            top_text = headline
            vs_text = "NEWS"

        # 3. DRAW LAYOUT
        
        # Draw "VS" or "SCORE" Badge in Center
        draw.rectangle(
            [(0, center_y - 100), (self.width, center_y + 100)],
            fill=(15, 23, 42) # Darker strip
        )
        draw.line([(0, center_y - 100), (self.width, center_y - 100)], fill=(255, 215, 0), width=5) # Gold Line top
        draw.line([(0, center_y + 100), (self.width, center_y + 100)], fill=(255, 215, 0), width=5) # Gold Line bottom
        
        # Draw Score/VS Text
        draw.text((center_x, center_y), vs_text, font=score_font, fill=(255, 255, 255), anchor="mm")

        # Draw Top Team (Home)
        lines = textwrap.wrap(top_text, width=20)
        y_pos = center_y - 200 - (len(lines)*70)
        for line in lines:
            draw.text((center_x, y_pos), line, font=team_font, fill='white', anchor="mm")
            y_pos += 75

        # Draw Bottom Team (Away)
        lines = textwrap.wrap(bottom_text, width=20)
        y_pos = center_y + 180
        for line in lines:
            draw.text((center_x, y_pos), line, font=team_font, fill='white', anchor="mm")
            y_pos += 75

        # 4. Footer
        draw.text((center_x, self.height - 80), subtext.upper(), font=meta_font, fill=(150, 150, 150), anchor="mm")

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_file.name, quality=95)
        return temp_file.name

def create_pro_image(headline: str, source: str) -> str:
    generator = ImageGenerator()
    return generator.generate(headline, source)
