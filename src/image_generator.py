"""
Premium Broadcast Image Generator.
Style: Professional Sports Dark Mode (ESPN/Sky Style)
"""

import logging
import textwrap
import tempfile
import hashlib
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1080
        # Standard Ubuntu font path for GitHub Actions
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        # Professional League Color Palettes
        self.THEMES = {
            "premier":    {"accent": (0, 255, 133), "name": "PREMIER LEAGUE"},
            "champions":  {"accent": (0, 112, 255), "name": "CHAMPIONS LEAGUE"},
            "liga":       {"accent": (255, 75, 0),  "name": "LA LIGA"},
            "bundes":     {"accent": (226, 0, 15),  "name": "BUNDESLIGA"},
            "serie":      {"accent": (0, 140, 255), "name": "SERIE A"},
            "default":    {"accent": (255, 215, 0), "name": "FOOTBALL UPDATE"},
        }

    def _get_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except OSError:
            return ImageFont.load_default()

    def _get_theme(self, league_name):
        lname = league_name.lower()
        for key, config in self.THEMES.items():
            if key in lname:
                return config
        return self.THEMES["default"]

    def _draw_team_section(self, draw, team_name, x_center, y_center):
        """Draws a professional team initial circle and the team name."""
        # Generate a unique professional color for the team circle
        hash_val = int(hashlib.sha256(team_name.encode('utf-8')).hexdigest(), 16)
        hue_r = (hash_val & 0x7F) + 50  # Muted professional tones
        hue_g = ((hash_val >> 8) & 0x7F) + 50
        hue_b = ((hash_val >> 16) & 0x7F) + 50

        # Draw Badge Circle
        radius = 110
        draw.ellipse([x_center - radius, y_center - radius, x_center + radius, y_center + radius], 
                     fill=(hue_r, hue_g, hue_b), outline=(255, 255, 255), width=4)
        
        # Draw Initial
        initial = team_name[0].upper()
        draw.text((x_center, y_center - 5), initial, font=self._get_font(100), fill=(255, 255, 255), anchor="mm")

        # Draw Team Name below badge
        name_lines = textwrap.wrap(team_name.upper(), width=12)
        y_text = y_center + radius + 50
        for line in name_lines:
            draw.text((x_center, y_text), line, font=self._get_font(50), fill=(255, 255, 255), anchor="mm")
            y_text += 60

    def generate(self, headline: str, league_name: str) -> str:
        theme = self._get_theme(league_name)
        
        # 1. Create Base Image (Deep Slate Dark Mode)
        img = Image.new('RGB', (self.width, self.height), color=(18, 24, 33))
        draw = ImageDraw.Draw(img)
        
        # 2. Draw Subtle Background Detail (Right side lighter)
        for i in range(self.width // 2, self.width):
            alpha = int((i - self.width // 2) / (self.width // 2) * 15)
            draw.line([(i, 0), (i, self.height)], fill=(255, 255, 255, alpha))

        # 3. Parse News Data
        home_team, away_team, score_text, status = "HOME", "AWAY", "VS", "UPCOMING"
        
        if "-" in headline and any(c.isdigit() for c in headline):
            try:
                parts = headline.split("-")
                left = parts[0].rsplit(" ", 1)
                right = parts[1].lstrip().split(" ", 1)
                home_team, home_score = left[0].strip(), left[1].strip()
                away_score, away_team = right[0].strip(), right[1].strip()
                score_text = f"{home_score} - {away_score}"
                status = "FULL TIME"
            except:
                pass
        elif " vs " in headline:
            home_team, away_team = headline.split(" vs ", 1)
            status = "KICK OFF"

        # 4. Draw Header (League & Status)
        # Accent Top Bar
        draw.rectangle([0, 0, self.width, 15], fill=theme["accent"])
        
        # Status Pill
        draw.rectangle([self.width//2 - 140, 60, self.width//2 + 140, 110], fill=(255, 255, 255))
        draw.text((self.width//2, 82), status, font=self._get_font(35), fill=(0, 0, 0), anchor="mm")
        
        # League Name
        draw.text((self.width//2, 160), theme["name"], font=self._get_font(40), fill=(180, 180, 180), anchor="mm")

        # 5. Draw Central Score Area
        cy = self.height // 2 - 50
        cx = self.width // 2
        
        # The Score Box
        draw.rectangle([cx - 180, cy - 100, cx + 180, cy + 100], fill=(28, 36, 48), outline=(theme["accent"]), width=3)
        draw.text((cx, cy - 5), score_text, font=self._get_font(150), fill=(255, 255, 255), anchor="mm")

        # 6. Draw Team Sections
        # Home (Left)
        self._draw_team_section(draw, home_team, cx - 340, cy)
        # Away (Right)
        self._draw_team_section(draw, away_team, cx + 340, cy)

        # 7. Draw Footer Decor
        draw.rectangle([0, self.height - 100, self.width, self.height], fill=(12, 16, 23))
        draw.text((self.width // 2, self.height - 50), "GLOBAL SCORE UPDATES", font=self._get_font(30), fill=(100, 100, 100), anchor="mm")

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(temp_file.name)
        return temp_file.name

def create_pro_image(headline: str, source: str) -> str:
    generator = ImageGenerator()
    return generator.generate(headline, source)
