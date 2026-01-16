# 🤖 Facebook Football News Bot

An automated bot that posts daily football/soccer news to your Facebook Page. Runs entirely on GitHub Actions - no servers required!

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 📰 **Automatic News Fetching** - Gets latest football news from NewsAPI or TheSportsDB
- 🤖 **AI-Powered Content** - Uses OpenAI/Hugging Face to create engaging posts
- 📸 **Beautiful Images** - Downloads relevant photos from Unsplash or Pexels
- 📱 **Facebook Integration** - Posts directly to your Facebook Page via Graph API
- ⏰ **Scheduled Posting** - Runs daily at 8 AM UTC via GitHub Actions
- 🔄 **Smart Fallbacks** - Multiple API sources ensure reliability
- 🛡️ **URL-Free Posts** - Automatically strips all URLs for clean content

## 🚀 Quick Start

### Prerequisites

- A Facebook Page you manage
- GitHub account
- ~10 minutes for setup

### Step 1: Fork This Repository

Click the "Fork" button at the top right of this page.

### Step 2: Get Facebook Credentials

1. **Get your Page ID:**
   - Go to your Facebook Page
   - Click "About" → "Page ID" (or find it in the URL)

2. **Get a Page Access Token:**
   
   a. Go to [Facebook Developer Portal](https://developers.facebook.com/)
   
   b. Create an App (Business type)
   
   c. Add "Facebook Login for Business" product
   
   d. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   
   e. Select your App and Page
   
   f. Add permissions:
      - `pages_manage_posts`
      - `pages_read_engagement`
      - `pages_show_list`
   
   g. Click "Generate Access Token"
   
   h. **Extend the token** (important!):
      - Use the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
      - Click "Extend Access Token"
      - This gives you a 60-day token

   > ⚠️ **For permanent tokens**, convert your long-lived user token to a Page Access Token. See [Facebook's documentation](https://developers.facebook.com/docs/pages/access-tokens).

### Step 3: Get API Keys (Recommended)

| Service | Purpose | Sign Up Link | Free Tier |
|---------|---------|--------------|-----------|
| NewsAPI | News data | [newsapi.org](https://newsapi.org/register) | 100 req/day |
| Unsplash | Images | [unsplash.com/developers](https://unsplash.com/developers) | 50 req/hour |
| Pexels | Images (backup) | [pexels.com/api](https://www.pexels.com/api/) | 200 req/hour |
| OpenAI | Content AI | [platform.openai.com](https://platform.openai.com/) | Pay per use |
| Hugging Face | Content AI (free) | [huggingface.co](https://huggingface.co/settings/tokens) | Free tier |

### Step 4: Add GitHub Secrets

Go to your forked repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Required | Description |
|-------------|----------|-------------|
| `FB_PAGE_ID` | ✅ Yes | Your Facebook Page ID |
| `FB_PAGE_ACCESS_TOKEN` | ✅ Yes | Page Access Token |
| `NEWSAPI_KEY` | Recommended | NewsAPI.org API key |
| `UNSPLASH_ACCESS_KEY` | Recommended | Unsplash API key |
| `PEXELS_API_KEY` | Optional | Pexels API key |
| `OPENAI_API_KEY` | Recommended | OpenAI API key |
| `HUGGINGFACE_TOKEN` | Optional | Hugging Face token |

### Step 5: Enable GitHub Actions

1. Go to the "Actions" tab in your repo
2. Click "I understand my workflows, go ahead and enable them"
3. The bot will run automatically at 8 AM UTC daily

### Step 6: Test It!

1. Go to Actions → "Daily Football Post"
2. Click "Run workflow" → "Run workflow"
3. Watch the magic happen! ✨

## 📁 Project Structure
