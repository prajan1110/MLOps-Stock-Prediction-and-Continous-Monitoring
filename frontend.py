"""
================================================================================
STOCK PREDICTION DASHBOARD - FRONTEND (STREAMLIT)
================================================================================
Interactive dashboard displaying:
1. Real-time stock price data
2. Technical indicators (MA, RSI, Bollinger Bands)
3. Price predictions with confidence scores
4. Model performance metrics
================================================================================
"""

# ============================================================================
# IMPORTS AND SETUP
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import pytz
import base64
from pathlib import Path

# Import from backend
from backend_data import get_stock_data, get_predictions, is_market_open, get_market_status

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# STYLING AND BACKGROUND
# ============================================================================

def _set_background_image_local(image_path: str):
    """Load local background image"""
    try:
        p = Path(image_path)
        if not p.exists():
            logger.warning(f"Background image not found at {image_path}")
            return
        data = p.read_bytes()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
        <style>
        .stApp {{
          background-image: url("data:image/jpeg;base64,{b64}");
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          background-attachment: fixed;
        }}
        .block-container {{
          background-color: rgba(0,0,0,0.45);
          border-radius: 8px;
        }}
        .main-header {{ 
          color: #fff; 
          text-shadow: 0 1px 3px rgba(0,0,0,0.6); 
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        logger.error(f"Error loading background image: {e}")

# Load background image
_set_background_image_local("assets/stock_bg.jpg")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Stock tickers
US_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
INDIAN_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"]
TICKERS = US_TICKERS + INDIAN_TICKERS

# Ticker display names
TICKER_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys Ltd.",
    "HINDUNILVR.NS": "Hindustan Unilever",
}

# ============================================================================
# DATA CACHING
# ============================================================================

@st.cache_data(ttl=30)
def get_cached_stock_data(ticker, days=7):
    """Cache stock data for 30 seconds"""
    return get_stock_data(ticker, days)

@st.cache_data(ttl=10)
def get_cached_predictions(ticker=None, limit=10):
    """Cache predictions for 10 seconds"""
    df = get_predictions(ticker, limit)
    if df is None:
        return pd.DataFrame(columns=["date", "pred_close", "confidence"])
    for c in ["date", "pred_close", "confidence"]:
        if c not in df.columns:
            df[c] = np.nan
    return df



# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.header("🎛 Controls")
    
    # Stock selection
    with st.expander("📊 Stock Selection", expanded=True):
        us_ticker = st.selectbox("US Stock", US_TICKERS, index=0, key="us_ticker")
        indian_ticker = st.selectbox("Indian Stock", INDIAN_TICKERS, index=0, key="indian_ticker")
        stock_type = st.radio("View", ["US Stock", "Indian Stock"], index=0, key="stock_type")
        selected_ticker = us_ticker if stock_type == "US Stock" else indian_ticker

    # View options
    with st.expander("⏱ View Options", expanded=False):
        days_back = st.slider("Days to Display", min_value=1, max_value=30, value=7, key="days_back")
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=True, key="auto_refresh")
        if st.button("Manual Refresh"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")
    st.header("ℹ️ Info")
    st.info("� Data updates every 1 minute\n\n🤖 Predictions during market hours\n\n⏰ US: 9:30 AM - 4:00 PM EST\n\n⏰ India: 9:15 AM - 3:30 PM IST")

# ============================================================================
# MAIN HEADER WITH MARKET STATUS
# ============================================================================

st.markdown('<h1 class="main-header">📈 Real-Time Stock Predictor</h1>', unsafe_allow_html=True)

# Prominent Market Status Banner
market_status = get_market_status()
col_status1, col_status2, col_status3 = st.columns([1, 1, 1])

with col_status1:
    if market_status['any_market_open']:
        st.success("### 🟢 MARKETS OPEN\n**Live Predictions Active**")
    else:
        st.error("### 🔴 MARKETS CLOSED\n**Showing Previous Predictions**")

with col_status2:
    us_emoji = "🟢" if market_status['us_market_open'] else "🔴"
    us_label = "OPEN" if market_status['us_market_open'] else "CLOSED"
    st.info(f"### {us_emoji} US Market\n**{us_label}**\n{market_status['us_time']}")

with col_status3:
    india_emoji = "🟢" if market_status['indian_market_open'] else "🔴"
    india_label = "OPEN" if market_status['indian_market_open'] else "CLOSED"
    st.info(f"### {india_emoji} Indian Market\n**{india_label}**\n{market_status['indian_time']}")

st.markdown("---")

# ============================================================================
# MAIN LAYOUT
# ============================================================================

col_main, col_side = st.columns([3, 1])

with col_main:
    stock_display_name = TICKER_NAMES.get(selected_ticker, selected_ticker)
    
    # Show specific ticker market status
    ticker_is_open = is_market_open(selected_ticker)
    ticker_type = "US" if selected_ticker not in INDIAN_TICKERS else "Indian"
    status_emoji = "🟢" if ticker_is_open else "🔴"
    status_text = "OPEN - Live Data" if ticker_is_open else "CLOSED - Historical Data"
    
    st.subheader(f"📊 {stock_display_name} ({selected_ticker}) {status_emoji} {status_text}")

    stock_data = get_cached_stock_data(selected_ticker, days_back)

    if stock_data is None or stock_data.empty:
        st.warning(f"No data available for {selected_ticker}")
        st.info("Data collection may be in progress. Please refresh or wait a minute.")
    else:
        # Prepare data
        stock_data['date'] = pd.to_datetime(stock_data['date'], utc=True)
        stock_data = stock_data.sort_values('date', ascending=False).reset_index(drop=True)

        # ====================================================================
        # KEY PERFORMANCE INDICATORS (KPIs)
        # ====================================================================
        
        latest = stock_data.iloc[0]
        prev = stock_data.iloc[1] if len(stock_data) > 1 else latest

        latest_price = float(latest['close'])
        prev_price = float(prev['close'])
        price_change = latest_price - prev_price
        change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0.0

        currency = "₹" if selected_ticker in INDIAN_TICKERS else "$"
        volume = int(latest['volume'])
        day_high = float(latest['high'])
        day_low = float(latest['low'])

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric(
                label="Current Price",
                value=f"{currency}{latest_price:,.2f}",
                delta=f"{currency}{price_change:,.2f} ({change_pct:.2f}%)" if prev_price != 0 else "—",
            )
        with k2:
            st.metric(label="Volume", value=f"{volume:,}")
        with k3:
            st.metric(label="Day High", value=f"{currency}{day_high:,.2f}")
        with k4:
            st.metric(label="Day Low", value=f"{currency}{day_low:,.2f}")



        # ====================================================================
        # SIMPLE PRICE CHART
        # ====================================================================
        
        def create_simple_price_chart(df, ticker):
            """Create simple line chart with price and moving average"""
            df = df.sort_values("date").reset_index(drop=True).copy()
            df['date'] = pd.to_datetime(df['date'], utc=True)
            
            fig = go.Figure()
            
            # Close price line
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['close'],
                    mode='lines',
                    name='Close',
                    line=dict(color='cyan', width=2)
                )
            )
            
            # 5-period moving average
            if len(df) >= 5:
                df['ma_5'] = df['close'].rolling(window=5).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df['ma_5'],
                        mode='lines',
                        name='MA 5',
                        line=dict(color='yellow', width=1.5, dash='dash')
                    )
                )
            
            fig.update_layout(
                template="plotly_dark",
                height=320,
                title=f"{ticker} - Recent Close Price",
                showlegend=True,
                margin=dict(t=40, b=20)
            )
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Price")
            
            return fig

        fig_simple = create_simple_price_chart(stock_data, selected_ticker)
        st.plotly_chart(fig_simple, width='stretch')



        # ====================================================================
        # ADVANCED TECHNICAL ANALYSIS CHART
        # ====================================================================
        
        def create_advanced_candlestick_chart(df, ticker):
            """
            Create multi-panel chart with:
            1. Candlestick chart + Moving Averages + Bollinger Bands
            2. RSI indicator
            3. Volume bars
            4. Predictions overlay
            """
            df = df.sort_values("date").reset_index(drop=True)
            df['date'] = pd.to_datetime(df['date'], utc=True)
            
            # Identify market gaps
            df['time_diff'] = df['date'].diff().dt.total_seconds().fillna(0)
            gap_threshold = 3600 if not ticker.endswith(".NS") else 6 * 3600
            gap_indices = df.index[df['time_diff'] > gap_threshold].tolist()

            # Insert NaN rows at gaps to break chart lines
            if gap_indices:
                rows_to_insert = []
                for idx in gap_indices:
                    nan_row = df.iloc[idx - 1].copy()
                    nan_row[['open', 'high', 'low', 'close', 'volume']] = np.nan
                    nan_row['date'] = df.iloc[idx]['date'] - pd.Timedelta(seconds=1)
                    rows_to_insert.append(nan_row)
                df = pd.concat([df, pd.DataFrame(rows_to_insert)], ignore_index=True)
                df = df.sort_values('date').reset_index(drop=True)

            # Calculate technical indicators
            df['ma_5'] = df['close'].rolling(window=5).mean()
            df['ma_10'] = df['close'].rolling(window=10).mean()
            df['ma_20'] = df['close'].rolling(window=20).mean()
            df['ma_50'] = df['close'].rolling(window=50).mean()

            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

            # Create subplots
            fig = make_subplots(
                rows=4, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.05,
                subplot_titles=(
                    f'{ticker} Price Chart with Technical Indicators',
                    'RSI (14)',
                    'Volume',
                    'Price Predictions vs Actual'
                ),
                row_heights=[0.45, 0.15, 0.15, 0.25]
            )


            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name="Price",
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444'
                ),
                row=1, col=1
            )

            # Moving averages
            for period, name in [(5, 'MA 5'), (10, 'MA 10'), (20, 'MA 20'), (50, 'MA 50')]:
                colname = f"ma_{period}"
                if colname in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df['date'],
                            y=df[colname],
                            mode='lines',
                            name=name,
                            opacity=0.85,
                            connectgaps=False
                        ),
                        row=1, col=1
                    )

            # Bollinger Bands
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df['bb_upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(width=1, dash='dash'),
                        connectgaps=False
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=df['date'],
                        y=df['bb_lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(width=1, dash='dash'),
                        fill='tonexty',
                        connectgaps=False
                    ),
                    row=1, col=1
                )

            # RSI indicator
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['rsi'],
                    mode='lines',
                    name='RSI',
                    connectgaps=False
                ),
                row=2, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            # Volume bars
            colors_vol = ['red' if c < o else 'green' for c, o in zip(df['close'], df['open'])]
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors_vol,
                    opacity=0.6
                ),
                row=3, col=1
            )

            # Add predictions
            predictions = get_cached_predictions(ticker, 100)
            if predictions is not None and not predictions.empty:
                predictions['date'] = pd.to_datetime(predictions['date'], utc=True)
                fig.add_trace(
                    go.Scatter(
                        x=predictions['date'],
                        y=predictions['pred_close'],
                        mode='markers+lines',
                        name='Predictions',
                        line=dict(dash='dot'),
                        connectgaps=False
                    ),
                    row=4, col=1
                )

            # Layout
            fig.update_layout(
                template="plotly_dark",
                height=850,
                showlegend=True,
                title=f"{ticker} Advanced Technical Analysis"
            )

            fig.update_xaxes(title_text="Date", row=4, col=1)
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
            fig.update_yaxes(title_text="Volume", row=3, col=1)
            fig.update_yaxes(title_text="Predicted Price", row=4, col=1)

            return fig

        fig_candle = create_advanced_candlestick_chart(stock_data, selected_ticker)
        st.plotly_chart(fig_candle, width='stretch')



        # ====================================================================
        # PREDICTION ACCURACY CHART
        # ====================================================================
        
        def create_prediction_accuracy_chart(ticker):
            """
            Compare predictions vs actual prices during market hours
            """
            predictions = get_cached_predictions(ticker, 500)
            if predictions is None:
                predictions = pd.DataFrame(columns=["date", "pred_close", "confidence"])
            
            if "date" in predictions.columns and not predictions.empty:
                predictions['date'] = pd.to_datetime(predictions['date'], utc=True)
            else:
                predictions = predictions.copy()

            stock_df = get_cached_stock_data(ticker, 14)
            if stock_df is None or stock_df.empty:
                return go.Figure()
            
            stock_df['date'] = pd.to_datetime(stock_df['date'], utc=True)
            stock_df = stock_df.sort_values('date')
            
            if predictions is not None and not predictions.empty:
                predictions['date'] = pd.to_datetime(predictions['date'], utc=True)

            # Market timezone and hours
            if ticker in INDIAN_TICKERS:
                market_tz = pytz.timezone("Asia/Kolkata")
                start_hour, start_min = 9, 15
                end_hour, end_min = 15, 30
            else:
                market_tz = pytz.timezone("America/New_York")
                start_hour, start_min = 9, 30
                end_hour, end_min = 16, 0

            stock_df['local_dt'] = stock_df['date'].dt.tz_convert(market_tz)
            if predictions is not None and not predictions.empty:
                predictions['local_dt'] = predictions['date'].dt.tz_convert(market_tz)

            # Filter to market hours only
            def in_market_hours(s):
                m = s.dt.hour * 60 + s.dt.minute
                start_min_tot = start_hour * 60 + start_min
                end_min_tot = end_hour * 60 + end_min
                return (m >= start_min_tot) & (m <= end_min_tot)

            stock_mask = stock_df['local_dt'].notna() & in_market_hours(stock_df['local_dt'])
            stock_df = stock_df[stock_mask].copy()
            
            if stock_df.empty:
                return go.Figure()

            fig = go.Figure()
            
            # Plot actual prices by day
            stock_df['trade_date'] = stock_df['local_dt'].dt.normalize()
            for day, df_day in stock_df.groupby('trade_date'):
                df_day = df_day.sort_values('local_dt')
                fig.add_trace(
                    go.Scatter(
                        x=df_day['local_dt'], 
                        y=df_day['close'], 
                        mode='lines', 
                        name=f'Actual {day.date()}', 
                        showlegend=False
                    )
                )

            # Plot predictions by day
            if predictions is not None and not predictions.empty:
                pred_mask = predictions['local_dt'].notna() & in_market_hours(predictions['local_dt'])
                predictions = predictions[pred_mask].copy()
                
                if not predictions.empty:
                    predictions['trade_date'] = predictions['local_dt'].dt.normalize()
                    for day, p_df in predictions.groupby('trade_date'):
                        p_df = p_df.sort_values('local_dt')
                        fig.add_trace(
                            go.Scatter(
                                x=p_df['local_dt'], 
                                y=p_df['pred_close'], 
                                mode='markers+lines', 
                                name=f'Predictions {day.date()}', 
                                showlegend=False, 
                                line=dict(dash='dot')
                            )
                        )

            fig.update_layout(
                template="plotly_dark", 
                height=420, 
                title=f"{ticker} Prediction Accuracy (market hours)"
            )
            fig.update_xaxes(title_text="Local Time")
            fig.update_yaxes(title_text="Price")
            
            return fig

        fig_acc = create_prediction_accuracy_chart(selected_ticker)
        st.plotly_chart(fig_acc, width='stretch')



# ============================================================================
# PREDICTIONS SIDEBAR
# ============================================================================

with col_side:
    st.subheader("🔮 Predictions")
    
    # Show market status for selected ticker
    ticker_market_open = is_market_open(selected_ticker)
    if ticker_market_open:
        st.success("🟢 Live Predictions")
    else:
        st.info("🔴 Previous Predictions (Market Closed)")

    predictions = get_cached_predictions(selected_ticker, 10)
    
    if predictions is None or predictions.empty:
        st.info("No predictions available.")
        if not ticker_market_open:
            st.caption("Predictions generated during market hours only")
    else:
        # Get most recent prediction
        predictions['date'] = pd.to_datetime(predictions['date'], utc=True)
        predictions = predictions.sort_values('date', ascending=False).reset_index(drop=True)
        latest_pred = predictions.iloc[0]
        
        # Show latest prediction with market status context
        st.metric(
            "Latest Price Prediction",
            f"${latest_pred['pred_close']:.2f}",
            delta=None
        )
        
        # Confidence with color coding
        confidence = latest_pred['confidence']
        conf_emoji = "🟢" if confidence > 75 else "🟡" if confidence > 50 else "🔴"
        st.metric("Confidence", f"{conf_emoji} {confidence:.1f}%")
        
        pred_time = latest_pred['date']
        st.caption(f"Generated: {pred_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not ticker_market_open:
            st.caption("⏰ Next update when market opens")

        currency = "₹" if selected_ticker in INDIAN_TICKERS else "$"
        pred_close = float(latest_pred['pred_close'])
        confidence = float(latest_pred.get('confidence', 0.5))

        # Display prediction metrics
        st.metric(label="Next Period Prediction", value=f"{currency}{pred_close:,.2f}")
        st.metric(label="Confidence", value=f"{confidence:.1%}")

        # Recent predictions table
        display_df = predictions[['date', 'pred_close', 'confidence']].copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%m-%d %H:%M')
        display_df['pred_close'] = display_df['pred_close'].round(2)
        display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
        display_df.columns = ['Time', 'Prediction', 'Confidence']
        
        st.dataframe(display_df, width='stretch', hide_index=True)

# ============================================================================
# MODEL PERFORMANCE SECTION
# ============================================================================

st.markdown("---")
st.subheader("📊 Model Performance")
perf_col1, perf_col2 = st.columns(2)

with perf_col1:
    # Model performance chart (placeholder with sample data)
    stocks = TICKERS[:5]
    mae_scores = np.random.uniform(0.5, 3.0, len(stocks))
    rmse_scores = np.random.uniform(1.0, 5.0, len(stocks))
    
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Bar(x=stocks, y=mae_scores, name='MAE'))
    fig_perf.add_trace(go.Bar(x=stocks, y=rmse_scores, name='RMSE'))
    fig_perf.update_layout(template="plotly_dark", title="Model Performance Across Stocks")
    
    st.plotly_chart(fig_perf, width='stretch')

with perf_col2:
    st.subheader("🎯 Prediction Features")
    st.markdown(
        """
- **Price lags**: Last 10 periods
- **Moving averages**: 5, 10, 20, 50 periods
- **RSI**: Relative Strength Index
- **Bollinger Bands**: Volatility indicator
- **Volume trends**: Trading volume patterns
- **Models**: Linear Regression, Random Forest
- **Selection**: Best model by MAE
"""
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888;'>🔄 Data updates every minute | Built with Streamlit, yfinance, scikit-learn</div>",
    unsafe_allow_html=True,
)

# ============================================================================
# AUTO-REFRESH MECHANISM
# ============================================================================

if 'auto_refresh' in locals() and auto_refresh:
    time.sleep(30)
    st.rerun()
