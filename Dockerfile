FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/models

WORKDIR /app

COPY requirements-api.txt ./requirements-api.txt
RUN python -m pip install --no-cache-dir --retries 10 --timeout 300 -r requirements-api.txt

COPY api ./api
COPY src ./src
COPY monitoring ./monitoring
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
