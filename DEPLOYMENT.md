# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites
- ✅ GitHub repository: `https://github.com/SkandaKumarPV/Stock_prediction_DS-PROJECT.git`
- ✅ Supabase database: Already configured
- ✅ Code pushed to GitHub

## Step-by-Step Deployment

### 1. Sign Up for Streamlit Cloud (FREE)
1. Go to https://share.streamlit.io/
2. Click "Sign up" (or "Continue with GitHub")
3. Authorize Streamlit Cloud to access your GitHub account

### 2. Deploy Your App
1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository**: `SkandaKumarPV/Stock_prediction_DS-PROJECT`
   - **Branch**: `main`
   - **Main file path**: `frontend.py`
   - **App URL** (optional): Choose a custom subdomain or use auto-generated

### 3. Configure Secrets (Environment Variables)
1. Click **"Advanced settings"** before deploying
2. In the **Secrets** section, paste this TOML format:

```toml
SUPABASE_URL = "https://fqzdorlokioibeuozsvi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxemRvcmxva2lvaWJldW96c3ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0ODQxODksImV4cCI6MjA3NzA2MDE4OX0.1oDqpvoTRfSPZKANc592hV4LZdOmia1L6qjzmaG7AVA"
```

3. Click **"Save"**

### 4. Deploy!
1. Click **"Deploy!"** button
2. Wait 2-5 minutes for initial build and deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

### 5. Verify Database Connection
Once deployed:
1. Open your app URL
2. Check if stock data loads correctly
3. Verify predictions are being generated
4. Monitor the Streamlit Cloud logs for any errors

## Post-Deployment

### Update Secrets Later (if needed)
1. Go to https://share.streamlit.io/
2. Click on your app
3. Click **"Settings"** → **"Secrets"**
4. Edit and save

### Automatic Redeployment
- Every time you push to the `main` branch on GitHub, Streamlit Cloud will automatically rebuild and redeploy your app
- No manual action needed!

### View Logs
- Click on your app in Streamlit Cloud dashboard
- Click **"Manage app"** → **"Logs"** to see real-time logs

## Supabase Database Setup (Already Done ✅)

Your Supabase database is already configured at:
- **URL**: https://fqzdorlokioibeuozsvi.supabase.co
- **Tables**: Created via `supabase_tables.sql`

If you need to recreate tables:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **SQL Editor**
4. Run the SQL from `supabase_tables.sql`

## Troubleshooting

### App won't start
- Check Streamlit Cloud logs for errors
- Verify all dependencies are in `requirements.txt`
- Ensure secrets are properly formatted (TOML syntax)

### Database connection errors
- Verify Supabase URL and key in secrets
- Check Supabase project is active (not paused)
- Ensure tables exist in Supabase

### Module not found errors
- Add missing packages to `requirements.txt`
- Push changes to GitHub
- Streamlit Cloud will auto-redeploy

## Free Tier Limits (Streamlit Cloud)
- ✅ Unlimited public apps
- ✅ 1GB RAM per app
- ✅ Automatic redeployment from GitHub
- ✅ Custom subdomains
- ✅ HTTPS included

## Support
- Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud
- Supabase docs: https://supabase.com/docs
