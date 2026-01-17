#!/usr/bin/env python3
import sys
import os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from match_analyzer import MatchAnalyzer
from post_generator import PostGenerator
from data_manager import DataManager

def main():
    print(f"🔴 Risky Bet #5")
    dm = DataManager()
    if dm.prediction_exists_today(5): return print("⚠️ Exists")
    
    odds = OddsAPIClient()
    fix = odds.get_upcoming_fixtures()
    if not fix: return print("❌ No fixtures")
    
    ana = MatchAnalyzer(odds)
    match, analysis = ana.find_risky_bet_match(fix)
    if not match: return print("❌ No match")
    
    gen = PostGenerator()
    post = gen.generate_risky_bet_post(match, analysis)
    
    fb = FacebookPoster()
    pid = fb.post_to_page(post)
    
    if pid:
        dm.save_prediction({
            'id': dm.generate_prediction_id(),
            'date': date.today().isoformat(),
            'post_number': 5,
            'risk_level': 'RISKY',
            'league': match['league'],
            'home_team': match['home_team'],
            'away_team': match['away_team'],
            'prediction': analysis['prediction'],
            'odds': analysis['odds'],
            'fixture_id': match['fixture_id'],
            'status': 'pending'
        })

if __name__ == "__main__":
    main()
