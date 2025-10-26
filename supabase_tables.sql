-- ============================================================================
-- SUPABASE DATABASE SETUP SQL
-- ============================================================================
-- Copy this entire SQL script and run it in:
-- Supabase Dashboard → SQL Editor → New Query → Paste → RUN
-- ============================================================================

-- Table 1: Stock OHLCV Data
CREATE TABLE IF NOT EXISTS ohlcv (
    id BIGSERIAL PRIMARY KEY,
    date TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume BIGINT,
    UNIQUE(date, symbol)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_date ON ohlcv(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_date ON ohlcv(date DESC);

-- Table 2: Model Predictions
CREATE TABLE IF NOT EXISTS model_predictions (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    pred_close REAL,
    confidence REAL,
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_symbol_date ON model_predictions(symbol, date DESC);

-- Table 3: Model Performance Metrics
CREATE TABLE IF NOT EXISTS model_performance (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT,
    model_type TEXT,
    mae REAL,
    mse REAL,
    r2 REAL,
    trained_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_performance_symbol ON model_performance(symbol, trained_at DESC);

-- Enable Row Level Security
ALTER TABLE ohlcv ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_performance ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'ohlcv' AND policyname = 'Enable all operations for ohlcv'
    ) THEN
        CREATE POLICY "Enable all operations for ohlcv" ON ohlcv FOR ALL USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'model_predictions' AND policyname = 'Enable all operations for predictions'
    ) THEN
        CREATE POLICY "Enable all operations for predictions" ON model_predictions FOR ALL USING (true);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'model_performance' AND policyname = 'Enable all operations for performance'
    ) THEN
        CREATE POLICY "Enable all operations for performance" ON model_performance FOR ALL USING (true);
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- After running this, verify by going to Table Editor
-- You should see 3 tables: ohlcv, model_predictions, model_performance
-- ============================================================================
