"""
BACKEND - DATA HANDLER
Fetches stock data from yfinance and stores in Supabase database
"""

import logging
import warnings
warnings.filterwarnings('ignore')

import threading
import time
from datetime import datetime
import pandas as pd
import yfinance as yf
import pytz
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SETTINGS
# ============================================================================

# Stock symbols to track
US_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
INDIA_STOCKS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"]
ALL_STOCKS = US_STOCKS + INDIA_STOCKS

# Timings
DATA_REFRESH_SECONDS = 60  # Fetch data every 1 minute
NUM_LAGS = 10  # Number of lag features for ML

# Connect to Supabase (supports both .env and Streamlit secrets)
def get_supabase_credentials():
    """Get Supabase credentials from .env or Streamlit secrets"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    # If not in .env, try Streamlit secrets (for Streamlit Cloud)
    if not supabase_url or not supabase_key:
        try:
            import streamlit as st
            supabase_url = st.secrets.get("SUPABASE_URL")
            supabase_key = st.secrets.get("SUPABASE_KEY")
        except:
            pass
    
    return supabase_url, supabase_key

supabase_url, supabase_key = get_supabase_credentials()

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    logger.info("✅ Connected to Supabase")
else:
    logger.error("❌ Missing Supabase credentials!")
    supabase = None

# Background thread variables
collector_thread = None
collector_lock = threading.Lock()
data_collection_active = False

# ============================================================================
# SIMPLE HELPER FUNCTIONS
# ============================================================================

def is_indian_stock(ticker: str) -> bool:
    """Check if this is an Indian stock (ends with .NS or .BO)"""
    return ticker.upper().endswith((".NS", ".BO"))


def is_market_open(ticker: str = None) -> bool:
    """
    Check if stock market is currently open for trading
    
    Market Hours:
    - US Market: Monday-Friday, 9:30 AM - 4:00 PM EST
    - Indian Market: Monday-Friday, 9:15 AM - 3:30 PM IST
    
    Args:
        ticker: Stock symbol (if None, checks both markets)
    
    Returns:
        True if market is open, False if closed
    """
    now_utc = datetime.now(pytz.UTC)
    
    # Check US Market
    if ticker is None or not is_indian_stock(ticker):
        us_tz = pytz.timezone("America/New_York")
        us_time = now_utc.astimezone(us_tz)
        
        if us_time.weekday() < 5:  # Monday to Friday
            market_open = us_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = us_time.replace(hour=16, minute=0, second=0, microsecond=0)
            if market_open <= us_time <= market_close:
                return True
    
    # Check Indian Market
    if ticker is None or is_indian_stock(ticker):
        india_tz = pytz.timezone("Asia/Kolkata")
        india_time = now_utc.astimezone(india_tz)
        
        if india_time.weekday() < 5:  # Monday to Friday
            market_open = india_time.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = india_time.replace(hour=15, minute=30, second=0, microsecond=0)
            if market_open <= india_time <= market_close:
                return True
    
    return False


def get_market_status() -> dict:
    """
    Get current status of both markets with timestamps
    
    Returns:
        Dictionary with market open/closed status and current times
    """
    now_utc = datetime.now(pytz.UTC)
    
    # US Market Status
    us_tz = pytz.timezone("America/New_York")
    us_time = now_utc.astimezone(us_tz)
    us_open = False
    
    if us_time.weekday() < 5:
        market_open = us_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = us_time.replace(hour=16, minute=0, second=0, microsecond=0)
        us_open = market_open <= us_time <= market_close
    
    # Indian Market Status
    india_tz = pytz.timezone("Asia/Kolkata")
    india_time = now_utc.astimezone(india_tz)
    india_open = False
    
    if india_time.weekday() < 5:
        market_open = india_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = india_time.replace(hour=15, minute=30, second=0, microsecond=0)
        india_open = market_open <= india_time <= market_close
    
    return {
        'us_market_open': us_open,
        'indian_market_open': india_open,
        'any_market_open': us_open or india_open,
        'us_time': us_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'indian_time': india_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    }


# ============================================================================
# FETCH STOCK DATA
# ============================================================================

def fetch_stock_data(ticker: str) -> pd.DataFrame:
    """Fetch latest stock data from Yahoo Finance"""
    try:
        # Determine market type and settings
        is_indian = is_indian_stock(ticker)
        
        if is_indian:
            interval = "5m"  # 5-minute data for Indian stocks
            period = "60d"  # Last 60 days
            timezone = pytz.timezone("Asia/Kolkata")
        else:
            interval = "1m"  # 1-minute data for US stocks
            period = "7d"  # Last 7 days
            timezone = pytz.timezone("America/New_York")
        
        # Fetch data from yfinance (with 3 retry attempts)
        df = pd.DataFrame()
        for attempt in range(3):
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval, auto_adjust=False)
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for {ticker}: {e}")
                time.sleep(1)
        
        if df.empty:
            return pd.DataFrame()
        
        # Process the data
        df = df.reset_index()
        
        # Find datetime column (different APIs use different names)
        datetime_col = None
        for col in ("Datetime", "Date", "index"):
            if col in df.columns:
                datetime_col = col
                break
        if not datetime_col:
            datetime_col = df.columns[0]
        
        # Convert to proper timezone
        df[datetime_col] = pd.to_datetime(df[datetime_col], utc=False)
        if df[datetime_col].dt.tz is None:
            df[datetime_col] = df[datetime_col].dt.tz_localize(timezone, ambiguous="infer", nonexistent="shift_forward")
        else:
            df[datetime_col] = df[datetime_col].dt.tz_convert(timezone)
        
        # Convert to UTC for database storage
        df['date'] = df[datetime_col].dt.tz_convert(pytz.UTC).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Standardize column names (Open, High, Low, Close, Volume)
        colmap = {c.lower(): c for c in df.columns}
        required = {}
        for col_name in ['open', 'high', 'low', 'close', 'volume']:
            if col_name in df.columns:
                required[col_name] = col_name
            elif col_name in colmap:
                required[col_name] = colmap[col_name]
            else:
                return pd.DataFrame()  # Missing required column
        
        # Create clean dataframe
        result = df[['date', required['open'], required['high'], required['low'], required['close'], required['volume']]].copy()
        result.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        result['symbol'] = ticker
        
        # Reorder columns
        result = result[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
        result = result.dropna()
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()


def save_to_database(df: pd.DataFrame):
    """Save stock data to Supabase database"""
    if df.empty or not supabase:
        return
    
    try:
        records = df.to_dict('records')
        supabase.table('ohlcv').upsert(records, on_conflict='date,symbol').execute()
        logger.info(f"✅ Saved {len(records)} records to database")
    except Exception as e:
        logger.error(f"❌ Error saving to database: {e}")


# ============================================================================
# DATABASE QUERIES
# ============================================================================

def get_stock_data(symbol: str, limit: int = 1000) -> pd.DataFrame:
    """Get stock data from database"""
    if not supabase:
        return pd.DataFrame()
    
    try:
        response = supabase.table('ohlcv').select('*').eq('symbol', symbol).order('date', desc=True).limit(limit).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            return df.sort_values('date')
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error getting data for {symbol}: {e}")
        return pd.DataFrame()


def get_predictions(symbol: str = None, limit: int = 10) -> pd.DataFrame:
    """Get latest predictions from database"""
    if not supabase:
        return pd.DataFrame()
    
    try:
        query = supabase.table('model_predictions').select('*')
        if symbol:
            query = query.eq('symbol', symbol)
        query = query.order('date', desc=True).limit(limit)
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return pd.DataFrame()


def save_prediction(symbol: str, predicted_price: float, confidence: float):
    """Save prediction to database"""
    if not supabase:
        return
    
    try:
        data = {
            'symbol': symbol,
            'pred_close': predicted_price,
            'confidence': confidence,
            'date': datetime.utcnow().isoformat()
        }
        supabase.table('model_predictions').insert(data).execute()
        logger.info(f"✅ Saved prediction: {symbol} ${predicted_price:.2f}")
    except Exception as e:
        logger.error(f"Error saving prediction: {e}")


def save_model_performance(symbol: str, model_type: str, mae: float, mse: float, r2: float):
    """Save model performance metrics to database"""
    if not supabase:
        return
    
    try:
        data = {
            'symbol': symbol,
            'model_type': model_type,
            'mae': mae,
            'mse': mse,
            'r2': r2,
            'trained_at': datetime.utcnow().isoformat()
        }
        supabase.table('model_performance').insert(data).execute()
    except Exception as e:
        logger.error(f"Error saving performance: {e}")


def get_model_performance(symbol: str = None, limit: int = 1) -> pd.DataFrame:
    """Get latest model performance metrics from database"""
    if not supabase:
        return pd.DataFrame()
    
    try:
        query = supabase.table('model_performance').select('*')
        if symbol:
            query = query.eq('symbol', symbol)
        query = query.order('trained_at', desc=True).limit(limit)
        response = query.execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['trained_at'] = pd.to_datetime(df['trained_at'])
            return df
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        return pd.DataFrame()


# ============================================================================
# CREATE ML FEATURES
# ============================================================================

def create_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create machine learning features from stock price data"""
    if df.empty or len(df) < 100:
        return pd.DataFrame()
    
    df = df.copy().sort_values('date')
    
    # 1. LAG FEATURES (previous prices)
    for lag in range(1, NUM_LAGS + 1):
        df[f'lag_{lag}'] = df['close'].shift(lag)
    
    # 2. MOVING AVERAGES
    for window in [5, 10, 20, 50]:
        df[f'ma_{window}'] = df['close'].rolling(window=window).mean()
    
    # 3. RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. BOLLINGER BANDS
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    # 5. VOLUME MOVING AVERAGE
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    
    # Remove rows with NaN values
    df = df.dropna()
    return df


# ============================================================================
# BACKGROUND DATA COLLECTION
# ============================================================================

def _collect_data_continuously():
    """Background worker that fetches data continuously"""
    global data_collection_active
    
    logger.info("🚀 Started data collection")
    
    while data_collection_active:
        try:
            # Fetch data for all stocks
            for ticker in ALL_STOCKS:
                df = fetch_stock_data(ticker)
                if not df.empty:
                    save_to_database(df)
            
            logger.info(f"✅ Collected data for {len(ALL_STOCKS)} stocks")
            time.sleep(DATA_REFRESH_SECONDS)
            
        except Exception as e:
            logger.error(f"Collection error: {e}")
            time.sleep(10)


def start_data_collection():
    """Start background data collection"""
    global collector_thread, data_collection_active
    
    with collector_lock:
        if data_collection_active:
            logger.info("⚠️  Data collection already running")
            return
        
        data_collection_active = True
        collector_thread = threading.Thread(target=_collect_data_continuously, daemon=True)
        collector_thread.start()
        logger.info("✅ Data collection started")


def stop_data_collection():
    """Stop background data collection"""
    global data_collection_active
    
    with collector_lock:
        if not data_collection_active:
            return
        
        data_collection_active = False
        logger.info("🛑 Data collection stopped")


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'ALL_STOCKS',
    'fetch_stock_data',
    'get_stock_data',
    'get_predictions',
    'save_to_database',
    'save_prediction',
    'save_model_performance',
    'create_ml_features',
    'start_data_collection',
    'stop_data_collection',
    'is_market_open',
    'get_market_status'
]
