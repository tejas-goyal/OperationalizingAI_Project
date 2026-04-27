# Runbook — Crypto Volatility API

## Starting the Stack

```bash
cd docker
docker compose up -d --build
```

Wait ~2 minutes for all services to become healthy. Verify with:

```bash
docker compose ps
```

All containers should show `healthy` or `running`.

## Stopping the Stack

```bash
cd docker
docker compose down
```

To also remove volumes (resets all data):

```bash
docker compose down -v
```

## Common Issues

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000
# Kill it
lsof -ti:8000 | xargs kill -9
```

### API Container Not Starting

Check logs:
```bash
docker logs crypto-api
```

Common causes: model artifact files missing, Python dependency errors.

### Grafana Shows No Data

1. Check Prometheus is scraping: visit `localhost:9090/targets`
2. Verify API is exposing metrics: `curl localhost:8000/metrics`
3. Wait 30s for first scrape interval to complete

### MLflow Container Slow to Start

MLflow installs packages at runtime. The healthcheck has `start_period: 120s` to accommodate this. Wait up to 2 minutes.

## Rollback to Baseline Model

If the ML model produces unexpected results:

```bash
docker compose stop api
MODEL_VARIANT=baseline docker compose up -d api
```

Verify: `curl localhost:8000/version | jq .variant` should return `"baseline"`.

To switch back: repeat with `MODEL_VARIANT=ml`.

## Running Tests

```bash
# Unit/integration tests
pytest tests/ -v

# Load test (requires running API)
python scripts/load_test.py

# Replay test (requires running API + feature parquet)
python scripts/replay_api_test.py --parquet data/processed/features.parquet --n 50
```

## CI Pipeline

CI runs automatically on push/PR to `main`. It checks:
1. `ruff` linting on `api/`, `tests/`, `scripts/`
2. `pytest` integration tests
3. Docker image build + smoke test
