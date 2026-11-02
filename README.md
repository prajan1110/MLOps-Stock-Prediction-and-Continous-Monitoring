# Stock Prediction and MLOps

A stock-market dashboard and end-to-end MLOps project for collecting OHLCV data, creating time-aware features, training and comparing regression models, serving predictions, and monitoring feature drift.

> **Disclaimer:** This project is for educational and demonstration purposes only. It is not investment advice. Market data is obtained from Yahoo Finance through `yfinance`; availability, delays, and coverage are not guaranteed.

## Contents

- [Project overview](#project-overview)
- [Architecture and pipelines](#architecture-and-pipelines)
- [Supported tickers and features](#supported-tickers-and-features)
- [Requirements](#requirements)
- [Quick start on Windows](#quick-start-on-windows)
- [Run with Docker Compose](#run-with-docker-compose)
- [Run the training pipeline](#run-the-training-pipeline)
- [Run the inference API](#run-the-inference-api)
- [Monitoring and automation](#monitoring-and-automation)
- [Configuration and secrets](#configuration-and-secrets)
- [Supabase setup](#supabase-setup)
- [Tests and validation](#tests-and-validation)
- [Project layout](#project-layout)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Limitations and security notes](#limitations-and-security-notes)

## Project overview

The repository contains two related application paths:

1. **Interactive stock dashboard:** `frontend.py` uses Streamlit and Plotly to show stock data, charts, market status, predictions, and model performance. Its legacy backend (`backend_data.py`, `backend_model.py`, and `backend_main.py`) fetches data during market hours and stores it in Supabase.
2. **Reproducible MLOps path:** DVC manages daily data collection, preprocessing, and model training. The training code uses MLflow for experiment tracking, packages model artifacts for each ticker, and can be served through FastAPI. A monitoring process checks feature drift and conditionally retrains the models.

The dashboard's market-hours collector and the DVC-based daily pipeline are separate workflows. The dashboard does not call the FastAPI service, and training through DVC does not write into the dashboard's Supabase tables.

## Architecture and pipelines

### DVC training pipeline

The pipeline in [`dvc.yaml`](dvc.yaml) contains three stages:

| Stage | What it does | Main outputs |
|---|---|---|
| `collect` | Downloads two years of daily OHLCV data for the configured tickers from Yahoo Finance. | `data/raw/stock_data.csv` |
| `prepare` | Validates and normalizes OHLCV data for training. | `data/processed/training.csv` |
| `train` | Builds features, compares models, logs runs to MLflow, and writes selected model artifacts and summary metrics. | `models/*.joblib`, `metrics/summary.json` |

Inspect or execute the pipeline with `dvc dag` and `dvc repro`. DVC tracks stage dependencies and outputs; the local cache is not a shared remote by default.

### Model training and evaluation

For each ticker, training creates lagged closing-price features, moving averages, RSI, Bollinger Bands, and a moving average of volume. The target is the next observed closing price. Rows are sorted chronologically and split into train, validation, and test partitions (70%, 15%, 15%). Linear Regression and Random Forest candidates are compared by validation MAE. The selected candidate is refit on train plus validation data and evaluated once on the held-out test period.

MLflow records the experiment `stock-price-prediction`, parameters, metrics, selected model, dataset SHA-256, feature schema, and model artifact. Local tracking data is stored under `mlruns/` by default.

### Monitoring and retraining

The monitoring workflow refreshes and prepares data, compares current feature distributions with the last successful reference snapshot using Population Stability Index (PSI), and retrains when PSI reaches the configured threshold. The default threshold is `0.2`. A first run also trains when the reference snapshot or expected model artifacts are missing.

The latest report is written to `metrics/drift_latest.json`. The reference snapshot is `data/reference_features.csv` and is updated only after training produces all expected ticker artifacts. Drift is a review signal; it is not a guarantee that a model is inaccurate or profitable.

### Services

- **Streamlit dashboard:** `http://localhost:8501`
- **FastAPI inference:** `http://localhost:8000`
- **Interactive API docs:** `http://localhost:8000/docs`
- **MLflow UI (optional):** `http://127.0.0.1:5000`

## Supported tickers and features

The MLOps pipeline uses the ticker list in [`src/config.py`](src/config.py):

- United States: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`
- India: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, `INFY.NS`, `HINDUNILVR.NS`

The engineered features include closing-price lags 1–10, 5/10/20/50-period closing-price averages, 14-period RSI, 20-period Bollinger Band values, and 20-period volume average. The model predicts the next available observation, not a guaranteed real-time market price.

## Requirements

- Python 3.12 is the tested container runtime and recommended local version.
- Git is needed for DVC repository operations.
- Docker Desktop with the Compose plugin is needed for the containerized stack.
- Internet access is needed to download Yahoo Finance data and install dependencies.
- A Supabase project is needed for the dashboard's cloud-backed storage.

## Quick start on Windows

Open PowerShell in the repository directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual environment activation, either allow activation for the current terminal with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or run the environment's Python directly as `.\.venv\Scripts\python.exe`.

### Configure Supabase

Create a Supabase project, copy [`.env.example`](.env.example) to `.env`, and set the project URL and publishable/anon key:

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally. Never commit it or put a Supabase secret/service-role key in the dashboard. Run [`supabase_tables.sql`](supabase_tables.sql) in the Supabase SQL Editor to create the tables.

### Start the dashboard and its backend

```powershell
python run.py
```

Then open `http://localhost:8501`. The entry point starts the background data collector and model worker and launches Streamlit. The dashboard refreshes automatically. It requires valid Supabase credentials and the tables described above.

To start only the dashboard process:

```powershell
python -m streamlit run frontend.py
```

The dashboard initializes its collector and model worker when it starts.

## Run with Docker Compose

The local Compose stack includes the dashboard, inference API, and daily MLOps automation service.

First, make model artifacts available for the API image and local mount. For an initial local setup, follow [Run the training pipeline](#run-the-training-pipeline) before building the API. Configure `.env` as described above; Compose passes it to the dashboard.

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open:

- Dashboard: `http://localhost:8501`
- API health: `http://localhost:8000/health`
- API model information: `http://localhost:8000/model-info`
- Interactive API docs: `http://localhost:8000/docs`

Stop the stack with `Ctrl+C`, or use `docker compose down` from another terminal. Add `-d` to run in the background; inspect output with `docker compose logs -f` and stop it with `docker compose down`.

The scheduler runs immediately after startup, then repeats every 24 hours. Local Compose persists data, DVC cache, models, metrics, and MLflow runs through bind mounts. Keep these files backed up if you need to preserve local experiments or model state.

The separate [`compose.production.yaml`](compose.production.yaml) references prebuilt images in GitHub Container Registry and uses named volumes. Use it only after those images have been published and the host has been configured to pull them. The repository does not include an active GitHub Actions workflow to build or publish these images.

## Run the training pipeline

From the activated virtual environment at the repository root:

```powershell
dvc dag
dvc repro
```

The collection stage needs internet access. Expected outputs include:

- `data/raw/stock_data.csv`
- `data/processed/training.csv`
- `models/<TICKER>.joblib` (Indian ticker periods are replaced with underscores)
- `metrics/summary.json`
- MLflow run data under `mlruns/`

You can run one stage or invoke the modules directly:

```powershell
dvc repro collect
dvc repro prepare
dvc repro train

python -m src.data_collection --output data/raw/stock_data.csv --period 2y --interval 1d
python -m src.preprocessing --input data/raw/stock_data.csv --output data/processed/training.csv
python -m src.train --input data/processed/training.csv --models-dir models --metrics-output metrics/summary.json
```

DVC uses a local cache unless a remote is configured. To share data and artifacts between machines, configure a DVC remote (for example, S3) and store credentials outside Git:

```powershell
dvc remote add -d storage s3://your-bucket/stock-prediction
```

On another machine, configure the same remote and credentials, then use `dvc pull` to retrieve tracked outputs.

## Run the inference API

The API reads `*.joblib` artifacts from `models/`. Train models or retrieve them with DVC before starting the service:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Service status and count of available model artifacts. |
| `GET` | `/model-info` | Metadata for available models; optionally filter with `?ticker=AAPL`. |
| `POST` | `/predict` | Predict the next observation for a supported ticker. |
| `GET` | `/docs` | Interactive OpenAPI documentation. |

Example request (the values below are illustrative; for useful predictions, supply current values for all features returned by `/model-info`):

```powershell
$features = @{
  close_lag_1 = 190.0; close_lag_2 = 189.0; close_lag_3 = 188.0
  close_lag_4 = 187.0; close_lag_5 = 186.0; close_lag_6 = 185.0
  close_lag_7 = 184.0; close_lag_8 = 183.0; close_lag_9 = 182.0
  close_lag_10 = 181.0
  close_ma_5 = 188.0; close_ma_10 = 185.0; close_ma_20 = 180.0
  close_ma_50 = 175.0
  rsi_14 = 55.0
  bb_middle_20 = 180.0; bb_upper_20 = 195.0; bb_lower_20 = 165.0
  volume_ma_20 = 1000000.0
}
$body = @{ ticker = "AAPL"; features = $features } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType "application/json" -Body $body
```

Use `/model-info?ticker=AAPL` to confirm the required feature names. Requests for unsupported tickers are rejected; a missing model artifact results in HTTP 404. Request IDs and latency are recorded in the service logs and returned in the `X-Request-ID` response header.

## Monitoring and automation

### Run a one-time automated cycle

```powershell
python -m monitoring.automation --once
```

This refreshes data and prepares it through DVC, compares per-ticker features against the previous reference snapshot, and runs the train stage if drift is detected or a bootstrap is required.

### Run the scheduler

```powershell
python -m monitoring.automation --interval-hours 24 --threshold 0.2
```

The scheduler runs a cycle immediately and repeats at the requested interval. Check `metrics/drift_latest.json` for the latest PSI report.

### Compare feature snapshots manually

```powershell
python -m monitoring.drift_detection --reference path\to\reference_features.csv --current path\to\current_features.csv --threshold 0.2
```

PSI is calculated only for shared numeric columns. A threshold breach identifies a distribution change; it does not itself assess prediction quality. Performance monitoring requires matching predictions with later observed prices and evaluating metrics such as rolling MAE/RMSE.

### View MLflow experiments

In another terminal:

```powershell
mlflow ui --backend-store-uri mlruns --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000`. The default tracking store is local and is not shared or backed up automatically. Set `MLFLOW_TRACKING_URI` to a durable tracking server when using a shared environment.

## Configuration and secrets

[`.env.example`](.env.example) documents the supported local environment variables:

| Variable | Use |
|---|---|
| `SUPABASE_URL` | Supabase project URL for the dashboard backend. |
| `SUPABASE_KEY` | Supabase publishable/anon key for the dashboard backend. |
| `MLFLOW_TRACKING_URI` | Optional MLflow tracking URI; training defaults to local `mlruns/`. |
| `MODEL_DIR` | Optional API model directory; defaults to `models`. |
| `LOG_LEVEL` | Documented logging setting; service logging currently uses its configured defaults. |

`.env` is ignored by Git. Streamlit Community Cloud uses the app's Settings → Secrets in TOML format instead:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-publishable-or-anon-key"
```

Do not paste real credentials into issues, logs, screenshots, or source files.

## Supabase setup

The dashboard backend uses three tables defined in [`supabase_tables.sql`](supabase_tables.sql):

- `ohlcv`: collected prices and volumes.
- `model_predictions`: predictions and confidence values.
- `model_performance`: model evaluation data.

Run the SQL in Supabase's SQL Editor, then confirm the tables exist in Table Editor. The SQL currently creates permissive Row Level Security policies for all operations. These policies are unsafe for a publicly exposed database; replace them with least-privilege policies before public or production use.

## Tests and validation

Run the test suite and compile-check the Python packages:

```powershell
python -m pytest -q
python -m compileall -q api src monitoring dashboard
```

For Docker Compose configuration validation:

```powershell
docker compose config --quiet
```

Tests use synthetic data and mocked model artifacts; they do not depend on Yahoo Finance or a live Supabase project.

## Project layout

```text
.
├── api/                      FastAPI model-inference service
├── assets/                   Dashboard assets
├── dashboard/                Streamlit wrapper entry point
├── data/                     DVC-managed raw, processed, and reference data
├── metrics/                  Training summary and drift reports
├── mlruns/                   Local MLflow tracking store (runtime data)
├── models/                   Per-ticker serialized model artifacts
├── monitoring/               PSI checks, logging, and scheduled automation
├── src/
│   ├── config.py             Supported ticker configuration
│   ├── data_collection.py    Yahoo Finance collection
│   ├── preprocessing.py      OHLCV validation and preparation
│   ├── features.py           Time-aware feature engineering
│   ├── train.py              Model training, evaluation, and MLflow logging
│   └── predict.py            Model artifact loading and prediction
├── tests/                    Automated tests
├── backend_data.py            Supabase-backed dashboard data collection
├── backend_main.py            Dashboard backend worker coordination
├── backend_model.py           Dashboard model training and predictions
├── frontend.py                Main Streamlit stock dashboard
├── run.py                     Starts dashboard and its backend workers
├── dvc.yaml                   Reproducible collection/prepare/train pipeline
├── compose.yaml               Local multi-service stack
├── compose.production.yaml    Published-image deployment configuration
├── supabase_tables.sql        Dashboard database schema and policies
├── requirements*.txt          Runtime and MLOps dependencies
├── DEPLOYMENT.md              Streamlit and Compose deployment notes
└── MLOPS_GUIDE.md             MLOps operational runbook
```

Generated data, models, local MLflow runs, DVC cache, and `.env` should not be committed unless intentionally versioned for a specific deployment workflow.

## Deployment

### Streamlit Community Cloud

Use the GitHub repository, select the branch to deploy, set the app entry point to `frontend.py`, and add `SUPABASE_URL` and `SUPABASE_KEY` under app secrets. Ensure the Supabase tables exist and tighten the SQL policies before exposing the app. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the deployment checklist.

### Docker host

For a host running local builds, use `docker compose up --build -d`. The production Compose file instead expects published GHCR images, a configured `.env`, and persistent named volumes. Plan backups for the data, model, metrics, DVC cache, and MLflow volumes. The project does not currently configure a cloud deployment target or image-publishing workflow.

## Troubleshooting

### `ModuleNotFoundError`

Activate the intended virtual environment and reinstall the pinned dependencies:

```powershell
python -m pip install -r requirements.txt
```

The Streamlit refresh component is included in the root requirements and `requirements-dashboard-ui.txt`.

### Dashboard cannot connect to Supabase

- Confirm `.env` exists at the repository root and contains the correct URL and publishable/anon key.
- Verify the Supabase project is active and that `supabase_tables.sql` has been run.
- Restart Streamlit after changing environment variables.

### No prediction models or API returns 404

- Run `dvc repro` and confirm artifacts exist in `models/`, or configure a DVC remote and run `dvc pull`.
- The API loads the model directory at startup/request time; confirm `MODEL_DIR` points to the artifacts.
- For Docker, verify the host `models/` folder contains the model files mounted into the container.

### DVC data collection fails

- Confirm internet access and try again later if Yahoo Finance is unavailable or rate-limiting requests.
- Run from the repository root with the project's Python environment activated.
- Check DVC output for the failing stage and verify available disk space.

### Docker dashboard or API is unavailable

- Confirm Docker Desktop is running and `docker compose up --build` completed successfully.
- Review logs with `docker compose logs -f`.
- Check that ports 8501 and 8000 are not already in use.
- Verify `.env` is present for the dashboard and model artifacts are available for inference.

## Limitations and security notes

- Yahoo Finance data is not an exchange-grade real-time feed. Intraday coverage and availability vary.
- The target is the next available observation's closing price. Model metrics do not imply future returns or trading performance.
- The legacy dashboard's market-hours checks use weekdays and clock times; they do not include an exchange holiday calendar.
- PSI measures feature-distribution changes, not model accuracy. The automation does not automatically deploy a new model to a remote production target.
- The default DVC and MLflow stores are local. Configure remote storage and backups for team or production use.
- The current Supabase SQL policies allow broad access. Review and restrict Row Level Security before using real or public data.
- Store credentials in local environment/secrets management only. Never commit `.env`, service-role keys, or cloud credentials.

## License

No license file is currently included. Contact the repository owner before redistributing or reusing the project beyond applicable repository terms.
