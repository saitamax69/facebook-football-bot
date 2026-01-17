# 🏆 Sports Prediction Bot

Automated Facebook sports predictions using GitHub Actions - 100% FREE!

## ✨ Features

- 🤖 Fully automated - posts 6 times daily
- 🟢🟡🔴 3 risk levels - Safe, Value, Risky
- 📊 Daily results tracking
- 🆓 100% free hosting via GitHub Actions
- 📱 Facebook page integration

## 📅 Schedule (UTC)

| Time | Post | Risk |
|------|------|------|
| 07:00 | 🟢 Safe Bet #1 | Low |
| 09:00 | 🟢 Safe Bet #2 | Low |
| 12:00 | 🟡 Value Bet #3 | Medium |
| 15:00 | 🟡 Value Bet #4 | Medium |
| 18:00 | 🔴 High Odds #5 | High |
| 23:00 | 📊 Daily Results | Summary |

## 🚀 Setup

### 1. Fork Repository

### 2. Add Secrets

Go to: **Settings → Secrets → Actions**

| Secret | Description |
|--------|-------------|
| `RAPIDAPI_KEY` | RapidAPI key for Odds API |
| `FB_PAGE_ID` | Facebook Page ID |
| `FB_ACCESS_TOKEN` | Facebook Page Access Token |
| `PAT_TOKEN` | GitHub Personal Access Token |

### 3. Enable Actions

Go to **Actions** tab and enable workflows.

## 🔑 Getting PAT_TOKEN

1. GitHub → Settings → Developer Settings
2. Personal Access Tokens → Tokens (classic)
3. Generate new token
4. Select: `repo`, `workflow`
5. Copy token and add as secret

## 📱 Telegram

Join: https://t.me/+xAQ3DCVJa8A2ZmY8

## 📜 License

MIT
