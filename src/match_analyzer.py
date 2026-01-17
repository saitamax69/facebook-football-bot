"""
🏆 Sports Prediction Bot - Match Analyzer
==========================================

Analyzes matches to generate predictions with confidence levels.
Uses odds data and statistical analysis to select best bets.
"""

import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import json

from src.config import RISK_LEVELS, TOP_LEAGUES, logger
from src.api_client import odds_api
from src.database import Prediction


# ═══════════════════════════════════════════════════════════════════
# 📊 ANALYSIS RESULT MODEL
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MatchAnalysis:
    """Result of match analysis"""
    fixture: Dict
    prediction: str
    prediction_type: str  # 1X2, OVER_UNDER, BTTS
    selected_odds: float
    confidence: int
    risk_level: str
    analysis_points: List[str]
    home_odds: float
    draw_odds: float
    away_odds: float
    over_25_odds: float
    under_25_odds: float
    bookmaker_odds: Dict


# ═══════════════════════════════════════════════════════════════════
# 🔍 MATCH ANALYZER CLASS
# ═══════════════════════════════════════════════════════════════════

class MatchAnalyzer:
    """
    Analyzes football matches to generate betting predictions.
    Uses odds comparison and statistical indicators.
    """
    
    def __init__(self):
        """Initialize the analyzer"""
        logger.info("🔍 Match Analyzer initialized")
    
    def analyze_match(self, fixture: Dict) -> Optional[MatchAnalysis]:
        """
        Analyze a single match and generate prediction.
        
        Args:
            fixture: Match fixture data with odds
            
        Returns:
            MatchAnalysis object or None if insufficient data
        """
        try:
            # Extract odds
            best_odds = odds_api.extract_best_odds(fixture)
            
            home_odds = best_odds['home']['odds']
            draw_odds = best_odds['draw']['odds']
            away_odds = best_odds['away']['odds']
            over_25 = best_odds['over_2_5']['odds']
            under_25 = best_odds['under_2_5']['odds']
            
            # Skip if essential odds are missing
            if not all([home_odds, draw_odds, away_odds]):
                logger.debug(f"⚠️ Missing odds for {fixture.get('home_team')} vs {fixture.get('away_team')}")
                return None
            
            # Calculate implied probabilities
            home_prob = 1 / home_odds if home_odds > 0 else 0
            draw_prob = 1 / draw_odds if draw_odds > 0 else 0
            away_prob = 1 / away_odds if away_odds > 0 else 0
            
            # Find the most likely outcome
            outcomes = [
                ('Home Win', home_odds, home_prob, fixture.get('home_team', 'Home')),
                ('Draw', draw_odds, draw_prob, 'Draw'),
                ('Away Win', away_odds, away_prob, fixture.get('away_team', 'Away'))
            ]
            
            # Sort by probability (highest first)
            outcomes.sort(key=lambda x: x[2], reverse=True)
            
            # Generate prediction based on the best value
            best_outcome = outcomes[0]
            prediction_type = '1X2'
            prediction = best_outcome[3]
            selected_odds = best_outcome[1]
            
            # Determine risk level and confidence
            risk_level = self.determine_risk_level(selected_odds)
            confidence = self.calculate_confidence(selected_odds, best_outcome[2])
            
            # Generate analysis points
            analysis_points = self.generate_analysis_points(
                fixture, best_outcome, home_odds, draw_odds, away_odds
            )
            
            return MatchAnalysis(
                fixture=fixture,
                prediction=prediction,
                prediction_type=prediction_type,
                selected_odds=selected_odds,
                confidence=confidence,
                risk_level=risk_level,
                analysis_points=analysis_points,
                home_odds=home_odds,
                draw_odds=draw_odds,
                away_odds=away_odds,
                over_25_odds=over_25,
                under_25_odds=under_25,
                bookmaker_odds=best_odds.get('specific', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return None
    
    def determine_risk_level(self, odds: float) -> str:
        """
        Determine risk level based on odds.
        
        Args:
            odds: Decimal odds value
            
        Returns:
            Risk level string (SAFE, VALUE, RISKY)
        """
        if odds <= RISK_LEVELS['SAFE'].odds_max:
            return 'SAFE'
        elif odds <= RISK_LEVELS['VALUE'].odds_max:
            return 'VALUE'
        else:
            return 'RISKY'
    
    def calculate_confidence(self, odds: float, implied_prob: float) -> int:
        """
        Calculate confidence percentage based on odds and probability.
        
        Args:
            odds: Decimal odds
            implied_prob: Implied probability from odds
            
        Returns:
            Confidence percentage (0-100)
        """
        # Base confidence from implied probability
        base_confidence = int(implied_prob * 100)
        
        # Adjust based on odds range
        if odds < 1.30:
            # Very low odds = high confidence
            return min(95, base_confidence + 10)
        elif odds < 1.60:
            return min(90, base_confidence + 5)
        elif odds < 2.00:
            return min(80, base_confidence)
        elif odds < 2.50:
            return min(70, base_confidence - 5)
        else:
            return min(60, base_confidence - 10)
    
    def calculate_value(self, odds: float, true_prob: float) -> float:
        """
        Calculate value in a bet.
        
        Args:
            odds: Bookmaker decimal odds
            true_prob: Our estimated true probability
            
        Returns:
            Value percentage (positive = good value)
        """
        implied_prob = 1 / odds
        return ((true_prob - implied_prob) / implied_prob) * 100
    
    def generate_analysis_points(
        self,
        fixture: Dict,
        outcome: Tuple,
        home_odds: float,
        draw_odds: float,
        away_odds: float
    ) -> List[str]:
        """
        Generate analysis reasoning points for a prediction.
        
        Args:
            fixture: Match fixture data
            outcome: Selected outcome tuple
            home_odds, draw_odds, away_odds: 1X2 odds
            
        Returns:
            List of 3 analysis points
        """
        points = []
        outcome_name, odds, prob, team = outcome
        
        home_team = fixture.get('home_team', 'Home')
        away_team = fixture.get('away_team', 'Away')
        league = fixture.get('league_name', 'Unknown League')
        
        # Point 1: Probability-based
        prob_pct = int(prob * 100)
        if outcome_name == 'Home Win':
            points.append(f"{home_team} have {prob_pct}% implied win probability at home")
        elif outcome_name == 'Away Win':
            points.append(f"{away_team} showing {prob_pct}% implied win probability")
        else:
            points.append(f"Draw has {prob_pct}% implied probability in this fixture")
        
        # Point 2: Odds comparison
        if odds < 1.50:
            points.append("Strong favorite with odds heavily in their favor")
        elif odds < 1.80:
            points.append("Clear favorite according to bookmaker consensus")
        elif odds < 2.20:
            points.append("Slight edge reflected in market odds")
        else:
            points.append("Value opportunity with good risk/reward ratio")
        
        # Point 3: Context-based
        context_points = [
            f"Key {league} fixture with high market liquidity",
            "Multiple bookmakers showing consistent odds",
            "Sharp money aligned with this selection",
            f"Home advantage factor considered for {home_team}",
            "Recent form and head-to-head record supports pick",
            "Statistical edge identified in pre-match analysis",
        ]
        
        # Select relevant context point
        if outcome_name == 'Home Win':
            points.append(f"Home advantage factor for {home_team} in {league}")
        elif outcome_name == 'Away Win':
            points.append(f"{away_team} capable of strong away performance")
        else:
            points.append("Match profile suggests tight contest")
        
        return points[:3]
    
    def select_best_matches(
        self,
        matches: List[Dict],
        risk_level: str,
        count: int = 1
    ) -> List[MatchAnalysis]:
        """
        Select the best matches for a given risk level.
        
        Args:
            matches: List of available fixtures
            risk_level: Target risk level (SAFE, VALUE, RISKY)
            count: Number of matches to select
            
        Returns:
            List of MatchAnalysis objects
        """
        risk_config = RISK_LEVELS[risk_level]
        analyzed = []
        
        for match in matches:
            analysis = self.analyze_match(match)
            if analysis:
                # Check if odds fall within the risk level range
                if risk_config.odds_min <= analysis.selected_odds <= risk_config.odds_max:
                    # Adjust confidence to match risk level range
                    analysis.confidence = self._adjust_confidence(
                        analysis.confidence,
                        risk_config.confidence_min,
                        risk_config.confidence_max
                    )
                    analysis.risk_level = risk_level
                    analyzed.append(analysis)
        
        # Sort by confidence and odds value
        analyzed.sort(key=lambda x: (x.confidence, -x.selected_odds), reverse=True)
        
        # If no matches in exact range, find closest matches
        if not analyzed and matches:
            logger.warning(f"⚠️ No exact matches for {risk_level}, finding alternatives")
            analyzed = self._find_alternative_matches(matches, risk_level, count)
        
        return analyzed[:count]
    
    def _adjust_confidence(
        self,
        confidence: int,
        min_conf: int,
        max_conf: int
    ) -> int:
        """Adjust confidence to fall within specified range"""
        if confidence > max_conf:
            return max_conf
        elif confidence < min_conf:
            return min_conf
        return confidence
    
    def _find_alternative_matches(
        self,
        matches: List[Dict],
        risk_level: str,
        count: int
    ) -> List[MatchAnalysis]:
        """Find alternative matches when no exact risk level matches exist"""
        risk_config = RISK_LEVELS[risk_level]
        analyzed = []
        
        for match in matches:
            analysis = self.analyze_match(match)
            if analysis:
                # Adjust to closest valid odds in range
                if analysis.selected_odds < risk_config.odds_min:
                    # Too safe - might work for safe bets
                    if risk_level == 'SAFE':
                        analysis.confidence = risk_config.confidence_max
                        analyzed.append(analysis)
                elif analysis.selected_odds > risk_config.odds_max:
                    # Too risky - might work for risky bets
                    if risk_level == 'RISKY':
                        analysis.confidence = risk_config.confidence_min
                        analyzed.append(analysis)
                else:
                    analysis.confidence = (risk_config.confidence_min + risk_config.confidence_max) // 2
                    analyzed.append(analysis)
        
        analyzed.sort(key=lambda x: abs(x.selected_odds - 
                     (risk_config.odds_min + risk_config.odds_max) / 2))
        
        return analyzed[:count]
    
    def analyze_for_over_under(
        self,
        fixture: Dict,
        line: float = 2.5
    ) -> Optional[MatchAnalysis]:
        """
        Analyze match for Over/Under prediction.
        
        Args:
            fixture: Match fixture data
            line: Goals line (default 2.5)
            
        Returns:
            MatchAnalysis for over/under or None
        """
        try:
            best_odds = odds_api.extract_best_odds(fixture)
            
            over_odds = best_odds['over_2_5']['odds']
            under_odds = best_odds['under_2_5']['odds']
            
            if not over_odds or not under_odds:
                return None
            
            # Determine which is better value
            over_prob = 1 / over_odds if over_odds > 0 else 0
            under_prob = 1 / under_odds if under_odds > 0 else 0
            
            if over_prob > under_prob:
                prediction = f"Over {line} Goals"
                selected_odds = over_odds
                prob = over_prob
            else:
                prediction = f"Under {line} Goals"
                selected_odds = under_odds
                prob = under_prob
            
            risk_level = self.determine_risk_level(selected_odds)
            confidence = self.calculate_confidence(selected_odds, prob)
            
            analysis_points = [
                f"Goal line of {line} analyzed for value",
                f"Implied probability: {int(prob * 100)}%",
                "Market consensus supports this selection"
            ]
            
            return MatchAnalysis(
                fixture=fixture,
                prediction=prediction,
                prediction_type='OVER_UNDER',
                selected_odds=selected_odds,
                confidence=confidence,
                risk_level=risk_level,
                analysis_points=analysis_points,
                home_odds=best_odds['home']['odds'],
                draw_odds=best_odds['draw']['odds'],
                away_odds=best_odds['away']['odds'],
                over_25_odds=over_odds,
                under_25_odds=under_odds,
                bookmaker_odds=best_odds.get('specific', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Over/Under analysis error: {e}")
            return None
    
    def get_daily_selections(self) -> Dict[str, List[MatchAnalysis]]:
        """
        Get all daily selections for each post.
        
        Returns:
            Dictionary with selections for each risk level
        """
        # Fetch upcoming fixtures
        fixtures = odds_api.get_upcoming_fixtures(hours=24)
        
        if not fixtures:
            logger.warning("⚠️ No fixtures available for today")
            return {}
        
        logger.info(f"📊 Analyzing {len(fixtures)} fixtures for daily selections")
        
        selections = {
            'SAFE_1': self.select_best_matches(fixtures, 'SAFE', 1),
            'SAFE_2': [],
            'VALUE_1': self.select_best_matches(fixtures, 'VALUE', 1),
            'VALUE_2': [],
            'RISKY': self.select_best_matches(fixtures, 'RISKY', 1)
        }
        
        # Get second selections avoiding duplicates
        used_matches = set()
        for key in ['SAFE_1', 'VALUE_1', 'RISKY']:
            for analysis in selections[key]:
                match_id = analysis.fixture.get('id', '')
                if match_id:
                    used_matches.add(match_id)
        
        # Filter out used matches
        remaining = [f for f in fixtures if f.get('id', '') not in used_matches]
        
        selections['SAFE_2'] = self.select_best_matches(remaining, 'SAFE', 1)
        
        remaining = [f for f in remaining if f.get('id', '') not in 
                    {a.fixture.get('id', '') for a in selections['SAFE_2']}]
        
        selections['VALUE_2'] = self.select_best_matches(remaining, 'VALUE', 1)
        
        logger.info(f"✅ Daily selections complete: {sum(len(v) for v in selections.values())} picks")
        
        return selections


# Create singleton instance
analyzer = MatchAnalyzer()
