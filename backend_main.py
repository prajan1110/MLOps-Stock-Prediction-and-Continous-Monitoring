"""
BACKEND - MAIN COORDINATOR
Starts data collection and model training in background
"""

import logging
import time
import threading

from backend_data import (
    start_data_collection,
    stop_data_collection,
    is_market_open,
    get_market_status
)

from backend_model import train_and_predict_all_stocks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# BACKGROUND TRAINING WORKER
# ============================================================================

model_training_active = False
model_thread = None
model_lock = threading.Lock()

def _train_models_continuously():
    """
    Background worker that trains models continuously
    - Only trains when markets are open
    - Trains every 5 minutes when open
    - Checks every 10 minutes when closed
    """
    global model_training_active
    
    logger.info("🤖 Model training worker started")
    
    # Wait 30 seconds before first training
    time.sleep(30)
    
    while model_training_active:
        try:
            # Check market status
            market_status = get_market_status()
            
            if market_status['any_market_open']:
                # Markets are OPEN - Train models
                logger.info("\n" + "=" * 80)
                logger.info("🎯 MARKETS OPEN - Starting Training Cycle")
                logger.info(f"   US Market: {'OPEN' if market_status['us_market_open'] else 'CLOSED'}")
                logger.info(f"   Indian Market: {'OPEN' if market_status['indian_market_open'] else 'CLOSED'}")
                logger.info(f"   US Time: {market_status['us_time']}")
                logger.info(f"   India Time: {market_status['indian_time']}")
                logger.info("=" * 80)
                
                # Train all models
                train_and_predict_all_stocks()
                
                logger.info("\n✅ Training complete. Next training in 5 minutes...")
                time.sleep(300)  # Wait 5 minutes
                
            else:
                # Markets are CLOSED - Just wait
                logger.info("💤 Markets closed. Showing previous predictions.")
                logger.info(f"   US Time: {market_status['us_time']}")
                logger.info(f"   India Time: {market_status['indian_time']}")
                logger.info("   Next check in 10 minutes...")
                time.sleep(600)  # Wait 10 minutes
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            time.sleep(60)  # Wait 1 minute on error


def start_model_training():
    """Start background model training"""
    global model_training_active, model_thread
    
    with model_lock:
        if model_training_active:
            logger.info("⚠️  Model training already running")
            return
        
        model_training_active = True
        model_thread = threading.Thread(target=_train_models_continuously, daemon=True)
        model_thread.start()
        logger.info("✅ Model training started")


def stop_model_training():
    """Stop background model training"""
    global model_training_active
    
    with model_lock:
        if not model_training_active:
            return
        
        model_training_active = False
        logger.info("🛑 Model training stopped")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def start_backend():
    """Start all backend services"""
    logger.info("\n" + "=" * 80)
    logger.info("🚀 STARTING BACKEND SERVICES")
    logger.info("=" * 80)
    
    # Start data collection
    start_data_collection()
    
    # Start model training
    start_model_training()
    
    logger.info("✅ All backend services started")
    logger.info("=" * 80 + "\n")


def stop_backend():
    """Stop all backend services"""
    logger.info("🛑 Stopping backend services...")
    stop_data_collection()
    stop_model_training()
    logger.info("✅ Backend stopped")


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'start_backend',
    'stop_backend',
    'start_model_training',
    'stop_model_training'
]
