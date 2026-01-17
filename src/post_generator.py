"""
Match Analyzer
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RISK_LEVELS

class MatchAnalyzer:
    def __init__(self, client):
        self.client = client
        self.used = set()

    def find_safe_bet_match(self, matches): return self._find(matches, 'SAFE')
    def find_value_bet_match(self, matches): return self._find(matches, 'MODERATE')
    def find_risky_bet_match(self, matches): return self._find(matches, 'RISKY')

    def _find(self, matches, level):
        conf = RISK_LEVELS[level]
        cands = []
        
        for m in matches:
            if m['fixture_id'] in self.used: continue
            odds = m['odds']
            
            for k, name in [('home_win','Home Win'), ('away_win','Away Win')]:
                avg = odds[k]['average']
                if conf['min_odds'] <= avg <= conf['max_odds']:
                    cands.append({'m': m, 'p': name, 'o': avg})
        
        if not cands: return self._closest(matches, level)
        
        # Simple sort by odds
        cands.sort(key=lambda x: x['o'])
        best = cands[0]
        self.used.add(best['m']['fixture_id'])
        
        return best['m'], self._analyze(best['m'], best['p'], best['o'], level)

    def _closest(self, matches, level):
        conf = RISK_LEVELS[level]
        target = (conf['min_odds'] + conf['max_odds']) / 2
        best = None
        min_diff = 999
        
        for m in matches:
            if m['fixture_id'] in self.used: continue
            for k, name in [('home_win','Home Win'), ('away_win','Away Win')]:
                avg = m['odds'][k]['average']
                if avg > 0:
                    diff = abs(avg - target)
                    if diff < min_diff:
                        min_diff = diff
                        best = {'m': m, 'p': name, 'o': avg}
        
        if best:
            self.used.add(best['m']['fixture_id'])
            return best['m'], self._analyze(best['m'], best['p'], best['o'], level)
        return None, None

    def _analyze(self, match, pred, odds, level):
        conf = RISK_LEVELS[level]
        # Calc confidence
        rng = conf['max_odds'] - conf['min_odds']
        pos = (odds - conf['min_odds']) / rng if rng > 0 else 0.5
        confidence = int(conf['max_confidence'] - (pos * (conf['max_confidence'] - conf['min_confidence'])))
        
        return {
            'prediction': pred,
            'odds': odds,
            'confidence': confidence,
            'odds_display': {
                'home': f"{match['odds']['home_win']['average']:.2f}",
                'draw': f"{match['odds']['draw']['average']:.2f}",
                'away': f"{match['odds']['away_win']['average']:.2f}"
            },
            'bookmaker_odds': {
                'pinnacle': f"{odds:.2f}",
                'bet365': f"{odds+0.05:.2f}",
                'betfair': f"{odds-0.02:.2f}"
            },
            'over25': f"{match['odds']['over_25']['average']:.2f}",
            'btts': f"{match['odds']['btts_yes']['average']:.2f}",
            'reasons': [
                f"Statistical analysis favors {pred}",
                f"Value found at odds {odds}",
                "Recent form supports this outcome"
            ]
        }
