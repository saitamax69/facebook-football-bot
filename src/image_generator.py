"""
Professional Dynamic Image Generator.
Features: League-specific themes, pattern backgrounds, and team avatars.
"""

import logging
import textwrap
import tempfile
import random
import hashlib
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1080
        # System font path (Guaranteed on GitHub Actions/Ubuntu)
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        # --- THEMES: Colors for specific leagues ---
        self.THEMES = {
            "premier":    {"bg_top": (56, 0, 60),    "bg_bot": (0, 255, 133), "accent": (255, 255, 255)}, # EPL Purple/Neon
            "champions":  {"bg_top": (10, 20, 60),   "bg_bot": (0, 0, 30),    "accent": (255, 0, 100)},   # UCL Midnight
            "liga":       {"bg_top": (255, 75, 0),   "bg_bot": (20, 20, 20),  "accent": (255, 255, 0)},   # La Liga Orange
            "bundes":     {"bg_top": (200, 0, 0),    "bg_bot": (20, 20, 20),  "accent": (255, 255, 255)}, # Bundesliga Red
            "serie":      {"bg_top": (0, 100, 200),  "bg_bot": (255, 255, 255), "accent": (0, 255, 0)},   # Serie A Blue
            "default":    {"bg_top": (15, 23, 42),   "bg_bot": (30, 41, 59),  "accent": (255, 215, 0)},   # Navy/Gold
        }

    def _get_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except OSError:
            return ImageFont.load_default()

    def _get_theme(self, league_name):
        """Selects colors based on the league name."""
        lname = league_name.lower()
        if "premier" in lname: return self.THEMES["premier"]
        if "champions" in lname or "ucl" in lname: return self.THEMES["champions"]
        if "liga" in lname: return self.THEMES["liga"]
        if "bundes" in lname: return self.THEMES["bundes"]
        if "serie" in lname: return self.THEMES["serie"]
        return self.THEMES["default"]

    def _generate_team_avatar(self, team_name, size=200):
        """Generates a colored circle with the team's first letter."""
        # Deterministic color based on team name hash
        hash_val = int(hashlib.sha256(team_name.encode('utf-8')).hexdigest(), 16)
        r = (hash_val & 0xFF0000) >> 16
        g = (hash_val & 0x00FF00) >> 8
        b = (hash_val & 0x0000FF)
        
        # Ensure color isn't too dark or too light
        r = min(max(r, 50), 220)
        g = min(max(g, 50), 220)
        b = min(max(b, 50), 220)
        
        img = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        
        # Draw Circle
        draw.ellipse([0, 0, size, size], fill=(r, g, b), outline=(255,255,255), width=5)
        
        # Draw Letter
        initial = team_name[0].upper()
        # Find a good font size
        font_size = int(size * 0.6)
        font = self._get_font(font_size)
        
        # Center the letter
        draw.text((size//2, size//2), initial, font=font, fill=(255,255,255), anchor="mm")
        
        return img

    def generate(self, headline: str, league_name: str) -> str:
        theme = self._get_theme(league_name)
        
        # 1. Background Gradient
        img = Image.new('RGB', (self.width, self.height), color=theme["bg_top"])
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            # Linear interpolation between top and bot colors
            ratio = y / self.height
            r = int(theme["bg_top"][0] * (1 - ratio) + theme["bg_bot"][0] * ratio)
            g = int(theme["bg_top"][1] * (1 - ratio) + theme["bg_bot"][1] * ratio)
            b = int(theme["bg_top"][2] * (1 - ratio) + theme["bg_bot"][2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 2. Add subtle pattern (Diagonal lines)
        for i in range(0, self.width + self.height, 40):
            draw.line([(i, 0), (0, i)], fill=(255, 255, 255, 20), width=1)

        # 3. Parse Data
        # Default values
        home_team = "Home Team"
        away_team = "Away Team"
        center_text = "VS"
        status_text = "MATCHDAY"

        if "-" in headline and any(c.isdigit() for c in headline):
            # Result: "Man City 3-1 Arsenal"
            try:
                parts = headline.split("-")
                left = parts[0].rsplit(" ", 1)
                right = parts[1].lstrip().split(" ", 1)
                home_team = left[0].strip()
                home_score = left[1].strip()
                away_score = right[0].strip()
                away_team = right[1].strip()
                center_text = f"{home_score} - {away_score}"
                status_text = "FULL TIME"
            except:
                home_team, away_team = headline.split("-", 1)
        elif " vs " in headline:
            # Preview
            home_team, away_team = headline.split(" vs ")
            status_text = "UPCOMING"

        cx = self.width // 2
        cy = self.height // 2

        # 4. Draw Layout
        
        # A. Status Badge (Top)
        draw.rectangle([(cx-250, 100), (cx+250, 180)], fill=(0, 0, 0, 150))
        draw.text((cx, 140), status_text, font=self._get_font(40), fill=theme["accent"], anchor="mm")

        # B. Center Scoreboard (Glass Effect)
        # Semi-transparent box in middle
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        draw_over = ImageDraw.Draw(overlay)
        draw_over.rectangle([(100, cy-120), (self.width-100, cy+120)], fill=(0, 0, 0, 100))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)

        # C. Score/VS
        draw.text((cx, cy), center_text, font=self._get_font(160), fill=theme["accent"], anchor="mm")

        # D. Home Team (Left/Top section)
        # Avatar
        home_avatar = self._generate_team_avatar(home_team)
        img.paste(home_avatar, (cx - 350, cy - 350), home_avatar)
        
        # Name
        h_lines = textwrap.wrap(home_team, width=15)
        y_h = cy - 420
        for line in reversed(h_lines): # Draw upwards from avatar
            draw.text((cx - 250, y_h), line, font=self._get_font(60), fill='white', anchor="mm")
            y_h -= 70

        # E. Away Team (Right/Bottom section)
        # Avatar
        away_avatar = self._generate_team_avatar(away_team)
        img.paste(away_avatar, (cx + 150, cy + 150), away_avatar)
        
        # Name
        a_lines = textwrap.wrap(away_team, width=15)
        y_a = cy + 400
        for line in a_lines:
            draw.text((cx + 250, y_a), line, font=self._get_font(60), fill='white', anchor="mm")
            y_a += 70

        # F. League Footer
        draw.text((cx, self.height - 80), league_name.upper(), font=self._get_font(40), fill=(200, 200, 200), anchor="mm")

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(temp_file.name)
        return temp_file.name

# --- THIS WAS MISSING IN THE PREVIOUS MESSAGE ---
def create_pro_image(headline: str, source: str) -> str:
    generator = ImageGenerator()
    return generator.generate(headline, source)
