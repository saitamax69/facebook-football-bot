#!/usr/bin/env python3
import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from post_generator import PostGenerator
from data_manager import DataManager

def check(p, r):
    pred = p.lower()
    h, a = r['home_score'], r['away_score']
    if 'home' in pred: return h > a
    if 'away' in pred: return a > h
    if 'draw' in pred: return h == a
    return h > a

def main():
    print("📊 Daily Results")
    dm = DataManager()
    odds = OddsAPIClient()
    
    # Check today and yesterday
    today = date.today().isoformat()
    preds = dm.get_pending_predictions(today)
    
    if not preds:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        preds = dm.get_pending_predictions(yesterday)
        today = yesterday
    
    if not preds: return print("⚠️ No pending predictions")
    
    for p in preds:
        res = odds.get_match_result(p['fixture_id'])
        if res['status'] == 'finished':
            won = check(p['prediction'], res)
            status = 'WIN' if won else 'LOSS'
            prof = round(p['odds'] - 1, 2) if won else -1.0
            score = f"{res['home_score']}-{res['away_score']}"
            dm.update_prediction_result(p['id'], status, score, prof)
    
    stats = dm.get_daily_stats(today)
    gen = PostGenerator()
    post = gen.generate_results_post(preds, stats) # Pass modified list? Ideally reload
    
    # Reload settled for post
    fb = FacebookPoster()
    fb.post_to_page(post)

if __name__ == "__main__":
    main()
