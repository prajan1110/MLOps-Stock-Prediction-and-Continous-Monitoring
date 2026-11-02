# MLOps Runbook

This runbook is the current setup guide for the existing Streamlit/Supabase stock app and its MLOps extension. Predictions are for education, not financial advice. Yahoo Finance data is periodic and is not guaranteed exchange-grade real-time data.

## 1. Reproducible Environment

Use Python 3.12 from the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-mlops.txt
```

Copy `.env.example` to `.env`, then set the Supabase project URL and publishable/anon key. Never commit `.env` or use a secret/service-role key in the dashboard. Run `supabase_tables.sql` in the Supabase SQL Editor and verify `ohlcv`, `model_predictions`, and `model_performance` exist.

Start the existing app:

```powershell
python run.py
```

Dashboard: `http://localhost:8501`. It collects intraday data and updates the existing Supabase-backed dashboard. The `dashboard/streamlit_app.py` wrapper also supports `streamlit run dashboard/streamlit_app.py`.

## 2. Dataset and DVC

The new training dataset uses daily OHLCV rows, UTC timestamps, and a next-observation closing-price target. Validation checks required columns, types, positive prices, OHLC consistency, nonnegative volume, and duplicate ticker/timestamp pairs. Technical features use only the current and prior observations. Training partitions are chronological; validation MAE selects between Linear Regression and Random Forest, while the final test partition is held out from model selection.

Inspect the three-stage collection, prepare, train pipeline:

```powershell
dvc dag
```

Run the pipeline (the collection stage needs internet access to Yahoo Finance):

```powershell
dvc repro
```

Outputs are DVC-managed under `data/raw/`, `data/processed/`, and `models/`; metrics are written to `metrics/summary.json`. DVC cache is local until a remote is configured. Example remote setup:

```powershell
dvc remote add -d storage s3://your-bucket/stock-prediction
```

Set remote credentials outside Git. To reproduce on another machine, configure the same remote and run `dvc pull` before using the data/model outputs.

Equivalent individual commands:

```powershell
python -m src.data_collection --output data/raw/stock_data.csv --period 2y --interval 1d
python -m src.preprocessing --input data/raw/stock_data.csv --output data/processed/training.csv
python -m src.train --input data/processed/training.csv --models-dir models --metrics-output metrics/summary.json
```

## 3. MLflow

Training logs parameters, ticker, target definition, data SHA-256, validation/test metrics, model artifacts, and the selected model version to the local `mlruns/` store. Start the UI in a second terminal:

```powershell
mlflow ui --backend-store-uri mlruns --host 127.0.0.1 --port 5000
```

Open `http://localhost:5000`. The local store is ignored by Git; configure a durable tracking and artifact store for team/cloud use.

## 4. FastAPI Inference

Run `dvc repro` first so selected model artifacts exist in `models/`, then start:

```powershell
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

- `GET /health`: service status and available model count.
- `GET /model-info`: model version, dataset hash, metrics, and feature names. Optional filter: `/model-info?ticker=AAPL`.
- `POST /predict`: validated ticker and feature-value mapping; response includes prediction, model version, and timestamp.
- `GET /docs`: interactive API docs.

Use the feature names returned from `/model-info` in the prediction request. The API logs a request ID, response status, and latency. It does not automatically retrain.

## 5. Monitoring

The drift command compares matching numeric columns with Population Stability Index (PSI); a PSI >= 0.2 is a review alert, not an automatic retraining trigger:

```powershell
python -m monitoring.drift_detection --reference path\to\reference_features.csv --current path\to\current_features.csv --threshold 0.2
```

Feature drift can be measured without labels. Performance drift requires joining saved predictions with later actual prices and tracking rolling MAE/RMSE. Retrain only when there is sufficient labelled data and the candidate passes the same time-aware evaluation protocol.

The Compose automation service now runs a daily cycle automatically: refresh data and prepare it through DVC, compare per-ticker features against the last successful training snapshot, and run the DVC train stage when drift reaches the threshold (or on first startup when the reference/models are missing). It saves the latest PSI report to `metrics/drift_latest.json` and updates the reference only after all expected model artifacts are present. Start it with `docker compose up -d --build`; keep Docker running for scheduled cycles. To run one cycle immediately from the host, use `python -m monitoring.automation --once`. The local reference, DVC cache, data, models, metrics, and MLflow store must persist; back them up for recovery. This automation does not provide a remote/cloud deployment target.

## 6. Docker

Materialize models using `dvc repro` or `dvc pull`, then build and run both services locally:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The dashboard is at `http://localhost:8501`, the API at `http://localhost:8000`, and interactive API docs at `http://localhost:8000/docs`. Compose mounts local `models/` read-only into the API container and starts the daily MLOps automation service. Without trained artifacts, API health reports zero models and prediction requests return 404. Compose reads dashboard credentials from the ignored local `.env`; never bake credentials into an image.

For Streamlit Community Cloud, select the GitHub repository, target branch, and root entry point `frontend.py`. Add `SUPABASE_URL` and `SUPABASE_KEY` in the app's Settings -> Secrets as TOML. Cloud deployment must be finalized from the hosting dashboard using your account. Restrict the current broad Supabase RLS policies before exposing the database publicly.

For a Compose host, build and start the services with `docker compose up --build -d`. The production Compose file uses GHCR images and named volumes; use it only after publishing those images. It keeps data, DVC cache, metrics, MLflow runs, and models in persistent volumes. The API and scheduler images contain the initial model bundle, and the scheduler's retrained artifacts are shared with inference. Back up these volumes and configure a DVC remote for recovery.

## 7. Verification

```powershell
python -m pytest -q
python -m compileall -q api src monitoring dashboard
```

The tests use synthetic data and mocked model artifacts; they do not call Yahoo Finance or Supabase.

## Scope Notes

The live repository's Supabase implementation is canonical; older notes describe conflicting SQLite variants. Kubernetes and LLM integration are marked as course-scope-dependent extensions in the proposal and are not included in this core implementation. Confirm whether the instructor requires them before expanding scope.
