"""
Odds API Client for fetching sports data
"""
import requests
import time
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RAPIDAPI_KEY, RAPIDAPI_HOST, API_BASE_URL, PRIORITY_LEAGUES


class OddsAPIClient:
    """Client for Odds API via RapidAPI"""
    
    def __init__(self):
        self.headers = {
            'x-rapidapi-host': RAPIDAPI_HOST,
            'x-rapidapi-key': RAPIDAPI_KEY or ''
        }
        self.base_url = API_BASE_URL
    
    def get_upcoming_fixtures(self, hours=48):
        """Fetch upcoming fixtures from priority leagues"""
        print(f"📡 Fetching upcoming fixtures...")
        
        fixtures = []
        
        if RAPIDAPI_KEY:
            try:
                response = self._make_request('odds', {
                    'sport': 'soccer',
                    'region': 'eu',
                    'market': 'h2h',
                    'oddsFormat': 'decimal'
                })
                
                if response and isinstance(response, list):
                    for event in response:
                        fixture = self._parse_fixture(event)
                        if fixture:
                            fixtures.append(fixture)
                    print(f"✅ API returned {len(fixtures)} fixtures")
            except Exception as e:
                print(f"⚠️ API error: {e}")
        
        if not fixtures:
            print("📦 Using sample fixtures...")
            fixtures = self._generate_sample_fixtures()
        
        return fixtures
    
    def get_match_result(self, fixture_id):
        """Get match result"""
        print(f"🔍 Fetching result for: {fixture_id}")
        
        if RAPIDAPI_KEY:
            try:
                response = self._make_request('scores', {'sport': 'soccer', 'daysFrom': 3})
                if response:
                    for event in response:
                        if event.get('id') == fixture_id:
                            scores = event.get('scores', [])
                            if scores and len(scores) >= 2:
                                return {
                                    'home_score': int(scores[0].get('score', 0)),
                                    'away_score': int(scores[1].get('score', 0)),
                                    'status': 'finished'
                                }
            except Exception as e:
                print(f"⚠️ Result fetch error: {e}")
        
        return self._generate_sample_result()
    
    def _make_request(self, endpoint, params=None):
        """Make API request with retry"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    time.sleep(5)
                else:
                    print(f"⚠️ API status: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Request error: {e}")
                time.sleep(2)
        
        return None
    
    def _parse_fixture(self, event):
        """Parse fixture from API response"""
        try:
            home_team = event.get('home_team', '')
            away_team = event.get('away_team', '')
            
            if not home_team or not away_team:
                return None
            
            commence_time = event.get('commence_time', '')
            try:
                start_dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            except:
                start_dt = datetime.utcnow() + timedelta(hours=random.randint(2, 24))
            
            odds_data = self._parse_odds(event.get('bookmakers', []))
            
            return {
                'fixture_id': event.get('id', f"fx_{random.randint(10000, 99999)}"),
                'league': event.get('sport_title', 'Football'),
                'home_team': home_team,
                'away_team': away_team,
                'start_time': start_dt,
                'date': start_dt.strftime('%d %b %Y'),
                'time': start_dt.strftime('%H:%M'),
                'odds': odds_data
            }
        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            return None
    
    def _parse_odds(self, bookmakers):
        """Parse odds from bookmakers"""
        odds = {'home_win': {}, 'draw': {}, 'away_win': {}, 'over_25': {}, 'btts_yes': {}}
        
        for bookie in bookmakers:
            name = bookie.get('key', '').lower()
            for market in bookie.get('markets', []):
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    for i, outcome in enumerate(outcomes):
                        price = outcome.get('price', 0)
                        if i == 0:
                            odds['home_win'][name] = price
                        elif i == 1:
                            odds['draw'][name] = price
                        elif i == 2:
                            odds['away_win'][name] = price
        
        for key in odds:
            values = [v for v in odds[key].values() if v > 0]
            odds[key]['average'] = round(sum(values) / len(values), 2) if values else 0
        
        return odds
    
    def _generate_sample_fixtures(self):
        """Generate sample fixtures"""
        matches = [
            {'league': 'Premier League', 'home': 'Arsenal', 'away': 'Chelsea', 'h': 1.85, 'd': 3.50, 'a': 4.20},
            {'league': 'Premier League', 'home': 'Manchester City', 'away': 'Liverpool', 'h': 1.70, 'd': 3.80, 'a': 4.80},
            {'league': 'Premier League', 'home': 'Manchester United', 'away': 'Tottenham', 'h': 2.10, 'd': 3.40, 'a': 3.50},
            {'league': 'Premier League', 'home': 'Newcastle', 'away': 'Aston Villa', 'h': 1.90, 'd': 3.50, 'a': 4.00},
            {'league': 'La Liga', 'home': 'Real Madrid', 'away': 'Barcelona', 'h': 2.20, 'd': 3.30, 'a': 3.40},
            {'league': 'La Liga', 'home': 'Atletico Madrid', 'away': 'Sevilla', 'h': 1.65, 'd': 3.60, 'a': 5.50},
            {'league': 'Bundesliga', 'home': 'Bayern Munich', 'away': 'Dortmund', 'h': 1.45, 'd': 4.50, 'a': 6.50},
            {'league': 'Bundesliga', 'home': 'RB Leipzig', 'away': 'Leverkusen', 'h': 2.00, 'd': 3.50, 'a': 3.80},
            {'league': 'Serie A', 'home': 'Juventus', 'away': 'Inter Milan', 'h': 2.30, 'd': 3.20, 'a': 3.20},
            {'league': 'Serie A', 'home': 'AC Milan', 'away': 'Napoli', 'h': 2.40, 'd': 3.30, 'a': 3.00},
            {'league': 'Serie A', 'home': 'Roma', 'away': 'Lazio', 'h': 2.20, 'd': 3.30, 'a': 3.40},
            {'league': 'Ligue 1', 'home': 'PSG', 'away': 'Monaco', 'h': 1.35, 'd': 5.00, 'a': 8.00},
            {'league': 'Ligue 1', 'home': 'Marseille', 'away': 'Lyon', 'h': 2.10, 'd': 3.40, 'a': 3.50},
            {'league': 'Eredivisie', 'home': 'Ajax', 'away': 'PSV', 'h': 1.95, 'd': 3.60, 'a': 3.90},
            {'league': 'Primeira Liga', 'home': 'Benfica', 'away': 'Porto', 'h': 2.00, 'd': 3.40, 'a': 3.80},
            {'league': 'Champions League', 'home': 'Real Madrid', 'away': 'Man City', 'h': 2.50, 'd': 3.30, 'a': 2.90},
            {'league': 'Champions League', 'home': 'Bayern Munich', 'away': 'PSG', 'h': 1.80, 'd': 3.70, 'a': 4.30},
            {'league': 'Europa League', 'home': 'Roma', 'away': 'Ajax', 'h': 1.90, 'd': 3.50, 'a': 4.20},
            {'league': 'Copa Libertadores', 'home': 'Flamengo', 'away': 'River Plate', 'h': 2.10, 'd': 3.30, 'a': 3.60},
            {'league': 'MLS', 'home': 'Inter Miami', 'away': 'LA Galaxy', 'h': 1.85, 'd': 3.50, 'a': 4.20},
            {'league': 'Saudi Pro League', 'home': 'Al-Hilal', 'away': 'Al-Nassr', 'h': 2.20, 'd': 3.30, 'a': 3.40},
            {'league': 'Belgian Pro League', 'home': 'Club Brugge', 'away': 'Anderlecht', 'h': 1.75, 'd': 3.70, 'a': 4.60},
            {'league': 'Super Lig', 'home': 'Galatasaray', 'away': 'Fenerbahce', 'h': 2.10, 'd': 3.40, 'a': 3.50},
            {'league': 'Scottish Premiership', 'home': 'Celtic', 'away': 'Rangers', 'h': 1.90, 'd': 3.50, 'a': 4.00},
            {'league': 'FA Cup', 'home': 'Brighton', 'away': 'Everton', 'h': 1.70, 'd': 3.60, 'a': 5.00},
            {'league': 'Copa del Rey', 'home': 'Valencia', 'away': 'Villarreal', 'h': 2.30, 'd': 3.30, 'a': 3.10},
            {'league': 'DFB Pokal', 'home': 'Stuttgart', 'away': 'Freiburg', 'h': 1.95, 'd': 3.50, 'a': 3.90},
            {'league': 'Coppa Italia', 'home': 'Atalanta', 'away': 'Fiorentina', 'h': 1.80, 'd': 3.60, 'a': 4.50},
        ]
        
        fixtures = []
        base_time = datetime.utcnow() + timedelta(hours=3)
        
        for i, m in enumerate(matches):
            start = base_time + timedelta(hours=i * 2)
            fixtures.append({
                'fixture_id': f"sample_{i}_{random.randint(1000, 9999)}",
                'league': m['league'],
                'home_team': m['home'],
                'away_team': m['away'],
                'start_time': start,
                'date': start.strftime('%d %b %Y'),
                'time': start.strftime('%H:%M'),
                'odds': {
                    'home_win': {'pinnacle': m['h'], 'bet365': m['h'] + 0.05, 'average': m['h']},
                    'draw': {'pinnacle': m['d'], 'bet365': m['d'] + 0.10, 'average': m['d']},
                    'away_win': {'pinnacle': m['a'], 'bet365': m['a'] + 0.08, 'average': m['a']},
                    'over_25': {'average': round(random.uniform(1.75, 2.05), 2)},
                    'btts_yes': {'average': round(random.uniform(1.70, 1.95), 2)}
                }
            })
        
        random.shuffle(fixtures)
        return fixtures
    
    def _generate_sample_result(self):
        """Generate sample result"""
        h = random.choices([0, 1, 2, 3, 4], weights=[15, 30, 35, 15, 5])[0]
        a = random.choices([0, 1, 2, 3], weights=[25, 40, 25, 10])[0]
        return {'home_score': h, 'away_score': a, 'status': 'finished'}
