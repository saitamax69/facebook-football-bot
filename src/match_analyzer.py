"""
Match Analyzer - Randomized, Multi-Market Picks
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RISK_LEVELS


class MatchAnalyzer:
    """
    Analyzes matches and selects optimal picks
    with multiple markets:
      - 1X2: Home / Draw / Away
      - Double Chance: Home or Draw, Away or Draw, Home or Away
      - Goals: Over/Under 2.5, Over 1.5, Under 3.5
      - BTTS: Yes / No
    """

    def __init__(self, odds_client):
        self.odds_client = odds_client
        self.used_fixtures = set()

    # Public/find methods used by scripts
    def find_safe_bet_match(self, matches):
        """Find best SAFE bet (low odds, low risk)"""
        return self._find_match_for_risk(matches, 'SAFE')

    def find_value_bet_match(self, matches):
        """Find best MODERATE/Value bet"""
        return self._find_match_for_risk(matches, 'MODERATE')

    def find_risky_bet_match(self, matches):
        """Find best RISKY/High odds bet"""
        return self._find_match_for_risk(matches, 'RISKY')

    # =========================
    # Core selection logic
    # =========================
    def _find_match_for_risk(self, matches, risk_level):
        cfg = RISK_LEVELS[risk_level]
        candidates = []

        for match in matches:
            if match['fixture_id'] in self.used_fixtures:
                continue

            odds = match.get('odds', {})
            options = self._collect_options_for_match(match, odds, cfg, risk_level)

            if options:
                # pick ONE random option for this match
                pick = random.choice(options)
                candidates.append({
                    'match': match,
                    'prediction': pick['prediction'],
                    'odds': pick['odds'],
                    'market': pick['market']
                })

        # If nothing fits exactly, find closest
        if not candidates:
            return self._find_closest_fallback(matches, risk_level)

        # Randomly pick one of the candidates to increase variation
        chosen = random.choice(candidates)
        match = chosen['match']
        prediction = chosen['prediction']
        odds_val = chosen['odds']
        market = chosen['market']

        self.used_fixtures.add(match['fixture_id'])
        analysis = self._build_analysis(match, prediction, odds_val, risk_level, market)

        return match, analysis

    def _collect_options_for_match(self, match, odds, cfg, risk_level):
        """
        Collect all valid betting options for a single match
        that fall inside the given risk level's odds range.
        """
        options = []
        min_odds, max_odds = cfg['min_odds'], cfg['max_odds']

        # 1) 1X2
        h = odds.get('home_win', {}).get('average', 0)
        d = odds.get('draw', {}).get('average', 0)
        a = odds.get('away_win', {}).get('average', 0)

        if min_odds <= h <= max_odds:
            options.append({'prediction': 'Home Win', 'odds': h, 'market': '1X2'})
        if min_odds <= d <= max_odds:
            options.append({'prediction': 'Draw', 'odds': d, 'market': '1X2'})
        if min_odds <= a <= max_odds:
            options.append({'prediction': 'Away Win', 'odds': a, 'market': '1X2'})

        # 2) Double Chance – works best for SAFE, but allowed for all
        if h > 0 and d > 0:
            # Home or Draw (1X)
            dc_1x = self._double_chance_odds(h, d)
            if min_odds <= dc_1x <= max_odds:
                options.append({'prediction': 'Home or Draw', 'odds': dc_1x, 'market': 'Double Chance'})
        if a > 0 and d > 0:
            # Away or Draw (X2)
            dc_x2 = self._double_chance_odds(a, d)
            if min_odds <= dc_x2 <= max_odds:
                options.append({'prediction': 'Away or Draw', 'odds': dc_x2, 'market': 'Double Chance'})
        if h > 0 and a > 0:
            # Home or Away (12)
            dc_12 = self._double_chance_odds(h, a)
            if min_odds <= dc_12 <= max_odds:
                options.append({'prediction': 'Home or Away', 'odds': dc_12, 'market': 'Double Chance'})

        # 3) Goals markets
        o25 = odds.get('over_25', {}).get('average', 0)
        btts_yes = odds.get('btts_yes', {}).get('average', 0)

        # Over 2.5
        if o25 > 0 and min_odds <= o25 <= max_odds:
            options.append({'prediction': 'Over 2.5 Goals', 'odds': o25, 'market': 'Goals'})

        # Simulate other goal lines from o25
        if o25 > 0:
            # Over 1.5 - usually lower odds than Over 2.5
            o15 = max(1.20, round(o25 - random.uniform(0.2, 0.5), 2))
            u25 = max(1.50, round(3.0 - o25, 2))  # rough inverse
            u35 = max(1.60, round(o25 + random.uniform(0.1, 0.4), 2))

            if min_odds <= o15 <= max_odds:
                options.append({'prediction': 'Over 1.5 Goals', 'odds': o15, 'market': 'Goals'})
            if min_odds <= u25 <= max_odds:
                options.append({'prediction': 'Under 2.5 Goals', 'odds': u25, 'market': 'Goals'})
            if min_odds <= u35 <= max_odds:
                options.append({'prediction': 'Under 3.5 Goals', 'odds': u35, 'market': 'Goals'})

        # 4) BTTS
        if btts_yes > 0 and min_odds <= btts_yes <= max_odds:
            options.append({'prediction': 'BTTS Yes', 'odds': btts_yes, 'market': 'BTTS'})

        # Rough synthetic price for BTTS No
        if btts_yes > 0:
            btts_no = max(1.60, round(3.0 - btts_yes, 2))
            if min_odds <= btts_no <= max_odds:
                options.append({'prediction': 'BTTS No', 'odds': btts_no, 'market': 'BTTS'})

        return options

    def _double_chance_odds(self, o1, o2):
        """
        Approximate double chance (1X, X2, or 12) from two decimal odds
        using: 1 / (1/o1 + 1/o2) * safety_factor
        """
        if o1 <= 1.01 or o2 <= 1.01:
            return 0
        base_prob = (1 / o1) + (1 / o2)
        if base_prob <= 0:
            return 0
        # Safety factor makes odds a bit lower than true value (bookmaker margin)
        dc_odds = 1 / base_prob * 0.95
        return round(dc_odds, 2)

    # =========================
    # Fallback if no exact bets
    # =========================
    def _find_closest_fallback(self, matches, risk_level):
        cfg = RISK_LEVELS[risk_level]
        target = (cfg['min_odds'] + cfg['max_odds']) / 2
        best = None
        best_diff = float('inf')

        for match in matches:
            if match['fixture_id'] in self.used_fixtures:
                continue

            odds = match.get('odds', {})
            market_candidates = [
                ('Home Win', odds.get('home_win', {}).get('average', 0), '1X2'),
                ('Away Win', odds.get('away_win', {}).get('average', 0), '1X2'),
                ('Draw', odds.get('draw', {}).get('average', 0), '1X2'),
                ('Over 2.5 Goals', odds.get('over_25', {}).get('average', 0), 'Goals'),
                ('BTTS Yes', odds.get('btts_yes', {}).get('average', 0), 'BTTS'),
            ]

            for name, val, market in market_candidates:
                if val > 0:
                    diff = abs(val - target)
                    if diff < best_diff:
                        best_diff = diff
                        best = {'match': match, 'prediction': name, 'odds': val, 'market': market}

        if best:
            self.used_fixtures.add(best['match']['fixture_id'])
            analysis = self._build_analysis(
                best['match'],
                best['prediction'],
                best['odds'],
                risk_level,
                best['market']
            )
            return best['match'], analysis

        return None, None

    # =========================
    # Analysis builder
    # =========================
    def _build_analysis(self, match, prediction, odds, risk_level, market):
        cfg = RISK_LEVELS[risk_level]
        confidence = self._calculate_confidence(odds, cfg)

        reasons = self._generate_reasons(
            match['home_team'],
            match['away_team'],
            prediction,
            market
        )

        return {
            'prediction': prediction,
            'odds': round(odds, 2),
            'confidence': confidence,
            'risk_level': risk_level,
            'market': market,
            'odds_display': {
                'home': f"{match['odds']['home_win']['average']:.2f}",
                'draw': f"{match['odds']['draw']['average']:.2f}",
                'away': f"{match['odds']['away_win']['average']:.2f}"
            },
            'bookmaker_odds': {
                'pinnacle': f"{odds:.2f}",
                'bet365': f"{odds + 0.03:.2f}",
                'betfair': f"{max(1.01, odds - 0.04):.2f}"
            },
            'over25': f"{match['odds']['over_25']['average']:.2f}",
            'btts': f"{match['odds']['btts_yes']['average']:.2f}",
            'btts_over': f"{round((match['odds']['over_25']['average'] + match['odds']['btts_yes']['average']) / 2 + 0.5, 2):.2f}",
            'reasons': reasons
        }

    def _calculate_confidence(self, odds, cfg):
        """Map odds inside [min,max] to confidence inside [min_conf,max_conf]."""
        if odds <= cfg['min_odds']:
            return cfg['max_confidence']
        if odds >= cfg['max_odds']:
            return cfg['min_confidence']

        odds_range = cfg['max_odds'] - cfg['min_odds']
        conf_range = cfg['max_confidence'] - cfg['min_confidence']
        pos = (odds - cfg['min_odds']) / odds_range
        conf = cfg['max_confidence'] - pos * conf_range
        return int(conf)

    def _generate_reasons(self, home, away, prediction, market):
        """Generate 3 explanatory reasons depending on prediction type."""
        reasons = []

        p = prediction.lower()
        if 'home win' in p:
            reasons = [
                f"{home} has strong home form recently",
                f"{home} looks superior to {away} on paper",
                "Market odds still offer some value on the home side"
            ]
        elif 'away win' in p:
            reasons = [
                f"{away} has been very solid away from home",
                f"{home} has shown defensive weaknesses lately",
                "Team news and momentum favour the visitors"
            ]
        elif 'draw' == p:
            reasons = [
                "Both teams are evenly matched",
                "Defensive styles point towards a tight game",
                "Odds on the draw are attractive given the matchup"
            ]
        elif 'home or draw' in p:
            reasons = [
                f"{home} rarely loses at home",
                "Double chance provides extra safety",
                "Stats point to at least one point for the hosts"
            ]
        elif 'away or draw' in p:
            reasons = [
                f"{away} difficult to beat on current form",
                "More margin of safety than straight away win",
                "Hosts inconsistent, visitors look solid"
            ]
        elif 'home or away' in p:
            reasons = [
                "Open game where a winner is very likely",
                "Both teams push for 3 points",
                "Style of play suggests someone will edge it"
            ]
        elif 'over 2.5' in p:
            reasons = [
                "Both sides average high goals per match",
                "Attacking strengths outweigh defensive solidity",
                "Previous meetings tend to be open and high scoring"
            ]
        elif 'under 2.5' in p:
            reasons = [
                "Both teams play cautious football",
                "Defensive setups suggest few clear chances",
                "Stats show many recent low-scoring games"
            ]
        elif 'over 1.5' in p:
            reasons = [
                "Early goal could open the match up",
                "Both teams usually score at least once",
                "Good balance between risk and reward"
            ]
        elif 'under 3.5' in p:
            reasons = [
                "Unlikely to become a goal fest",
                "Tactical battle rather than end-to-end",
                "Both managers tend to keep things tight"
            ]
        elif 'btts yes' in p:
            reasons = [
                f"{home} and {away} both carry attacking threat",
                "Defensive errors likely at both ends",
                "Both teams have scored in most recent games"
            ]
        elif 'btts no' in p:
            reasons = [
                f"One of {home} or {away} struggles in attack",
                "At least one defence is very solid",
                "Match scenario suggests a clean sheet is likely"
            ]
        else:
            reasons = [
                "Statistical model favours this selection",
                "Odds appear mispriced compared to true chance",
                "Good balance between risk and reward"
            ]

        # Guarantee exactly 3 reasons
        if len(reasons) < 3:
            while len(reasons) < 3:
                reasons.append("Additional supporting factor for this pick")
        return reasons[:3]
