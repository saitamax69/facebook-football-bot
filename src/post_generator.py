"""
Post Generator
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_LINK, HASHTAGS

class PostGenerator:
    def __init__(self): self.tg = TELEGRAM_LINK

    def generate_safe_bet_post(self, m, a, num):
        return self._base_post(m, a, '🟢', 'SAFE BET', num, 'LOW', 'SAFE')

    def generate_value_bet_post(self, m, a, num):
        return self._base_post(m, a, '🟡', 'VALUE BET', num, 'MEDIUM', 'MODERATE')
        
    def generate_risky_bet_post(self, m, a):
        return self._base_post(m, a, '🔴', 'HIGH ODDS', 5, 'HIGH', 'RISKY')

    def _base_post(self, m, a, emo, title, num, risk, tag_key):
        tags = ' '.join(HASHTAGS[tag_key][:5] + HASHTAGS['GENERAL'][:5])
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
🔗 {self.tg}

{tags} #{m['home_team'].replace(' ','')} #{m['away_team'].replace(' ','')}"""

    def generate_results_post(self, preds, stats):
        res_txt = ""
        for p in preds:
            e = '✅' if p['result']=='WIN' else '❌'
            res_txt += f"\n{e} {p['home_team']} vs {p['away_team']}\nPick: {p['prediction']} ({p['final_score']})\n"
        
        prof = stats['profit']
        sign = '+' if prof >= 0 else ''
        
        return f"""📊 DAILY RESULTS 📊
🗓️ {stats['date']}

{res_txt}
━━━━━━━━━━━━━━━━━━
✅ Wins: {stats['wins']}
❌ Losses: {stats['losses']}
💰 Profit: {sign}{prof} units

📲 JOIN FOR TOMORROW 👇
🔗 {self.tg}

#DailyResults #BettingTips #Profit"""
