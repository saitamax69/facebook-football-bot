#!/usr/bin/env python3
"""
Daily Results Post Script
Runs via GitHub Actions at 23:00 UTC (end of day)
"""

import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from odds_api import OddsAPIClient
from facebook_api import FacebookPoster
from post_generator import PostGenerator
from data_manager import DataManager


def check_prediction_result(prediction, result_data):
    """
    Check if prediction was correct based on result
    """
    pred_type = prediction.get('prediction', '').lower()
    home_score = result_data.get('home_score', 0)
    away_score = result_data.get('away_score', 0)
    total_goals = home_score + away_score
    
    # 1X2
    if 'home win' in pred_type:
        return home_score > away_score
    elif 'away win' in pred_type:
        return away_score > home_score
    elif 'draw' == pred_type:  # strict draw
        return home_score == away_score
    
    # Double Chance
    elif 'home or draw' in pred_type:
        return home_score >= away_score
    elif 'away or draw' in pred_type:
        return away_score >= home_score
    elif 'home or away' in pred_type:
        return home_score != away_score

    # Goals
    elif 'over 2.5' in pred_type:
        return total_goals > 2.5
    elif 'under 2.5' in pred_type:
        return total_goals < 2.5
    elif 'over 1.5' in pred_type:
        return total_goals > 1.5
    elif 'under 3.5' in pred_type:
        return total_goals < 3.5

    # BTTS
    elif 'btts yes' in pred_type:
        return home_score > 0 and away_score > 0
    elif 'btts no' in pred_type:
        return home_score == 0 or away_score == 0
    
    # Default fallback
    return home_score > away_score


def main():
    print(f"{'='*60}")
    print(f"📊 Daily Results Processing")
    print(f"📅 Date: {date.today().isoformat()}")
    print(f"{'='*60}")
    
    dm = DataManager()
    odds_client = OddsAPIClient()
    post_gen = PostGenerator()
    fb_poster = FacebookPoster()
    
    # 1. Get predictions for TODAY (since we run at 23:00)
    today = date.today().isoformat()
    # Also check yesterday just in case we missed a run or timezone issues
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Prioritize today's settled/pending items
    pending_preds = dm.get_pending_predictions(today)
    if not pending_preds:
        print(f"ℹ️ No pending predictions for today ({today}). Checking yesterday ({yesterday})...")
        pending_preds = dm.get_pending_predictions(yesterday)
        report_date = yesterday
    else:
        report_date = today

    if not pending_preds:
        # Maybe they are already settled?
        # If running manually multiple times, we might want to repost settled results?
        # But for automation, let's assume we process pending ones.
        # Actually, let's grab SETTLED ones for the stats check too.
        pass

    # We need ALL predictions for the target date to count wins (both pending & already settled)
    # Re-fetch all predictions for that date
    all_preds_for_date = []
    # This part requires DataManager to support 'get_all_for_date' or we filter manually
    # Let's filter manually from file to be safe
    all_data = dm._read(dm.pred_file)
    if all_data and 'predictions' in all_data:
        all_preds_for_date = [p for p in all_data['predictions'] if p.get('date') == report_date]

    if not all_preds_for_date:
        print("❌ No predictions found for this date. Exiting.")
        return

    print(f"📋 Found {len(all_preds_for_date)} predictions for {report_date}")

    # 2. Update results for any that are still pending
    updated_count = 0
    for pred in all_preds_for_date:
        if pred.get('status') != 'settled':
            print(f"🔍 Checking result: {pred.get('home_team')} vs {pred.get('away_team')}...")
            fixture_id = pred.get('fixture_id')
            
            # Fetch result from API
            res = odds_client.get_match_result(fixture_id)
            
            if res and res.get('status') == 'finished':
                won = check_prediction_result(pred, res)
                result_status = 'WIN' if won else 'LOSS'
                
                # Profit calc
                dec_odds = float(pred.get('odds', 0))
                profit = round(dec_odds - 1, 2) if won else -1.0
                
                final_score = f"{res['home_score']}-{res['away_score']}"
                
                # Save to DB
                dm.update_prediction_result(pred['id'], result_status, final_score, profit)
                
                # Update local object
                pred['status'] = 'settled'
                pred['result'] = result_status
                pred['final_score'] = final_score
                pred['profit'] = profit
                updated_count += 1
                print(f"   ✅ {result_status} ({final_score})")
            else:
                print(f"   ⏳ Match not finished/found.")
    
    # 3. Calculate Stats for the Day
    # Filter only settled predictions for the final report
    settled_preds = [p for p in all_preds_for_date if p.get('status') == 'settled']
    
    if not settled_preds:
        print("⚠️ No settled results available yet.")
        return

    wins = sum(1 for p in settled_preds if p.get('result') == 'WIN')
    total = len(settled_preds)
    losses = total - wins
    
    daily_profit = sum(p.get('profit', 0) for p in settled_preds)
    
    print(f"\n📊 Day Stats: {wins} Wins / {total} Total")
    
    # ---------------------------------------------------------
    # 🛑 THRESHOLD CHECK: ONLY POST IF WINS >= 3
    # ---------------------------------------------------------
    # You asked: "not post if there is not at least 3 from 5 win"
    # We'll adapt logic: if wins < 3, skip post.
    # Note: If total < 3 (e.g. only 2 games finished), we might want to wait?
    # Or strict: wins must be >= 3.
    
    if wins < 3:
        print(f"⛔ SKIPPING POST: Win count ({wins}) is less than 3.")
        return

    # 4. Generate & Post
    print(f"✅ Threshold met ({wins} wins). Generating post...")
    
    # Prepare stats dict for generator
    stats = {
        'date': report_date,
        'wins': wins,
        'losses': losses,
        'hit_rate': int((wins/total)*100) if total > 0 else 0,
        'profit': round(daily_profit, 2)
    }
    
    # Get weekly stats too
    stats['weekly'] = dm.get_weekly_stats()

    post_content = post_gen.generate_results_post(settled_preds, stats)
    
    print("\n📤 Posting to Facebook...")
    post_id = fb_poster.post_to_page(post_content)
    
    if post_id:
        print(f"✅ Results posted successfully! ID: {post_id}")
    else:
        print("❌ Failed to post results to Facebook")


if __name__ == "__main__":
    main()
