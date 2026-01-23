"""
Post Generator for creating Facebook post content
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_LINK, HASHTAGS


class PostGenerator:
    """Generates formatted post content"""
    
    def __init__(self):
        self.telegram = TELEGRAM_LINK
    
    def generate_safe_bet_post(self, match, analysis, post_num):
        return self._base_post(match, analysis, '🟢', 'SAFE BET', post_num, 'LOW', 'SAFE')

    def generate_value_bet_post(self, match, analysis, post_num):
        return self._base_post(match, analysis, '🟡', 'VALUE BET', post_num, 'MEDIUM', 'MODERATE')
        
    def generate_risky_bet_post(self, match, analysis):
        return self._base_post(match, analysis, '🔴', 'HIGH ODDS', 5, 'HIGH', 'RISKY')

    def _base_post(self, m, a, emo, title, num, risk, tag_key):
        tags = self._hashtags(tag_key, m['league'], m['home_team'], m['away_team'])
        
        return f"""{emo}⚽{emo}⚽{emo}⚽{emo}⚽{emo}

{title} #{num}

━━━━━━━━━━━━━━━━━━
🏆 {m['league']}
📅 {m['date']} | ⏰ {m['time']}
━━━━━━━━━━━━━━━━━━

🏠 {m['home_team']}
        🆚
✈️ {m['away_team']}

📊 ODDS:
1️⃣ Home: {a['odds_display']['home']}
❌ Draw: {a['odds_display']['draw']}
2️⃣ Away: {a['odds_display']['away']}

🎯 PREDICTION:
✅ PICK: {a['prediction']}
💰 ODDS: {a['odds']}
📊 CONFIDENCE: {a['confidence']}%

📉 ANALYSIS:
• {a['reasons'][0]}
• {a['reasons'][1]}

🔒 RISK: {risk} {emo}

📲 MORE FREE TIPS 👇
🔗 {self.telegram}

{tags}"""

    def generate_results_post(self, predictions, stats):
        results_txt = ""
        
        # CRITICAL FIX: Use .get() to avoid KeyError
        for p in predictions:
            res = p.get('result', 'PENDING')
            emoji = '✅' if res == 'WIN' else '❌'
            
            results_txt += f"""
{emoji} {p.get('home_team', 'Home')} vs {p.get('away_team', 'Away')}
Pick: {p.get('prediction', 'Pick')} ({p.get('final_score', '?-?')})
"""
        
        profit = stats.get('profit', 0)
        sign = '+' if profit >= 0 else ''
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        
        return f"""📊 DAILY RESULTS 📊
🗓️ {stats.get('date', 'Today')}

{results_txt}
━━━━━━━━━━━━━━━━━━
✅ Wins: {wins}
❌ Losses: {losses}
💰 Profit: {sign}{profit} units

📲 JOIN FOR TOMORROW 👇
🔗 {self.telegram}

#DailyResults #BettingTips #Profit #Football"""
    
    def _hashtags(self, risk, league, home, away):
        tags = HASHTAGS.get(risk, [])[:4] + HASHTAGS.get('GENERAL', [])[:4]
        # Clean team names for hashtags
        l_tag = '#' + league.replace(' ', '').replace('-', '').replace('.', '')
        h_tag = '#' + home.replace(' ', '').replace('-', '').replace('.', '')
        a_tag = '#' + away.replace(' ', '').replace('-', '').replace('.', '')
        
        tags.append(l_tag)
        tags.append(h_tag)
        tags.append(a_tag)
        
        return ' '.join(tags[:15])
