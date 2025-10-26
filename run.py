"""
RUN - Single Entry Point
Starts both backend and frontend with one command

Usage: python run.py
"""

import subprocess
import sys
import time
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# START BACKEND
# ============================================================================

def start_backend():
    """Start backend (data collection + model training)"""
    try:
        logger.info("🚀 Starting backend...")
        from backend_main import start_backend as run_backend
        run_backend()
        logger.info("✅ Backend started!")
    except Exception as e:
        logger.error(f"❌ Backend error: {e}")
        logger.info("💡 Make sure:")
        logger.info("   1. .env file exists with Supabase credentials")
        logger.info("   2. Tables created in Supabase SQL Editor")

# ============================================================================
# START FRONTEND
# ============================================================================

def start_frontend():
    """Start frontend (Streamlit dashboard)"""
    try:
        logger.info("\n🖥️  Starting dashboard...")
        logger.info("   URL: http://localhost:8501")
        logger.info("\n💡 Press Ctrl+C to stop\n")
        
        time.sleep(2)  # Wait for backend to initialize
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend.py",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Frontend error: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    print("=" * 80)
    print("📈 STOCK PREDICTION SYSTEM")
    print("=" * 80)
    print("\nStarting:")
    print("   ✓ Backend: Data + Models")
    print("   ✓ Frontend: Dashboard\n")
    
    # Start backend in background
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait for initialization
    time.sleep(3)
    
    # Start frontend (blocking)
    start_frontend()

if __name__ == "__main__":
    main()
