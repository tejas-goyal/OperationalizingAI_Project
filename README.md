# Crypto Volatility Spike Detector

Real-time volatility spike detection for BTC-USD and ETH-USD using XGBoost, served via FastAPI with Prometheus + Grafana monitoring.

**Team:** Eshita Raj Vegesna, Vaishnavi Athrey Ramesh, Litesha Nagendra, Tejas Goyal

## Quick Start

```bash
docker compose -f docker/compose.yaml up -d --build
```

Services start at: API → `localhost:8000` | Grafana → `localhost:3000` | Prometheus → `localhost:9090` | MLflow → `localhost:5001`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Liveness check + uptime |
| `/predict` | POST | Spike prediction (JSON body: `{"features": {...}}`) |
| `/version` | GET | Model metadata and feature list |
| `/metrics` | GET | Prometheus metrics |

## Architecture

```
Coinbase WS → Kafka → Featurizer → FastAPI (/predict)
                                        ↓
                                   Prometheus → Grafana
```

## Rollback

```bash
# Switch to z-score baseline
docker compose stop api
MODEL_VARIANT=baseline docker compose up -d api
```

## Demo Video

[Link to unlisted YouTube / Loom video — TODO]
