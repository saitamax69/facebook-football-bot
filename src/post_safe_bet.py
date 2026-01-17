#!/usr/bin/env python3
"""Safe Bet Post Script - Runs at 07:00 and 09:00 UTC"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from match_analyzer import MatchAnalyzer
from post_generator import PostGenerator
from data_manager import DataManager


def main(post_number):
    print(f"{'='*50}")
    print(f"🟢 Safe Bet #{post_number}")
    print(f"📅 {date.today()}")
    print(f"{'='*50}")
    
    dm = DataManager()
    odds = OddsAPIClient()
    analyzer = MatchAnalyzer(odds)
    gen = PostGenerator()
    fb = FacebookPoster()
    
    if dm.prediction_exists_today(post_number):
        print(f"⚠️ Already posted #{post_number} today")
        return
    
    try:
        print("\n📡 Fetching fixtures...")
        fixtures = odds.get_upcoming_fixtures()
        
        if not fixtures:
            print("❌ No fixtures")
            return
        
        print(f"✅ Found {len(fixtures)} fixtures")
        
        print("\n🔍 Analyzing...")
        match, analysis = analyzer.find_safe_bet_match(fixtures)
        
        if not match:
            print("❌ No suitable match")
            return
        
        print(f"✅ {match['home_team']} vs {match['away_team']}")
        print(f"   Pick: {analysis['prediction']} @ {analysis['odds']}")
        
        print("\n📝 Generating post...")
        post = gen.generate_safe_bet_post(match, analysis, post_number)
        
        print("\n📤 Posting...")
        post_id = fb.post_to_page(post)
        
        if post_id:
            dm.save_prediction({
                'id': dm.generate_prediction_id(),
                'date': date.today().isoformat(),
                'post_number': post_number,
                'risk_level': 'SAFE',
                'league': match['league'],
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'prediction': analysis['prediction'],
                'odds': analysis['odds'],
                'confidence': analysis['confidence'],
                'fixture_id': match['fixture_id'],
                'status': 'pending',
                'result': None,
                'final_score': None,
                'profit': None,
                'fb_post_id': post_id
            })
            print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(num)
