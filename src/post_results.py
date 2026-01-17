#!/usr/bin/env python3
"""Daily Results Post Script - Runs at 23:00 UTC"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from post_generator import PostGenerator
from data_manager import DataManager


def check_result(pred, result):
    """Check if prediction won"""
    p = pred.get('prediction', '').lower()
    h = result.get('home_score', 0)
    a = result.get('away_score', 0)
    total = h + a
    
    if 'home win' in p: return h > a
    if 'away win' in p: return a > h
    if 'draw' in p and 'or' not in p: return h == a
    if 'home or draw' in p: return h >= a
    if 'away or draw' in p: return a >= h
    if 'over 2.5' in p: return total > 2.5
    if 'under 2.5' in p: return total < 2.5
    if 'btts yes' in p: return h > 0 and a > 0
    return h > a


def main():
    print(f"{'='*50}")
    print(f"📊 Daily Results")
    print(f"📅 {date.today()}")
    print(f"{'='*50}")
    
    dm = DataManager()
    odds = OddsAPIClient()
    gen = PostGenerator()
    fb = FacebookPoster()
    
    today = date.today().isoformat()
    
    try:
        print("\n📋 Getting predictions...")
        preds = dm.get_pending_predictions(today)
        
        if not preds:
            print("⚠️ No pending predictions")
            return
        
        print(f"✅ Found {len(preds)} predictions")
        
        print("\n🔍 Fetching results...")
        for p in preds:
            print(f"   {p['home_team']} vs {p['away_team']}...")
            
            result = odds.get_match_result(p.get('fixture_id', ''))
            score = f"{result['home_score']}-{result['away_score']}"
            won = check_result(p, result)
            res = 'WIN' if won else 'LOSS'
            profit = round(p.get('odds', 1.5) - 1, 2) if won else -1.0
            
            dm.update_prediction_result(p['id'], res, score, profit)
            
            p['result'] = res
            p['final_score'] = score
            p['profit'] = profit
            p['status'] = 'settled'
            
            print(f"   {'✅' if won else '❌'} {score} - {res}")
        
        print("\n📊 Calculating stats...")
        stats = dm.get_daily_stats(today)
        stats['weekly'] = dm.get_weekly_stats()
        
        print(f"   {stats['wins']}W - {stats['losses']}L ({stats['hit_rate']}%)")
        
        print("\n📝 Generating post...")
        post = gen.generate_results_post(preds, stats)
        
        print("\n📤 Posting...")
        fb.post_to_page(post)
        print("✅ Done!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
