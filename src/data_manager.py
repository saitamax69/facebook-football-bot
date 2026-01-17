"""
Data Manager for JSON file storage
"""
import json
import os
from datetime import datetime, date, timedelta
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PREDICTIONS_FILE, STATS_FILE


class DataManager:
    """Manages prediction data and statistics"""
    
    def __init__(self):
        self.pred_file = PREDICTIONS_FILE
        self.stats_file = STATS_FILE
        self._init_files()
    
    def _init_files(self):
        """Create data files if needed"""
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(self.pred_file):
            self._write({'predictions': []}, self.pred_file)
        
        if not os.path.exists(self.stats_file):
            self._write({'total': 0, 'wins': 0, 'losses': 0}, self.stats_file)
    
    def _read(self, path):
        """Read JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _write(self, data, path):
        """Write JSON file"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_prediction(self, pred):
        """Save new prediction"""
        data = self._read(self.pred_file)
        if 'predictions' not in data:
            data['predictions'] = []
        data['predictions'].append(pred)
        self._write(data, self.pred_file)
        print(f"💾 Saved: {pred['home_team']} vs {pred['away_team']}")
    
    def get_todays_predictions(self):
        """Get today's predictions"""
        today = date.today().isoformat()
        data = self._read(self.pred_file)
        return [p for p in data.get('predictions', []) if p.get('date') == today]
    
    def get_pending_predictions(self, target_date=None):
        """Get pending predictions"""
        if not target_date:
            target_date = date.today().isoformat()
        data = self._read(self.pred_file)
        return [p for p in data.get('predictions', []) 
                if p.get('date') == target_date and p.get('status') == 'pending']
    
    def update_prediction_result(self, pred_id, result, score, profit):
        """Update prediction with result"""
        data = self._read(self.pred_file)
        for p in data.get('predictions', []):
            if p.get('id') == pred_id:
                p['status'] = 'settled'
                p['result'] = result
                p['final_score'] = score
                p['profit'] = profit
                break
        self._write(data, self.pred_file)
    
    def get_daily_stats(self, target_date=None):
        """Get daily stats"""
        if not target_date:
            target_date = date.today().isoformat()
        
        data = self._read(self.pred_file)
        preds = [p for p in data.get('predictions', []) 
                 if p.get('date') == target_date and p.get('status') == 'settled']
        
        wins = len([p for p in preds if p.get('result') == 'WIN'])
        losses = len([p for p in preds if p.get('result') == 'LOSS'])
        total = wins + losses
        hit_rate = round((wins / total * 100), 1) if total > 0 else 0
        profit = sum(p.get('profit', 0) for p in preds)
        
        return {
            'date': target_date,
            'total': total,
            'wins': wins,
            'losses': losses,
            'hit_rate': hit_rate,
            'profit': round(profit, 2)
        }
    
    def get_weekly_stats(self):
        """Get weekly stats"""
        data = self._read(self.pred_file)
        today = date.today()
        week_ago = (today - timedelta(days=7)).isoformat()
        
        preds = [p for p in data.get('predictions', []) 
                 if p.get('status') == 'settled' and p.get('date', '') >= week_ago]
        
        wins = len([p for p in preds if p.get('result') == 'WIN'])
        losses = len([p for p in preds if p.get('result') == 'LOSS'])
        total = wins + losses
        hit_rate = round((wins / total * 100), 1) if total > 0 else 0
        profit = sum(p.get('profit', 0) for p in preds)
        
        return {
            'wins': wins,
            'losses': losses,
            'hit_rate': hit_rate,
            'profit': round(profit, 2)
        }
    
    def generate_prediction_id(self):
        """Generate unique ID"""
        return f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def prediction_exists_today(self, post_num):
        """Check if post already exists today"""
        preds = self.get_todays_predictions()
        return any(p.get('post_number') == post_num for p in preds)
