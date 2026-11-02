# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites
- ✅ GitHub repository: `https://github.com/prajan1110/MLOps-Stock-Prediction-and-Continous-Monitoring.git`
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
   - **Repository**: `prajan1110/MLOps-Stock-Prediction-and-Continous-Monitoring`
   - **Branch**: `main`
   - **Main file path**: `frontend.py`
   - **App URL** (optional): Choose a custom subdomain or use auto-generated

### 3. Configure Secrets (Environment Variables)
1. Click **"Advanced settings"** before deploying
2. In the **Secrets** section, paste this TOML format:

```toml
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_anon_key"
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
## Supabase Database Setup

Configure your own Supabase project URL and anon key as secrets. Create the tables by running `supabase_tables.sql` in the Supabase SQL Editor.

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

## Provider Limits

Check Streamlit Community Cloud's current availability, resource limits, sleep behavior, and pricing before deployment. These policies can change.

## Docker Compose Deployment

Train/materialize model artifacts first with `dvc repro` (or `dvc pull` on a fresh machine), then create a local `.env` from `.env.example`. The `.env` file is ignored by Git.

```powershell
docker compose up --build
```

- Streamlit dashboard: `http://localhost:8501`
- FastAPI inference: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

The dashboard and inference API are separate containers. The API mounts the local `models/` directory read-only; without DVC model artifacts, `/health` reports zero models and `/predict` returns 404. Never bake credentials into either image.

## Streamlit Community Cloud

Deploy the existing dashboard from the GitHub repository `prajan1110/MLOps-Stock-Prediction-and-Continous-Monitoring`, using the branch you intend to publish and root entry point `frontend.py`. Install dependencies from the repository's pinned `requirements.txt`.

In the app's **Settings → Secrets**, configure TOML values:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-publishable-or-anon-key"
```

Do not paste a Supabase secret/service-role key into source control or use it as a browser-exposed key. The current SQL schema grants broad table access; replace those policies with appropriately restricted RLS policies before making the database publicly accessible. Streamlit Cloud deployment requires GitHub/Streamlit account access and must be completed from the hosting dashboard.

## Support
- Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud
- Supabase docs: https://supabase.com/docs
