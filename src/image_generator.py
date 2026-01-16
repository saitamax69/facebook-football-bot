"""
Professional Scoreboard Generator.
Uses System Fonts to guarantee size and readability.
"""

import logging
import textwrap
import tempfile
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1080
        # GitHub Actions (Ubuntu) System Font Path
        # This guarantees it won't be tiny pixels
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def _get_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except OSError:
            # Fallback for local testing (Windows/Mac) if DejaVu isn't there
            return ImageFont.load_default()

    def generate(self, headline: str, league_name: str) -> str:
        # 1. Dark Background (Navy)
        img = Image.new('RGB', (self.width, self.height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        
        # 2. Parse Headline
        # Formats: "TeamA 2-1 TeamB" OR "TeamA vs TeamB"
        if "-" in headline and any(c.isdigit() for c in headline):
            # Result
            parts = headline.split("-") # ["Man City 3", "1 Man Utd"]
            # Extract score from text (rough logic but works for simple strings)
            try:
                left_side = parts[0].rsplit(" ", 1) # ["Man City", "3"]
                right_side = parts[1].lstrip().split(" ", 1) # ["1", "Man Utd"]
                
                team_home = left_side[0].strip()
                score_home = left_side[1].strip()
                score_away = right_side[0].strip()
                team_away = right_side[1].strip()
                center_text = f"{score_home} - {score_away}"
                status_text = "FULL TIME"
            except:
                # Fallback if parsing fails
                team_home, team_away = headline.split("-")
                center_text = "VS"
                status_text = "MATCH RESULT"
        else:
            # Preview
            if " vs " in headline:
                team_home, team_away = headline.split(" vs ")
            else:
                team_home = headline
                team_away = ""
            center_text = "VS"
            status_text = "UPCOMING MATCH"

        # 3. Drawing Layout
        cx = self.width // 2
        cy = self.height // 2

        # A. Status Badge (Top)
        draw.rectangle([(cx-200, 150), (cx+200, 220)], fill=(220, 38, 38)) # Red Badge
        draw.text((cx, 185), status_text, font=self._get_font(40), fill='white', anchor="mm")

        # B. Home Team (Top Half)
        # Wrap text if team name is long
        home_lines = textwrap.wrap(team_home, width=15)
        y_pos = cy - 250
        for line in home_lines:
            draw.text((cx, y_pos), line, font=self._get_font(80), fill='white', anchor="mm")
            y_pos += 90

        # C. The Score/VS (Middle)
        # Draw a Gold Box behind score
        draw.rectangle([(0, cy-100), (self.width, cy+100)], fill=(30, 41, 59))
        draw.line([(0, cy-100), (self.width, cy-100)], fill=(255, 215, 0), width=5)
        draw.line([(0, cy+100), (self.width, cy+100)], fill=(255, 215, 0), width=5)
        
        # Huge Text
        draw.text((cx, cy), center_text, font=self._get_font(150), fill=(255, 215, 0), anchor="mm")

        # D. Away Team (Bottom Half)
        away_lines = textwrap.wrap(team_away, width=15)
        y_pos = cy + 200
        for line in away_lines:
            draw.text((cx, y_pos), line, font=self._get_font(80), fill='white', anchor="mm")
            y_pos += 90

        # E. League Footer
        draw.text((cx, self.height - 100), league_name.upper(), font=self._get_font(50), fill=(148, 163, 184), anchor="mm")

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_file.name, quality=95)
        return temp_file.name

def create_pro_image(headline: str, source: str) -> str:
    generator = ImageGenerator()
    return generator.generate(headline, source)
