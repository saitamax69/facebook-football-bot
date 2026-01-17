"""
Data Manager for storing and retrieving predictions and stats.
Uses JSON file storage for persistence between GitHub Actions runs.
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import PREDICTIONS_FILE, STATS_FILE
except ImportError:
    from config import PREDICTIONS_FILE, STATS_FILE


class DataManager:
    """
    Manager for prediction and statistics data storage.
    Handles JSON file operations for persistence.
    """
    
    def __init__(self):
        """Initialize the data manager and ensure files exist."""
        self.predictions_file = PREDICTIONS_FILE
        self.stats_file = STATS_FILE
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create data directory and files if they don't exist."""
        # Create data directory
        os.makedirs('data', exist_ok=True)
        
        # Create predictions file
        if not os.path.exists(self.predictions_file):
            print(f"📁 Creating {self.predictions_file}")
            self._write_json(self.predictions_file, {'predictions': []})
        
        # Create stats file
        if not os.path.exists(self.stats_file):
            print(f"📁 Creating {self.stats_file}")
            self._write_json(self.stats_file, {
                'total_predictions': 0,
                'total_wins': 0,
                'total_losses': 0,
                'total_pending': 0,
                'overall_profit': 0.0,
                'win_rate': 0.0,
                'daily_stats': {},
                'last_updated': datetime.now().isoformat()
            })
    
    def _read_json(self, filepath: str) -> Dict:
        """
        Read and parse a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Parsed JSON data as dictionary
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ File not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error in {filepath}: {e}")
            return {}
        except Exception as e:
            print(f"⚠️ Error reading {filepath}: {e}")
            return {}
    
    def _write_json(self, filepath: str, data: Dict):
        """
        Write data to a JSON file.
        
        Args:
            filepath: Path to the JSON file
            data: Dictionary to write
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            print(f"💾 Saved to {filepath}")
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
    
    def save_prediction(self, prediction_data: Dict):
        """
        Save a new prediction to storage.
        
        Args:
            prediction_data: Dictionary containing prediction details:
                - id: Unique prediction ID
                - date: Date string (YYYY-MM-DD)
                - post_number: 1-5 indicating which post of the day
                - risk_level: SAFE, MODERATE, or RISKY
                - league: League name
                - home_team: Home team name
                - away_team: Away team name
                - prediction: The actual prediction (e.g., "Home Win")
                - odds: Decimal odds
                - confidence: Confidence percentage
                - fixture_id: API fixture ID
                - status: pending, settled
                - result: None, WIN, or LOSS
                - final_score: Final score string (e.g., "2-1")
                - profit: Profit/loss in units
        """
        print(f"💾 Saving prediction: {prediction_data.get('prediction')} for {prediction_data.get('home_team')} vs {prediction_data.get('away_team')}")
        
        data = self._read_json(self.predictions_file)
        
        if 'predictions' not in data:
            data['predictions'] = []
        
        # Add timestamp
        prediction_data['created_at'] = datetime.now().isoformat()
        
        data['predictions'].append(prediction_data)
        self._write_json(self.predictions_file, data)
        
        # Update stats
        self._update_stats_on_new_prediction()
    
    def _update_stats_on_new_prediction(self):
        """Update stats when a new prediction is added."""
        stats = self._read_json(self.stats_file)
        stats['total_predictions'] = stats.get('total_predictions', 0) + 1
        stats['total_pending'] = stats.get('total_pending', 0) + 1
        stats['last_updated'] = datetime.now().isoformat()
        self._write_json(self.stats_file, stats)
    
    def get_todays_predictions(self) -> List[Dict]:
        """
        Get all predictions for today.
        
        Returns:
            List of prediction dictionaries for today
        """
        today = date.today().isoformat()
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        todays = [p for p in predictions if p.get('date') == today]
        print(f"📋 Found {len(todays)} predictions for today ({today})")
        
        return todays
    
    def get_pending_predictions(self, target_date: Optional[str] = None) -> List[Dict]:
        """
        Get predictions that are still pending results.
        
        Args:
            target_date: Optional date string (YYYY-MM-DD), defaults to today
            
        Returns:
            List of pending prediction dictionaries
        """
        if target_date is None:
            target_date = date.today().isoformat()
        
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        pending = [
            p for p in predictions 
            if p.get('date') == target_date and p.get('status') == 'pending'
        ]
        
        print(f"📋 Found {len(pending)} pending predictions for {target_date}")
        return pending
    
    def get_predictions_by_date(self, target_date: str) -> List[Dict]:
        """
        Get all predictions for a specific date.
        
        Args:
            target_date: Date string (YYYY-MM-DD)
            
        Returns:
            List of prediction dictionaries
        """
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        return [p for p in predictions if p.get('date') == target_date]
    
    def update_prediction_result(self, prediction_id: str, result: str, 
                                 final_score: str, profit: float):
        """
        Update a prediction with its result.
        
        Args:
            prediction_id: The prediction's unique ID
            result: 'WIN' or 'LOSS'
            final_score: Final score string (e.g., "2-1")
            profit: Profit/loss in units
        """
        print(f"📝 Updating prediction {prediction_id}: {result} ({final_score})")
        
        data = self._read_json(self.predictions_file)
        
        for pred in data.get('predictions', []):
            if pred.get('id') == prediction_id:
                pred['status'] = 'settled'
                pred['result'] = result
                pred['final_score'] = final_score
                pred['profit'] = profit
                pred['settled_at'] = datetime.now().isoformat()
                break
        
        self._write_json(self.predictions_file, data)
        
        # Update stats
        self._update_stats_on_result(result, profit)
    
    def _update_stats_on_result(self, result: str, profit: float):
        """Update stats when a prediction is settled."""
        stats = self._read_json(self.stats_file)
        
        if result == 'WIN':
            stats['total_wins'] = stats.get('total_wins', 0) + 1
        else:
            stats['total_losses'] = stats.get('total_losses', 0) + 1
        
        stats['total_pending'] = max(0, stats.get('total_pending', 0) - 1)
        stats['overall_profit'] = round(stats.get('overall_profit', 0) + profit, 2)
        
        # Calculate win rate
        total_settled = stats.get('total_wins', 0) + stats.get('total_losses', 0)
        if total_settled > 0:
            stats['win_rate'] = round((stats.get('total_wins', 0) / total_settled) * 100, 1)
        
        stats['last_updated'] = datetime.now().isoformat()
        self._write_json(self.stats_file, stats)
    
    def get_daily_stats(self, target_date: Optional[str] = None) -> Dict:
        """
        Get statistics for a specific date.
        
        Args:
            target_date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with daily statistics
        """
        if target_date is None:
            target_date = date.today().isoformat()
        
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        day_preds = [
            p for p in predictions 
            if p.get('date') == target_date and p.get('status') == 'settled'
        ]
        
        wins = len([p for p in day_preds if p.get('result') == 'WIN'])
        losses = len([p for p in day_preds if p.get('result') == 'LOSS'])
        total = wins + losses
        
        hit_rate = (wins / total * 100) if total > 0 else 0
        profit = sum(p.get('profit', 0) for p in day_preds)
        
        return {
            'date': target_date,
            'total': total,
            'wins': wins,
            'losses': losses,
            'hit_rate': round(hit_rate, 1),
            'profit': round(profit, 2),
            'predictions': day_preds
        }
    
    def get_weekly_stats(self) -> Dict:
        """
        Get statistics for the current week (last 7 days).
        
        Returns:
            Dictionary with weekly statistics
        """
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        week_preds = [
            p for p in predictions 
            if p.get('status') == 'settled'
            and week_ago.isoformat() <= p.get('date', '') <= today.isoformat()
        ]
        
        wins = len([p for p in week_preds if p.get('result') == 'WIN'])
        losses = len([p for p in week_preds if p.get('result') == 'LOSS'])
        total = wins + losses
        
        hit_rate = (wins / total * 100) if total > 0 else 0
        profit = sum(p.get('profit', 0) for p in week_preds)
        
        return {
            'total': total,
            'wins': wins,
            'losses': losses,
            'hit_rate': round(hit_rate, 1),
            'profit': round(profit, 2)
        }
    
    def get_monthly_stats(self) -> Dict:
        """
        Get statistics for the current month.
        
        Returns:
            Dictionary with monthly statistics
        """
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        today = date.today()
        month_start = today.replace(day=1)
        
        month_preds = [
            p for p in predictions 
            if p.get('status') == 'settled'
            and p.get('date', '') >= month_start.isoformat()
        ]
        
        wins = len([p for p in month_preds if p.get('result') == 'WIN'])
        losses = len([p for p in month_preds if p.get('result') == 'LOSS'])
        total = wins + losses
        
        hit_rate = (wins / total * 100) if total > 0 else 0
        profit = sum(p.get('profit', 0) for p in month_preds)
        
        return {
            'total': total,
            'wins': wins,
            'losses': losses,
            'hit_rate': round(hit_rate, 1),
            'profit': round(profit, 2)
        }
    
    def get_overall_stats(self) -> Dict:
        """
        Get overall statistics.
        
        Returns:
            Dictionary with overall statistics
        """
        return self._read_json(self.stats_file)
    
    def generate_prediction_id(self) -> str:
        """
        Generate a unique prediction ID.
        
        Returns:
            Unique ID string
        """
        import time
        return f"{date.today().isoformat()}_{int(time.time() * 1000)}"
    
    def prediction_exists_today(self, post_number: int) -> bool:
        """
        Check if a prediction for the given post number already exists today.
        
        Args:
            post_number: The post number (1-5)
            
        Returns:
            True if prediction exists, False otherwise
        """
        today_preds = self.get_todays_predictions()
        exists = any(p.get('post_number') == post_number for p in today_preds)
        
        if exists:
            print(f"⚠️ Prediction #{post_number} already exists for today")
        
        return exists
    
    def get_last_n_predictions(self, n: int = 10) -> List[Dict]:
        """
        Get the last N predictions.
        
        Args:
            n: Number of predictions to return
            
        Returns:
            List of prediction dictionaries
        """
        data = self._read_json(self.predictions_file)
        predictions = data.get('predictions', [])
        
        # Sort by created_at descending
        sorted_preds = sorted(
            predictions, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        return sorted_preds[:n]
    
    def cleanup_old_predictions(self, days: int = 30):
        """
        Remove predictions older than specified days.
        
        Args:
            days: Number of days to keep
        """
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        
        data = self._read_json(self.predictions_file)
        original_count = len(data.get('predictions', []))
        
        data['predictions'] = [
            p for p in data.get('predictions', [])
            if p.get('date', '') >= cutoff
        ]
        
        removed_count = original_count - len(data['predictions'])
        
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old predictions")
            self._write_json(self.predictions_file, data)


# For testing
if __name__ == "__main__":
    dm = DataManager()
    
    # Test save prediction
    test_pred = {
        'id': dm.generate_prediction_id(),
        'date': date.today().isoformat(),
        'post_number': 99,  # Test post
        'risk_level': 'SAFE',
        'league': 'Test League',
        'home_team': 'Test Home',
        'away_team': 'Test Away',
        'prediction': 'Home Win',
        'odds': 1.50,
        'confidence': 85,
        'fixture_id': 'test_123',
        'status': 'pending',
        'result': None,
        'final_score': None,
        'profit': None
    }
    
    dm.save_prediction(test_pred)
    
    # Test get today's predictions
    today_preds = dm.get_todays_predictions()
    print(f"\nToday's predictions: {len(today_preds)}")
    
    # Test stats
    stats = dm.get_daily_stats()
    print(f"Daily stats: {stats}")
