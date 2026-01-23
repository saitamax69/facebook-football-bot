#!/usr/bin/env python3
"""Daily Results Post Script - Fixed"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from post_generator import PostGenerator
from data_manager import DataManager

def check(p, r):
    pred = p.get('prediction', '').lower()
    h = r.get('home_score', 0)
    a = r.get('away_score', 0)
    total = h + a
    
    if 'home' in pred: return h > a
    if 'away' in pred: return a > h
    if 'draw' in pred: return h == a
    if 'over 2.5' in pred: return total > 2.5
    return h > a

def main():
    print(f"{'='*50}")
    print(f"📊 Daily Results Processing")
    print(f"{'='*50}")
    
    dm = DataManager()
    odds = OddsAPIClient()
    gen = PostGenerator()
    fb = FacebookPoster()
    
    # 1. Get Pending Predictions (Try Today, then Yesterday)
    today = date.today().isoformat()
    preds = dm.get_pending_predictions(today)
    
    if not preds:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        print(f"ℹ️ No pending for today, checking yesterday ({yesterday})...")
        preds = dm.get_pending_predictions(yesterday)
        today = yesterday # Set date for stats context
    
    if not preds: 
        return print("✅ No pending predictions to process.")
    
    print(f"📋 Found {len(preds)} pending predictions")
    
    # 2. Check Results
    settled_preds = [] # List for finished games
    
    for p in preds:
        fixture_id = p.get('fixture_id')
        print(f"🔍 Checking: {p.get('home_team')} vs {p.get('away_team')}...")
        
        res = odds.get_match_result(fixture_id)
        
        if res and res.get('status') == 'finished':
            won = check(p, res)
            status = 'WIN' if won else 'LOSS'
            # Profit calc: (Odds - 1) for win, -1 for loss
            odds_val = float(p.get('odds', 1.0))
            prof = round(odds_val - 1, 2) if won else -1.0
            score = f"{res['home_score']}-{res['away_score']}"
            
            # Update Database
            dm.update_prediction_result(p['id'], status, score, prof)
            
            # Update Local Object for the Post
            p['result'] = status
            p['final_score'] = score
            p['profit'] = prof
            
            settled_preds.append(p)
            print(f"   ✅ Finished: {score} -> {status}")
        else:
            print(f"   ⏳ Match not finished yet.")

    # 3. Generate Post ONLY if we have results
    if not settled_preds:
        return print("⚠️ No matches finished yet. Skipping post.")

    print("\n📊 Calculating stats...")
    stats = dm.get_daily_stats(today)
    
    print("\n📝 Generating post...")
    post = gen.generate_results_post(settled_preds, stats)
    
    print("\n📤 Posting...")
    fb.post_to_page(post)
    print("✅ Daily Results Done!")

if __name__ == "__main__":
    main()
