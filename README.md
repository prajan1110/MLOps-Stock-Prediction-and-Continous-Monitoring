# End-to-End MLOps Pipeline for Stock Price Prediction

> Canonical setup and workflow documentation: [MLOPS_GUIDE.md](MLOPS_GUIDE.md). The legacy notes below are retained for context; follow the linked guide for current commands and configuration.

---

# Legacy Stock Prediction Notes



A real-time stock price prediction system that uses Machine Learning to predict stock prices during market hours. Tracks 10 stocks (5 US + 5 Indian) with automatic market hours detection.



## ✨ FeaturesA simple stock price prediction system using machine learning. Predicts prices for US and Indian stocks.



- **Smart Market Hours Detection**: Automatically detects when US and Indian stock markets are open

- **Real-time Data Collection**: Fetches live stock data every 1-5 minutes during market hours

- **Dual ML Models**: Uses Linear Regression + Random Forest, picks the best performer## ✨ What It DoesComplete real-time stock prediction system with machine learning and cloud database.A comprehensive real-time stock prediction system that collects stock data using yfinance and generates predictions using advanced machine learning models.

- **Live Web Dashboard**: Beautiful Streamlit interface with charts and predictions

- **Cloud Database**: Stores all data in Supabase (PostgreSQL cloud)

- **10 Stocks Tracked**:

  - 🇺🇸 US: AAPL, MSFT, GOOGL, AMZN, TSLA- Fetches live stock data from Yahoo Finance

  - 🇮🇳 India: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ITC.NS

- Trains machine learning models (Linear Regression + Random Forest)

## 🚀 Quick Start

- Predicts next price with confidence score---## 🚀 Features

### 1. Install Dependencies

- Only runs predictions during market hours

```powershell

pip install -r requirements.txt- Stores everything in Supabase cloud database

```

- Shows predictions in beautiful web dashboard

### 2. Setup Supabase

## 🚀 QUICK START (3 Steps)### Real-Time Data Collection

1. Go to [supabase.com](https://supabase.com) and create a free account

2. Create a new project## 📊 Tracked Stocks

3. Go to SQL Editor and run the `supabase_tables.sql` file

4. Copy your project URL and API key from Settings → API- **1-minute intervals** for US stocks, **5-minute intervals** for Indian stocks

5. Create a `.env` file in the project folder:

**US Stocks:** AAPL, MSFT, GOOGL, AMZN, TSLA  

```env

SUPABASE_URL=your_project_url_here**Indian Stocks:** RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, HINDUNILVR.NS### Step 1: Create Database Tables (2 minutes)- **Multiple stocks**: 10 stocks (5 US + 5 Indian)

SUPABASE_KEY=your_anon_key_here

```



### 3. Run the Application## 🚀 How to Run  - US: AAPL, MSFT, GOOGL, AMZN, TSLA



```powershell

python run.py

```### Step 1: Install1. Go to https://supabase.com and login  - Indian: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, HINDUNILVR.NS



The app will start:```bash

- Backend: Collects data and trains models

- Frontend: Opens at http://localhost:8501pip install -r requirements.txt2. Open your project: **fqzdorlokioibeuozsvi**- **Automatic updates**: Background collection every minute



## 📁 Project Structure```



```3. Click **SQL Editor** (left sidebar)- **Database storage**: SQLite database for persistent data

sharat_stock/

├── backend_data.py       # Fetches stock data and saves to database### Step 2: Setup Database

├── backend_model.py      # Trains ML models and makes predictions

├── backend_main.py       # Coordinates data collection and training4. Click **New Query**

├── frontend.py           # Streamlit web dashboard

├── run.py               # Main entry point - starts everything1. Create account at https://supabase.com

├── requirements.txt      # Python packages needed

├── supabase_tables.sql   # Database schema2. Create new project5. Open file `supabase_tables.sql` in this folder### Advanced Predictions

└── .env                 # Your Supabase credentials (create this)

```3. Get your credentials (Settings → API)



## 🎯 How It Works4. Create `.env` file:6. Copy ALL the SQL code- **Multiple ML models**: Linear Regression and Random Forest



### Simple Explanation```env



1. **Data Collection** (`backend_data.py`):SUPABASE_URL=your_url_here7. Paste in Supabase SQL Editor- **Feature engineering**: Technical indicators including:

   - Checks if market is open (US: 9:30 AM-4:00 PM EST, India: 9:15 AM-3:30 PM IST)

   - Downloads latest stock prices using yfinanceSUPABASE_KEY=your_key_here

   - Saves data to Supabase cloud database

```8. Click **RUN** button  - Price lags (1-10 periods)

2. **ML Training** (`backend_model.py`):

   - Trains two models: Linear Regression + Random Forest

   - Creates features: Moving averages, RSI, price changes

   - Picks the model with best accuracy### Step 3: Create Tables9. Wait for "Success" message  - Moving averages (5, 10, 20, 50)

   - Makes predictions for next price



3. **Coordination** (`backend_main.py`):

   - Runs data collection every 5 minutes when markets are open1. Open Supabase Dashboard10. Verify: Go to **Table Editor** → You should see 3 tables:  - RSI (Relative Strength Index)

   - Waits 10 minutes when markets are closed

   - Trains models automatically after collecting data2. Go to SQL Editor



4. **Dashboard** (`frontend.py`):3. Click New Query    - `ohlcv`  - Bollinger Bands

   - Shows market open/closed status with big colored banner

   - Displays candlestick charts with technical indicators4. Copy all code from `supabase_tables.sql`

   - Shows latest predictions with confidence scores

   - Updates automatically5. Paste and click RUN    - `model_predictions`  - Volume analysis



### Market Hours Behavior6. Check Table Editor - you should see 3 tables



- **Markets Open**: Actively fetches data every 5 minutes and makes new predictions    - `model_performance`- **Model selection**: Automatically selects best performing model by MAE

- **Markets Closed**: Shows last predictions, waits to resume when markets open

- **Status Display**: Green banner = Open, Red banner = Closed### Step 4: Start App



## 🔧 Troubleshooting```bash- **Confidence scoring**: Each prediction includes confidence level



### "Connection refused" or "Cannot connect to Supabase"python run.py

- Check your `.env` file has correct SUPABASE_URL and SUPABASE_KEY

- Verify your Supabase project is active at supabase.com```### Step 2: Verify Credentials (Already Done ✅)



### "No data available" in dashboard

- Wait 5-10 minutes for initial data collection

- Check that markets are currently openDashboard opens at http://localhost:8501### Interactive Dashboard

- Look at terminal output for errors



### "Module not found" errors

- Run: `pip install -r requirements.txt`## 📁 Simple File StructureYour `.env` file is already configured with Supabase credentials.- **Real-time charts**: Candlestick charts with technical indicators

- Make sure you're using Python 3.11 or higher



### Streamlit shows old errors after code changes

- Run: `streamlit cache clear````- **Prediction visualization**: Shows predictions vs actual prices

- Then restart: `python run.py`

5 Files Total:

## 📊 Technical Details

### Step 3: Run the Application- **Auto-refresh**: 30-second automatic data refresh

- **Python Version**: 3.11+

- **ML Models**: scikit-learn (LinearRegression, RandomForestRegressor)BACKEND (3 files):

- **Data Source**: yfinance (Yahoo Finance API)

- **Database**: Supabase (PostgreSQL)├── backend_data.py    - Fetches data, saves to database- **Responsive design**: Modern interface with background image

- **Frontend**: Streamlit with Plotly charts

- **Timezone Handling**: pytz (America/New_York, Asia/Kolkata)├── backend_model.py   - Trains models, makes predictions

- **Data Intervals**: 1-minute (US stocks), 5-minute (Indian stocks)

└── backend_main.py    - Coordinates everything**Option A: Double-click `START.bat`** (Windows - Easiest!)- **Multiple timeframes**: 1-30 days of historical data

## 🌐 Deploying to GitHub



### Prerequisites

- Git installed on your computerFRONTEND (1 file):

- GitHub account created

- Repository created at: https://github.com/SkandaKumarPV/Stock_prediction_DS-PROJECT.git└── frontend.py        - Web dashboard



### Steps to Push Code**Option B: Command line**## 📁 Project Structure



1. **Open PowerShell in project folder** (`sharat_stock/`)RUN (1 file):



2. **Initialize Git and push**:└── run.py            - Starts everything```powershell



```powershell```

# Initialize git repository

git initpython run.py```



# Add all files (except those in .gitignore)## 🧠 How It Works (Simple Explanation)

git add .

```sharat_stock/

# Commit with message

git commit -m "Initial commit: Stock prediction system with market hours detection"### 1. Data Collection (backend_data.py)



# Add your GitHub repository```├── data_handler.py      # Data collection and storage (Backend Part 1)

git remote add origin https://github.com/SkandaKumarPV/Stock_prediction_DS-PROJECT.git

Every 1 minute:

# Push to GitHub (main branch)

git push -u origin main→ Fetch latest stock prices from Yahoo Finance**That's it!** 🎉 Dashboard opens at http://localhost:8501├── model_handler.py     # Model training and predictions (Backend Part 2)

```

→ Save to Supabase database

### ⚠️ Important Security Notes

→ Add technical indicators (moving averages, RSI, etc.)├── final.py            # Main coordinator (Entry point)

- The `.gitignore` file will automatically exclude your `.env` file

- **Never commit your Supabase credentials** to GitHub```

- If you want to deploy to a server, add credentials as environment variables

- Your `.env` file stays local and private---├── streamlit_app.py    # Streamlit web dashboard (Frontend)



### Optional: Deploy to Streamlit Community Cloud### 2. Model Training (backend_model.py)



1. Go to [share.streamlit.io](https://share.streamlit.io)```├── run.py              # Easy startup script

2. Connect your GitHub account

3. Select your repositoryEvery 5 minutes (when markets open):

4. Set main file path: `frontend.py`

5. Add your Supabase secrets in "Advanced settings" → "Secrets":→ Get data from database## 📁 Project Structure├── START.bat           # Windows batch file for quick start

   ```

   SUPABASE_URL = "your_url_here"→ Train Linear Regression model

   SUPABASE_KEY = "your_key_here"

   ```→ Train Random Forest model├── requirements.txt    # Python dependencies

6. Click "Deploy"

→ Test both models

Note: On Streamlit Cloud, only the frontend will run. You'll need a separate service (like Heroku, Railway, or a VPS) to run the backend continuously.

→ Pick the one with lower error```├── data.db            # SQLite database (auto-created)

## 📝 Code Simplification

→ Make prediction

This codebase has been simplified for easy understanding:

- **Clear variable names**: `ALL_STOCKS` instead of `TICKERS`→ Save prediction to databasesharat_stock/├── assets/            # Background images and resources

- **Simple function names**: `fetch_stock_data()` instead of `fetch_latest_data()`

- **Step-by-step comments**: Each major step is numbered and explained```

- **Single responsibility**: Each file has one clear purpose

├── backend_data.py       # Data collection from yfinance → Supabase└── README.md          # Documentation

## 📄 License

### 3. Coordinator (backend_main.py)

This project is open source and available for educational purposes.

```├── backend_model.py      # Machine learning models & predictions```

## 🤝 Contributing

Checks every cycle:

Feel free to fork, modify, and submit pull requests. For major changes, please open an issue first.

→ Is market open?├── backend_main.py       # Coordinator (starts everything)

---

   Yes: Train models (every 5 min)

**Created with ❤️ for learning Machine Learning and Stock Market Analysis**

   No: Wait and check again (every 10 min)├── frontend.py           # Streamlit dashboard (web UI)## 🛠️ Installation

```

├── run.py                # Single entry point

### 4. Dashboard (frontend.py)

```├── supabase_tables.sql   # Database setup SQL (run once)1. **Clone or download** the project files

Shows:

→ Market status (OPEN/CLOSED)├── .env                  # Supabase credentials (configured ✅)2. **Install dependencies**:

→ Stock price chart

→ Prediction with confidence└── requirements.txt      # Python dependencies (installed ✅)   ```bash

→ Technical indicators

``````   pip install -r requirements.txt



## ⏰ Market Hours   ```



**US Market:** Monday-Friday, 9:30 AM - 4:00 PM EST  **Total: 3 backend + 1 frontend + 1 run = 5 files** ✨

**Indian Market:** Monday-Friday, 9:15 AM - 3:30 PM IST

## 🚀 Quick Start

**Smart Behavior:**

- Markets Open → Makes new predictions every 5 min---

- Markets Closed → Shows last predictions, waits

### **EASIEST WAY (Windows):**

## 📊 Database (3 Simple Tables)

## 🎯 What It DoesJust double-click `START.bat` file!

### Table 1: ohlcv (Stock Prices)

Stores: date, symbol, open, high, low, close, volume



### Table 2: model_predictions (Predictions)### When You Run `python run.py`:### **Option 1: Run Everything (Recommended)**

Stores: symbol, predicted_price, confidence, date

```bash

### Table 3: model_performance (Model Quality)

Stores: symbol, model_type, accuracy_metrics, trained_at1. **Backend starts automatically:**python run.py



## 🎨 Dashboard Features   - Fetches stock prices for 10 stocks (5 US + 5 Indian)```



- **Big Status Banner**: See if markets are OPEN (green) or CLOSED (red)   - Stores data in Supabase cloud databaseThis starts both backend (data collection + ML models) and frontend (dashboard).

- **Stock Selector**: Choose any of 10 stocks

- **Price Chart**: Interactive candlestick chart   - Trains ML models (Linear Regression + Random Forest)

- **Prediction Card**: Shows predicted price + confidence %

- **Technical Indicators**: Moving averages, RSI, Bollinger Bands   - Generates price predictions every 5 minutes### **Option 2: Manual Start**

- **Model Info**: Which model was used + how accurate it is

   - Updates data every 1 minute

## 🔧 Troubleshooting

**Backend (data collection + predictions):**

**Problem:** "Could not find table 'public.ohlcv'"  

**Solution:** You didn't create tables. Do Step 3 again.2. **Frontend opens in browser:**```bash



**Problem:** "Missing Supabase credentials"     - Dashboard at http://localhost:8501python final.py

**Solution:** Create `.env` file with your URL and key.

   - Interactive candlestick charts```

**Problem:** "No data available"  

**Solution:** Wait 1-2 minutes for data collection to start.   - Technical indicators (Moving Averages, RSI, Bollinger Bands)



**Problem:** "Models not training"     - Real-time price predictions with confidence scores**Frontend (web dashboard):**

**Solution:** Check if markets are open. Models only work during market hours.

   - Auto-refreshes every 30 seconds```bash

## 📖 Code Explained Simply

python -m streamlit run streamlit_app.py

### backend_data.py (163 lines)

- `fetch_stock_data()` - Gets data from Yahoo Finance3. **View data in Supabase:**```

- `save_to_database()` - Saves data to Supabase

- `is_market_open()` - Checks if trading is happening now   - Go to Supabase Dashboard → Table Editor

- `create_ml_features()` - Adds moving averages, RSI, etc.

- `start_data_collection()` - Runs fetch loop every minute   - See all stock prices, predictions, and model performanceThe dashboard will open at: **http://localhost:8501**



### backend_model.py (151 lines)   - Edit data manually if needed

- `prepare_training_data()` - Splits data into train/test

- `train_two_models()` - Trains Linear Regression + Random Forest   - Export to CSV anytime## 🗄️ Database Configuration

- `select_best_model()` - Picks model with lowest error

- `calculate_confidence_score()` - Gives prediction confidence 0-100%

- `train_and_predict_one_stock()` - Complete flow for one stock

---### **Option 1: Supabase (Recommended - Cloud Database with Dashboard)** 🚀

### backend_main.py (143 lines)

- `_train_models_continuously()` - Background worker loop

- `start_model_training()` - Starts the training thread

- `start_backend()` - Starts data + training## 📊 Tracked Stocks**Why Supabase?**



### frontend.py (716 lines)- ✅ **Beautiful web dashboard** to view/edit data

- Market status display

- Stock selector### US Stocks (5):- ✅ **Real-time updates** - see data changes instantly

- Candlestick charts

- Prediction display- AAPL - Apple Inc.- ✅ **Free tier** with generous limits

- Technical indicator plots

- Model performance metrics- MSFT - Microsoft Corp.- ✅ **Automatic backups** and scalability



### run.py (78 lines)- GOOGL - Alphabet Inc.- ✅ **No installation** needed - fully cloud-based

- `start_backend()` - Starts backend in thread

- `start_frontend()` - Starts Streamlit dashboard- AMZN - Amazon.com Inc.

- `main()` - Entry point that starts everything

- TSLA - Tesla Inc.**Quick Setup (5 minutes):**

## 💡 Simple Concepts

```powershell

### What is Machine Learning?

Computer learns patterns from past data to predict future prices.### Indian Stocks (5):# 1. Install Supabase package



### What is Linear Regression?- RELIANCE.NS - Reliance Industriespip install supabase python-dotenv

Draws a straight line through data points to predict trend.

- TCS.NS - Tata Consultancy Services

### What is Random Forest?

Makes many decision trees and averages their predictions.- HDFCBANK.NS - HDFC Bank# 2. Follow the quick start guide



### What is Confidence Score?- INFY.NS - Infosys Ltd.# See QUICKSTART_SUPABASE.md

How sure the model is: 0% = guessing, 100% = very confident

- HINDUNILVR.NS - Hindustan Unilever```

### What is MAE (Mean Absolute Error)?

Average prediction error in dollars. Lower = better.



### What is R² Score?---**📖 See [QUICKSTART_SUPABASE.md](QUICKSTART_SUPABASE.md) for 5-minute setup**  

Model accuracy: 0 = terrible, 1 = perfect

**📖 See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for detailed guide**

## ⚠️ Important Notes

## 🔧 How It Works

- This is for LEARNING only, not financial advice

- Stock predictions are never 100% accurate### **Option 2: SQLite (Default - Local Development)**

- Always do your own research before investing

- Never invest money you can't afford to lose### Data Flow:No setup needed! The app automatically creates `data.db` file.



## 📦 What Gets Installed```



- `streamlit` - Web dashboard frameworkyfinance API### **Option 3: PostgreSQL (Server Deployment)**

- `pandas` - Data manipulation

- `yfinance` - Gets stock data from Yahoo    ↓For production/cloud deployment, set the `DATABASE_URL` environment variable:

- `scikit-learn` - Machine learning models

- `plotly` - Interactive chartsbackend_data.py (fetch & store)

- `supabase` - Cloud database

- `pytz` - Timezone handling    ↓```powershell



## 🎯 Simple WorkflowSupabase Database (cloud)# Windows PowerShell



```    ↓$env:DATABASE_URL="postgresql://username:password@host:5432/database"

1. Run: python run.py

   ↓backend_model.py (train ML models)

2. Backend starts in background

   ↓    ↓# Mac/Linux

3. Fetches data every 1 min

   ↓Predictions saved to Supabaseexport DATABASE_URL="postgresql://username:password@host:5432/database"

4. Trains models every 5 min (when markets open)

   ↓    ↓```

5. Saves predictions to database

   ↓frontend.py (display dashboard)

6. Dashboard shows everything in real-time

```    ↓**📖 See [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for detailed setup instructions including:**



## 📈 What Makes a Good Prediction?Your Browser (http://localhost:8501)- Local PostgreSQL installation



- ✅ Confidence > 70%```- Free cloud databases (ElephantSQL, Supabase)

- ✅ Model R² > 0.8

- ✅ Low error (MAE < $2)- Heroku deployment

- ✅ Recent data available

- ✅ Low price volatility### Machine Learning:- AWS/Azure/GCP setup



## 🚦 Color Meanings- **Features:** Price lags, moving averages (5/10/20/50), RSI, Bollinger Bands, volume



- 🟢 Green = Market OPEN / Good prediction- **Models:** Linear Regression + Random Forest (100 trees)## �📊 How It Works

- 🔴 Red = Market CLOSED / Low confidence  

- 🟡 Yellow = Medium confidence- **Selection:** Automatically picks best model (lowest error)

- 🔵 Blue = Information

- **Validation:** 80/20 train/test split### Backend Architecture (2-File System)

## ❓ FAQ

- **Confidence:** Based on R² score, MAE, and volatility

**Q: How often do predictions update?**  

A: Every 5 minutes when markets are open.#### **1. data_handler.py** - Data Collection & Storage



**Q: Can I add more stocks?**  ### Background Workers:- Fetches stock data from yfinance API

A: Yes, edit `ALL_STOCKS` list in `backend_data.py`.

- **Data Collection:** Runs every 60 seconds- Stores data in database (SQLite or PostgreSQL)

**Q: Is Supabase free?**  

A: Yes, free tier is enough for this project.- **Model Training:** Runs every 300 seconds (5 minutes)- Handles timezone conversions (US Eastern / Indian IST)



**Q: Do I need to keep it running 24/7?**  - **Dashboard:** Auto-refreshes every 30 seconds- Creates features for machine learning

A: No, it automatically handles market hours.

- Manages background data collection thread

**Q: Can I use this for real trading?**  

A: No, this is educational only. Not financial advice.---



---#### **2. model_handler.py** - Model Training & Prediction



**Made for learning purposes** 📚  ## ⚙️ Configuration- Trains Linear Regression and Random Forest models

**Have fun exploring machine learning!** 🚀

- Validates models using train/test split

### Change Data Collection Interval:- Selects best model based on MAE (Mean Absolute Error)

Edit `backend_data.py`:- Generates predictions with confidence scores

```python- Stores predictions and performance metrics

REFRESH_INTERVAL = 60  # seconds (default: 1 minute)

```#### **3. final.py** - Coordinator

- Integrates data_handler and model_handler

### Change Model Training Interval:- Manages the complete pipeline:

Edit `backend_main.py`:  1. Collect data → 2. Train models → 3. Generate predictions

```python- Provides convenience functions for frontend

time.sleep(300)  # seconds (default: 5 minutes)

```### Frontend

**streamlit_app.py** - Interactive Dashboard

### Add/Remove Stocks:- Real-time price charts with technical indicators

Edit `backend_data.py`:- Candlestick charts with MA, RSI, Bollinger Bands

```python- Prediction visualization

US_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]- Auto-refresh every 30 seconds

INDIAN_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"]

```## 🎯 Key Features



---### Enhanced Predictions

- **Advanced features**: RSI, Bollinger Bands, multiple moving averages

## 🐛 Troubleshooting- **Better models**: Random Forest in addition to Linear Regression

- **Feature scaling**: StandardScaler for improved model performance

### Error: "Could not find the table 'public.ohlcv'"- **Confidence scoring**: Dynamic confidence based on market volatility

**Problem:** Tables not created in Supabase  

**Solution:** Run the SQL from `supabase_tables.sql` in Supabase SQL Editor (Step 1 above)### Real-Time Capabilities

- **Threading**: Background data collection doesn't block UI

### Error: "Missing Supabase credentials"- **1-minute updates**: More frequent data collection for better predictions

**Problem:** `.env` file missing or incorrect  - **Error handling**: Robust error handling and logging

**Solution:** Your `.env` is already configured, but verify it has:- **Database optimization**: Efficient data storage and retrieval

```

SUPABASE_URL=https://fqzdorlokioibeuozsvi.supabase.co### User Experience

SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...- **Modern UI**: Beautiful, responsive Streamlit interface

```- **Interactive charts**: Advanced Plotly visualizations

- **Auto-refresh**: Automatic data updates

### Frontend doesn't load- **Performance metrics**: Model accuracy and confidence scores

**Problem:** Streamlit not starting  

**Solution:** Run directly:## 📈 Technical Details

```powershell

python -m streamlit run frontend.py### Database Schema

```- **ohlcv**: Stock price data (Open, High, Low, Close, Volume)

- **predictions**: Model predictions with confidence scores

### No data showing in dashboard- **model_performance**: Model accuracy metrics

**Problem:** Data collection hasn't started yet  

**Solution:** Wait 1-2 minutes for initial data collection### Models Used

- **Linear Regression**: Fast, interpretable baseline model

### Backend errors- **Random Forest**: Ensemble method for better accuracy

**Problem:** Dependencies missing  - **Feature Selection**: Automatic selection of best features

**Solution:** Reinstall:- **Cross-validation**: Model performance evaluation

```powershell

pip install -r requirements.txt### Performance Metrics

```- **MAE**: Mean Absolute Error

- **MSE**: Mean Squared Error

### Connection test- **RMSE**: Root Mean Squared Error

```powershell- **R² Score**: Coefficient of determination

python -c "from backend_data import supabase; print('Connected:', supabase is not None)"

```## 🔧 Configuration

Should show: `Connected: True`

### Tickers

---Edit the `TICKERS` list in `final.py` to add/remove stocks:

```python

## 🛑 Stopping the ApplicationTICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]

```

Press **Ctrl+C** in the terminal

### Refresh Interval

The system will:Change the data collection frequency in `final.py`:

1. Stop data collection thread```python

2. Stop model training threadREFRESH_INTERVAL = 1  # minutes

3. Close Streamlit dashboard```

4. Exit cleanly

### Prediction Features

---Modify the `N_LAGS` variable to change the number of price lags:

```python

## 📊 MonitoringN_LAGS = 10  # Number of price lags for prediction

```

### Check Logs:

- Terminal shows real-time logs## 🐛 Troubleshooting

- Look for ✅ (success) or ❌ (error) symbols

### Common Issues

### Check Supabase Dashboard:1. **No data showing**: Market might be closed, wait for market hours

1. Go to https://supabase.com/dashboard/project/fqzdorlokioibeuozsvi2. **Predictions not updating**: Ensure data collection is running

2. **Table Editor** → View all your data3. **Database errors**: Delete `data.db` to reset the database

   - `ohlcv` table → Stock prices4. **Import errors**: Run `pip install -r requirements.txt`

   - `model_predictions` table → ML predictions

   - `model_performance` table → Model accuracy metrics### Logs

3. **SQL Editor** → Run custom queriesCheck the console output for detailed logging information about data collection and prediction processes.

4. **Database** → View table structure and indexes

## 📝 Notes

### Check Dashboard:

- Open http://localhost:8501- **Market hours**: Data collection works best during market hours

- Select any stock from dropdown- **Internet required**: yfinance needs internet connection

- View real-time charts and predictions- **Storage**: Database grows over time, consider periodic cleanup

- Check confidence scores- **Performance**: More data = better predictions



---## 🤝 Contributing



## 📈 FeaturesFeel free to submit issues and enhancement requests!



### Data Collection:## 📄 License

✅ Real-time stock prices from yfinance  

✅ 1-minute intervals (US stocks)  This project is open source and available under the MIT License.

✅ 5-minute intervals (Indian stocks)  
✅ Automatic timezone handling (UTC/EST/IST)  
✅ Cloud storage in Supabase  

### Machine Learning:
✅ Linear Regression model  
✅ Random Forest (100 trees)  
✅ Automatic model selection  
✅ 15+ technical features  
✅ Confidence scoring (0-100%)  
✅ Performance tracking (MAE, MSE, R²)  

### Dashboard:
✅ Interactive candlestick charts  
✅ Moving averages (5, 10, 20, 50-day)  
✅ RSI indicator  
✅ Bollinger Bands  
✅ Volume analysis  
✅ Price predictions with confidence  
✅ Auto-refresh (30 seconds)  
✅ Beautiful UI with background image  

### Supabase Integration:
✅ Cloud database with web dashboard  
✅ Real-time data synchronization  
✅ Manual data editing through UI  
✅ CSV export functionality  
✅ Automatic backups  
✅ Scalable to millions of records  

---

## 💡 Tips

1. **First run takes 1-2 minutes** - Initial data collection for all stocks
2. **Models need 50+ data points** - Wait for data to accumulate
3. **Best predictions after 1 hour** - More historical data = better accuracy
4. **Monitor Supabase dashboard** - Verify data is being stored correctly
5. **Enable auto-refresh in frontend** - See updates in real-time
6. **Check confidence scores** - Higher confidence = more reliable prediction

---

## 📦 Dependencies

All installed via `requirements.txt`:
- **pandas, numpy** - Data processing
- **scikit-learn** - Machine learning
- **yfinance** - Stock data API
- **streamlit, plotly** - Dashboard and charts
- **supabase** - Cloud database
- **python-dotenv** - Environment variables
- **pytz** - Timezone handling

---

## 🎓 File Descriptions

### Backend Files:

**1. backend_data.py** (351 lines)
- Fetches stock data from yfinance API
- Stores in Supabase database
- Creates ML features (lags, moving averages, RSI, Bollinger Bands)
- Background data collection worker (every 60 seconds)
- Database query functions

**2. backend_model.py** (223 lines)
- Trains Linear Regression and Random Forest models
- Validates models on test data
- Selects best model based on MAE
- Generates price predictions
- Calculates confidence scores
- Saves predictions and performance metrics

**3. backend_main.py** (152 lines)
- Coordinates data collection and model training
- Manages background worker threads
- Initial data collection on startup
- Main entry point for backend

### Frontend File:

**frontend.py** (646 lines)
- Streamlit web dashboard
- Interactive Plotly charts
- Real-time data display
- Technical indicator visualization
- Prediction display with confidence
- Auto-refresh functionality

### Run File:

**run.py** (88 lines)
- Single entry point for entire system
- Starts backend in background thread
- Starts frontend (Streamlit)
- Handles graceful shutdown

---

## 🚀 Advanced Usage

### Run Backend Only:
```powershell
python backend_main.py
```

### Run Frontend Only:
```powershell
python -m streamlit run frontend.py
```

### Collect Initial Data:
```python
from backend_main import collect_initial_data
collect_initial_data()
```

### Train Models Manually:
```python
from backend_model import train_and_predict_all
train_and_predict_all()
```

---

## 📋 Quick Reference

| Action | Command |
|--------|---------|
| Run application | `python run.py` |
| Run backend only | `python backend_main.py` |
| Run frontend only | `streamlit run frontend.py` |
| Test connection | `python -c "from backend_data import supabase; print(supabase)"` |
| Stop application | Press `Ctrl+C` |

| URL | Purpose |
|-----|---------|
| http://localhost:8501 | Dashboard |
| https://supabase.com/dashboard/project/fqzdorlokioibeuozsvi | Database |

---

**Last Updated:** October 26, 2025  
**Status:** ✅ Ready to Run  
**Next Step:** Create tables in Supabase, then run `python run.py`
