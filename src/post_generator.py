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
        """Generate Safe Bet post"""
        tags = self._hashtags('SAFE', match['league'], match['home_team'], match['away_team'])
        
        return f"""🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

🔒 𝗦𝗔𝗙𝗘 𝗕𝗘𝗧 #{post_num} 🔒

━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 {match['league']}
📅 {match['date']} | ⏰ {match['time']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 {match['home_team']}
        ⚔️
✈️ {match['away_team']}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 𝗢𝗗𝗗𝗦 𝗖𝗢𝗠𝗣𝗔𝗥𝗜𝗦𝗢𝗡
┌─────────────────────────┐
│ 🏠 Home Win:  {analysis['odds_display']['home']:<8} │
│ 🤝 Draw:      {analysis['odds_display']['draw']:<8} │
│ ✈️ Away Win:  {analysis['odds_display']['away']:<8} │
└─────────────────────────┘

🏦 𝗕𝗢𝗢𝗞𝗠𝗔𝗞𝗘𝗥𝗦
├─ Pinnacle:  {analysis['bookmaker_odds']['pinnacle']}
├─ Bet365:    {analysis['bookmaker_odds']['bet365']}
└─ Betfair:   {analysis['bookmaker_odds']['betfair']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 𝗢𝗨𝗥 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 𝗣𝗜𝗖𝗞: {analysis['prediction']}
💰 𝗢𝗗𝗗𝗦: {analysis['odds']}
🎚️ 𝗖𝗢𝗡𝗙𝗜𝗗𝗘𝗡𝗖𝗘: 🟢🟢🟢🟢🟢 {analysis['confidence']}%

━━━━━━━━━━━━━━━━━━━━━━━━━

📈 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦
• {analysis['reasons'][0]}
• {analysis['reasons'][1]}
• {analysis['reasons'][2]}

━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 𝗥𝗜𝗦𝗞: 𝗟𝗢𝗪 🟢
💎 𝗧𝗬𝗣𝗘: 𝗦𝗔𝗙𝗘 𝗕𝗘𝗧

━━━━━━━━━━━━━━━━━━━━━━━━━

📲 𝗠𝗢𝗥𝗘 𝗙𝗥𝗘𝗘 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡𝗦 👇
🔗 {self.telegram}
🎁 We post more FREE predictions on Telegram daily!

🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢⚽🟢

{tags}"""
    
    def generate_value_bet_post(self, match, analysis, post_num):
        """Generate Value Bet post"""
        tags = self._hashtags('MODERATE', match['league'], match['home_team'], match['away_team'])
        
        return f"""🟡⚽🟡⚽🟡⚽🟡⚽🟡⚽🟡⚽🟡

💎 𝗩𝗔𝗟𝗨𝗘 𝗕𝗘𝗧 #{post_num} 💎

━━━━━━━━━━━━━━━━━━━━━━━━━

⚽ {match['league']}
🗓️ {match['date']} • 🕐 {match['time']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 {match['home_team']}
        🆚
✈️ {match['away_team']}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 𝗠𝗔𝗜𝗡 𝗢𝗗𝗗𝗦
• 1️⃣ Home Win: {analysis['odds_display']['home']}
• ❌ Draw:     {analysis['odds_display']['draw']}
• 2️⃣ Away Win: {analysis['odds_display']['away']}

📈 𝗢𝗧𝗛𝗘𝗥 𝗠𝗔𝗥𝗞𝗘𝗧𝗦
• Over 2.5 Goals: {analysis['over25']}
• BTTS Yes:       {analysis['btts']}

🏦 Pinnacle: {analysis['bookmaker_odds']['pinnacle']} │ Bet365: {analysis['bookmaker_odds']['bet365']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 𝗢𝗨𝗥 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡
━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 𝗣𝗜𝗖𝗞: {analysis['prediction']}
💵 𝗢𝗗𝗗𝗦: {analysis['odds']}
📊 𝗖𝗢𝗡𝗙𝗜𝗗𝗘𝗡𝗖𝗘: 🟡🟡🟡🟡⚪ {analysis['confidence']}%

━━━━━━━━━━━━━━━━━━━━━━━━━

📉 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦
📌 {analysis['reasons'][0]}
📌 {analysis['reasons'][1]}
📌 {analysis['reasons'][2]}

━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 𝗥𝗜𝗦𝗞: 𝗠𝗘𝗗𝗜𝗨𝗠 🟡
🎯 𝗧𝗬𝗣𝗘: 𝗩𝗔𝗟𝗨𝗘 𝗕𝗘𝗧

━━━━━━━━━━━━━━━━━━━━━━━━━

📲 𝗠𝗢𝗥𝗘 𝗙𝗥𝗘𝗘 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡𝗦 👇
🔗 {self.telegram}
🎁 We post more FREE predictions on Telegram daily!

🟡⚽🟡⚽🟡⚽🟡⚽🟡⚽🟡⚽🟡

{tags}"""
    
    def generate_risky_bet_post(self, match, analysis):
        """Generate Risky Bet post"""
        tags = self._hashtags('RISKY', match['league'], match['home_team'], match['away_team'])
        
        return f"""🔴🎰🔴🎰🔴🎰🔴🎰🔴🎰🔴🎰🔴

🚀 𝗛𝗜𝗚𝗛 𝗢𝗗𝗗𝗦 𝗣𝗜𝗖𝗞 #𝟱 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 {match['league']}
📅 {match['date']} | ⏰ {match['time']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 {match['home_team']}
        💥
✈️ {match['away_team']}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 𝗠𝗔𝗜𝗡 𝗢𝗗𝗗𝗦
🏠 Home Win: {analysis['odds_display']['home']}
🤝 Draw:     {analysis['odds_display']['draw']}
✈️ Away Win: {analysis['odds_display']['away']}

🎰 𝗦𝗣𝗘𝗖𝗜𝗔𝗟 𝗠𝗔𝗥𝗞𝗘𝗧𝗦
💠 BTTS + Over 2.5: {analysis['btts_over']}
💠 Both Teams Score: {analysis['btts']}

━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 𝗛𝗜𝗚𝗛-𝗥𝗜𝗦𝗞 𝗣𝗜𝗖𝗞
━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡: {analysis['prediction']}
💰 𝗢𝗗𝗗𝗦: {analysis['odds']} 🔥
📊 𝗖𝗢𝗡𝗙𝗜𝗗𝗘𝗡𝗖𝗘: 🔴🔴🔴⚪⚪ {analysis['confidence']}%

━━━━━━━━━━━━━━━━━━━━━━━━━

💡 𝗪𝗛𝗬 𝗪𝗘 𝗟𝗜𝗞𝗘 𝗜𝗧
• {analysis['reasons'][0]}
• {analysis['reasons'][1]}

⚠️ Small stake recommended!

━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 𝗥𝗜𝗦𝗞: 𝗛𝗜𝗚𝗛 🔴
🎰 𝗧𝗬𝗣𝗘: 𝗝𝗔𝗖𝗞𝗣𝗢𝗧 𝗣𝗜𝗖𝗞

━━━━━━━━━━━━━━━━━━━━━━━━━

📲 𝗠𝗢𝗥𝗘 𝗙𝗥𝗘𝗘 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡𝗦 👇
🔗 {self.telegram}
🎁 We post more FREE predictions on Telegram daily!

🔴🎰🔴🎰🔴🎰🔴🎰🔴🎰🔴🎰🔴

{tags}"""
    
    def generate_results_post(self, predictions, stats):
        """Generate Daily Results post"""
        results = ""
        for p in predictions:
            emoji = '✅' if p.get('result') == 'WIN' else '❌'
            risk = {'SAFE': '🟢 SAFE', 'MODERATE': '🟡 VALUE', 'RISKY': '🔴 HIGH'}.get(p.get('risk_level', ''), '⚪')
            
            results += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{risk} BET #{p.get('post_number', '?')}
{p.get('home_team', '')} vs {p.get('away_team', '')}
📊 FT: {p.get('final_score', 'N/A')}
📌 Pick: {p.get('prediction', '')} @ {p.get('odds', '')}
{emoji} {'𝗪𝗜𝗡' if p.get('result') == 'WIN' else '𝗟𝗢𝗦𝗦'}
"""
        
        profit = stats.get('profit', 0)
        sign = '+' if profit >= 0 else ''
        weekly = stats.get('weekly', {'wins': 0, 'losses': 0, 'hit_rate': 0})
        summary = "🏆 𝗚𝗥𝗘𝗔𝗧 𝗗𝗔𝗬! 🏆" if stats.get('wins', 0) >= 3 else "💪 We go again tomorrow! 💪"
        
        return f"""📊🏆📊🏆📊🏆📊🏆📊🏆📊🏆📊

📊 𝗗𝗔𝗜𝗟𝗬 𝗥𝗘𝗦𝗨𝗟𝗧𝗦 📊

🗓️ {stats.get('date', 'Today')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 𝗧𝗢𝗗𝗔𝗬'𝗦 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡 𝗥𝗘𝗦𝗨𝗟𝗧𝗦
{results}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 𝗗𝗔𝗜𝗟𝗬 𝗦𝗧𝗔𝗧𝗦
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Wins: {stats.get('wins', 0)}/5
❌ Losses: {stats.get('losses', 0)}/5
📈 Hit Rate: {stats.get('hit_rate', 0)}%
{'📈' if profit >= 0 else '📉'} Profit: {sign}{profit} units

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 𝗣𝗥𝗢𝗙𝗜𝗧 𝗖𝗔𝗟𝗖𝗨𝗟𝗔𝗧𝗢𝗥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$10/pick → 💰 ${sign}{round(profit * 10, 2)}
$50/pick → 💰 ${sign}{round(profit * 50, 2)}
$100/pick → 💰 ${sign}{round(profit * 100, 2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 𝗪𝗘𝗘𝗞𝗟𝗬 𝗥𝗘𝗖𝗢𝗥𝗗
{weekly.get('wins', 0)}W - {weekly.get('losses', 0)}L ({weekly.get('hit_rate', 0)}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📲 𝗝𝗢𝗜𝗡 𝗙𝗢𝗥 𝗧𝗢𝗠𝗢𝗥𝗥𝗢𝗪'𝗦 𝗣𝗜𝗖𝗞𝗦 👇
🔗 {self.telegram}

🎁 We post more FREE predictions on Telegram daily!
💎 Don't miss tomorrow's winners!

📊🏆📊🏆📊🏆📊🏆📊🏆📊🏆📊

#DailyResults #BettingResults #FreeTips #SportsBetting #Winner #Football"""
    
    def _hashtags(self, risk, league, home, away):
        """Generate hashtags"""
        tags = HASHTAGS.get(risk, [])[:4] + HASHTAGS.get('GENERAL', [])[:4]
        tags.append('#' + league.replace(' ', '').replace('-', ''))
        tags.append('#' + home.replace(' ', '').replace('-', ''))
        tags.append('#' + away.replace(' ', '').replace('-', ''))
        return ' '.join(tags[:12])
