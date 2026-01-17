"""
Data Manager
"""
import json
import os
from datetime import date
from config import PREDICTIONS_FILE, STATS_FILE

class DataManager:
    def __init__(self):
        self.p_file = PREDICTIONS_FILE
        self.s_file = STATS_FILE
        self._init()
    
    def _init(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.p_file): self._w(self.p_file, {'predictions': []})
        if not os.path.exists(self.s_file): self._w(self.s_file, {'total': 0})

    def _r(self, f):
        try:
            with open(f, 'r') as h: return json.load(h)
        except: return {}

    def _w(self, f, d):
        with open(f, 'w') as h: json.dump(d, h, indent=2, default=str)

    def save_prediction(self, p):
        d = self._r(self.p_file)
        if 'predictions' not in d: d['predictions'] = []
        d['predictions'].append(p)
        self._w(self.p_file, d)

    def get_pending_predictions(self, d):
        data = self._r(self.p_file)
        return [p for p in data.get('predictions', []) if p.get('date') == d and p.get('status') == 'pending']

    def update_prediction_result(self, pid, res, score, prof):
        d = self._r(self.p_file)
        for p in d.get('predictions', []):
            if p['id'] == pid:
                p['status'] = 'settled'
                p['result'] = res
                p['final_score'] = score
                p['profit'] = prof
        self._w(self.p_file, d)

    def get_daily_stats(self, d):
        data = self._r(self.p_file)
        preds = [p for p in data.get('predictions', []) if p.get('date') == d and p.get('status') == 'settled']
        wins = len([p for p in preds if p['result'] == 'WIN'])
        loss = len([p for p in preds if p['result'] == 'LOSS'])
        prof = sum(p.get('profit', 0) for p in preds)
        return {'date': d, 'wins': wins, 'losses': loss, 'profit': round(prof, 2)}
    
    def prediction_exists_today(self, num):
        today = date.today().isoformat()
        data = self._r(self.p_file)
        return any(p.get('post_number') == num and p.get('date') == today for p in data.get('predictions', []))
    
    def generate_prediction_id(self):
        import datetime
        return f"pred_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
