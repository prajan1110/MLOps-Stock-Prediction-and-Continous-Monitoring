"""
BACKEND - ML MODEL TRAINER
Trains machine learning models and makes price predictions
"""

import logging
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend_data import (
    ALL_STOCKS,
    get_stock_data,
    create_ml_features,
    save_prediction,
    save_model_performance
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SETTINGS
# ============================================================================

MIN_DATA_POINTS = 50  # Need at least 50 data points to train
TRAIN_SPLIT_RATIO = 0.8  # 80% for training, 20% for validation

# ============================================================================
# STEP 1: PREPARE DATA
# ============================================================================

def prepare_training_data(df: pd.DataFrame):
    """
    Split data into training and validation sets
    Returns: X_train, y_train, X_val, y_val, feature_columns
    """
    if df.empty or len(df) < MIN_DATA_POINTS:
        return None, None, None, None, None
    
    # Sort by date
    df = df.copy().sort_values('date')
    
    # Create target: next period's closing price
    df['target'] = df['close'].shift(-1)
    df = df.dropna()
    
    if len(df) < MIN_DATA_POINTS:
        return None, None, None, None, None
    
    # Get feature columns (exclude non-features)
    exclude_cols = ['date', 'symbol', 'target', 'id', 'open', 'high', 'low', 'volume']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    if not feature_cols:
        return None, None, None, None, None
    
    # Split: 80% train, 20% validation
    split_index = int(len(df) * TRAIN_SPLIT_RATIO)
    train_data = df.iloc[:split_index]
    val_data = df.iloc[split_index:]
    
    # Create X (features) and y (target)
    X_train = train_data[feature_cols].values
    y_train = train_data['target'].values
    X_val = val_data[feature_cols].values
    y_val = val_data['target'].values
    
    return X_train, y_train, X_val, y_val, feature_cols


# ============================================================================
# STEP 2: TRAIN MODELS
# ============================================================================

def train_two_models(X_train, y_train):
    """Train both Linear Regression and Random Forest models"""
    
    # Model 1: Linear Regression (simple and fast)
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    
    # Model 2: Random Forest (more complex, better accuracy)
    forest_model = RandomForestRegressor(
        n_estimators=100,  # Use 100 trees
        random_state=42,
        n_jobs=1
    )
    forest_model.fit(X_train, y_train)
    
    return linear_model, forest_model


# ============================================================================
# STEP 3: SELECT BEST MODEL
# ============================================================================

def select_best_model(linear_model, forest_model, X_val, y_val):
    """Evaluate both models and return the best one"""
    
    # Test Linear Regression
    linear_predictions = linear_model.predict(X_val)
    linear_mae = mean_absolute_error(y_val, linear_predictions)
    linear_mse = mean_squared_error(y_val, linear_predictions)
    linear_r2 = r2_score(y_val, linear_predictions)
    
    # Test Random Forest
    forest_predictions = forest_model.predict(X_val)
    forest_mae = mean_absolute_error(y_val, forest_predictions)
    forest_mse = mean_squared_error(y_val, forest_predictions)
    forest_r2 = r2_score(y_val, forest_predictions)
    
    logger.info(f"   Linear Regression - Error: ${linear_mae:.2f}, Accuracy: {linear_r2:.2%}")
    logger.info(f"   Random Forest - Error: ${forest_mae:.2f}, Accuracy: {forest_r2:.2%}")
    
    # Choose model with lower error (MAE = Mean Absolute Error)
    if linear_mae <= forest_mae:
        logger.info(f"   ✅ Selected: Linear Regression")
        return linear_model, "LinearRegression", {
            'mae': linear_mae,
            'mse': linear_mse,
            'r2': linear_r2
        }
    else:
        logger.info(f"   ✅ Selected: Random Forest")
        return forest_model, "RandomForest", {
            'mae': forest_mae,
            'mse': forest_mse,
            'r2': forest_r2
        }


# ============================================================================
# STEP 4: CALCULATE CONFIDENCE
# ============================================================================

def calculate_confidence_score(metrics: dict, recent_volatility: float) -> float:
    """Calculate how confident we are in the prediction (0-100%)"""
    
    # Base confidence from R² score (model accuracy)
    r2 = metrics.get('r2', 0)
    base_confidence = max(0, min(100, r2 * 100))
    
    # Reduce confidence if error is high
    mae = metrics.get('mae', 1.0)
    if mae > 0:
        error_penalty = min(20, mae * 5)
    else:
        error_penalty = 0
    
    # Reduce confidence if price is very volatile
    volatility_penalty = min(15, recent_volatility * 10)
    
    # Final confidence score
    confidence = max(0, min(100, base_confidence - error_penalty - volatility_penalty))
    
    return confidence


# ============================================================================
# MAIN: TRAIN AND PREDICT
# ============================================================================

def train_and_predict_one_stock(ticker: str):
    """Train model and make prediction for one stock"""
    try:
        logger.info(f"🎯 Training model for {ticker}...")
        
        # Step 1: Get stock data from database
        df = get_stock_data(ticker, limit=1000)
        if df.empty:
            logger.warning(f"   No data available for {ticker}")
            return None
        
        # Step 2: Create ML features
        df_features = create_ml_features(df)
        if df_features.empty or len(df_features) < MIN_DATA_POINTS:
            logger.warning(f"   Not enough data for {ticker}")
            return None
        
        # Step 3: Prepare training data
        X_train, y_train, X_val, y_val, feature_cols = prepare_training_data(df_features)
        if X_train is None:
            logger.warning(f"   Data preparation failed for {ticker}")
            return None
        
        # Step 4: Train both models
        linear_model, forest_model = train_two_models(X_train, y_train)
        
        # Step 5: Select best model
        best_model, model_name, metrics = select_best_model(linear_model, forest_model, X_val, y_val)
        
        # Step 6: Save model performance to database
        save_model_performance(ticker, model_name, metrics['mae'], metrics['mse'], metrics['r2'])
        
        # Step 7: Make prediction for next period
        latest_features = df_features[feature_cols].iloc[-1:].values
        predicted_price = best_model.predict(latest_features)[0]
        
        # Step 8: Calculate confidence score
        recent_prices = df_features['close'].tail(20)
        price_volatility = recent_prices.std() / recent_prices.mean()
        confidence = calculate_confidence_score(metrics, price_volatility)
        
        # Step 9: Save prediction to database
        save_prediction(ticker, float(predicted_price), float(confidence))
        
        logger.info(f"   💰 Predicted Price: ${predicted_price:.2f} (Confidence: {confidence:.0f}%)")
        
        return {
            'ticker': ticker,
            'predicted_price': predicted_price,
            'confidence': confidence,
            'model_type': model_name,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"   ❌ Error processing {ticker}: {e}")
        return None


def train_and_predict_all_stocks():
    """Train models and make predictions for all stocks"""
    logger.info("=" * 80)
    logger.info("🚀 TRAINING MODELS FOR ALL STOCKS")
    logger.info("=" * 80)
    
    results = []
    for ticker in ALL_STOCKS:
        result = train_and_predict_one_stock(ticker)
        if result:
            results.append(result)
    
    logger.info(f"\n✅ Successfully trained {len(results)}/{len(ALL_STOCKS)} stocks")
    return results


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'train_and_predict_one_stock',
    'train_and_predict_all_stocks'
]
