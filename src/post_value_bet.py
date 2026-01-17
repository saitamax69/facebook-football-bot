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

def main(num):
    print(f"🟡 Value Bet #{num}")
    dm = DataManager()
    if dm.prediction_exists_today(num): return print("⚠️ Exists")
    
    odds = OddsAPIClient()
    fix = odds.get_upcoming_fixtures()
    if not fix: return print("❌ No fixtures")
    
    ana = MatchAnalyzer(odds)
    match, analysis = ana.find_value_bet_match(fix)
    if not match: return print("❌ No match")
    
    gen = PostGenerator()
    post = gen.generate_value_bet_post(match, analysis, num)
    
    fb = FacebookPoster()
    pid = fb.post_to_page(post)
    
    if pid:
        dm.save_prediction({
            'id': dm.generate_prediction_id(),
            'date': date.today().isoformat(),
            'post_number': num,
            'risk_level': 'MODERATE',
            'league': match['league'],
            'home_team': match['home_team'],
            'away_team': match['away_team'],
            'prediction': analysis['prediction'],
            'odds': analysis['odds'],
            'fixture_id': match['fixture_id'],
            'status': 'pending'
        })

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 3)
