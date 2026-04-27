# Demo Video Script & Checklist

**Target length:** 8 minutes | **Format:** Screen recording with voiceover, uploaded as unlisted YouTube

**Required sections:** Startup, prediction, failure recovery, rollback, metrics summary.

---

## Pre-Recording Checklist

- [ ] Docker Desktop running
- [ ] Kill anything on ports 8000, 9090, 3000, 9092, 5001: `lsof -ti:8000,9090,3000,9092,5001 | xargs kill -9 2>/dev/null`
- [ ] Terminal font size ≥ 14pt so commands are readable on video
- [ ] Two browser tabs ready (don't open yet — open during recording for effect)
- [ ] Clone the repo fresh or `cd` into the project root so the grader sees the repo structure

---

## Script

### 1. Intro & Architecture (45s)

> "Hi, we're Eshita, Vaishnavi, Litesha, and Tejas. We built a real-time crypto volatility spike detector. Here's the architecture."

**Action:** Open `docs/architecture_diagram.png` full-screen.

> "Coinbase WebSocket ticks flow into Kafka, our featurizer computes 20 time-windowed features, and the FastAPI service returns spike predictions. Prometheus scrapes the API and Grafana visualizes everything. The whole stack runs in Docker Compose."

---

### 2. One-Command Startup (60s)

```bash
# Show the repo structure first
ls -la
ls docker/

# Start everything
docker compose -f docker/compose.yaml up -d --build
```

> "One command brings up six services: Kafka, MLflow, the prediction API, Prometheus, and Grafana. Each service has health checks — nothing starts until its dependencies are ready."

**Wait ~30s, then:**

```bash
docker compose -f docker/compose.yaml ps
```

> "All containers are healthy."

---

### 3. API Endpoints & Prediction (90s)

```bash
# Health check
curl -s http://localhost:8000/health | jq .
```

> "The /health endpoint shows the API is up, which model variant is loaded, and uptime."

```bash
# Model version
curl -s http://localhost:8000/version | jq .
```

> "The /version endpoint shows our model metadata — 20 features, the decision threshold, and supported trading pairs."

```bash
# Make a prediction
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "product_id": "BTC-USD",
      "ret_mean_10s": 0.000001, "ret_std_10s": 0.000012, "ret_abs_10s": 0.000008,
      "tick_count_10s": 25, "spread_mean_10s": 0.000002, "trade_intensity_10s": 2.5,
      "ret_mean_30s": 0.000001, "ret_std_30s": 0.000015, "ret_abs_30s": 0.00001,
      "tick_count_30s": 35, "spread_mean_30s": 0.000002, "trade_intensity_30s": 3.0,
      "ret_mean_60s": 0.000001, "ret_std_60s": 0.00002, "ret_abs_60s": 0.000012,
      "tick_count_60s": 45, "spread_mean_60s": 0.000002, "trade_intensity_60s": 3.5,
      "spread_bps": 0.05, "mid_price": 66900.0
    }
  }' | jq .
```

> "The /predict endpoint takes 20 features and returns the spike probability, whether a spike was predicted, and the threshold used."

---

### 4. Failure Recovery (75s)

> "Now let's simulate a failure."

**Action:** Open browser to `http://localhost:3000` — click on the "Crypto Volatility API" dashboard. Show it's live with data.

```bash
# Kill the API container
docker compose -f docker/compose.yaml stop api
```

> "I've stopped the API. Watch Grafana — the request rate drops to zero."

**Action:** Switch to browser, show Grafana panels going flat / showing no data for ~10 seconds.

```bash
# Bring it back
docker compose -f docker/compose.yaml start api
```

> "One command restarts it. The health check passes, Prometheus picks it back up, and Grafana shows traffic again."

**Action:** Switch to browser, show data returning in the panels. Wait a few seconds for it to appear.

```bash
# Verify it's back
curl -s http://localhost:8000/health | jq .status
```

---

### 5. Rollback to Baseline (60s)

> "If the ML model starts producing bad predictions — maybe due to data drift — we can roll back to the z-score baseline instantly."

```bash
# Stop the API
docker compose -f docker/compose.yaml stop api

# Restart with baseline model
MODEL_VARIANT=baseline docker compose -f docker/compose.yaml up -d api

# Verify the switch
curl -s http://localhost:8000/version | jq .variant
```

> "The variant is now 'baseline'. The z-score rule uses a simple statistical threshold instead of XGBoost. No rebuild needed — just an environment variable change."

```bash
# Switch back to ML model
docker compose -f docker/compose.yaml stop api
MODEL_VARIANT=ml docker compose -f docker/compose.yaml up -d api
curl -s http://localhost:8000/version | jq .variant
```

> "And we're back to the ML model."

---

### 6. Monitoring Dashboard (60s)

**Action:** Switch to browser showing Grafana at `localhost:3000`.

> "Grafana auto-provisions on startup with four panels."

**Action:** Point at each panel as you describe it.

> "Top-left: predict latency — p50 and p95 in milliseconds. Top-right: request rate to /predict. Bottom-left: error rate — anything non-2xx. Bottom-right: traffic across all endpoints."

**Action:** Open `localhost:9090/targets` in a new tab.

> "Prometheus is scraping our API every 15 seconds. The target is healthy."

---

### 7. Metrics Summary (45s)

> "Let me summarize our key metrics."

```bash
# Run the load test on camera
python scripts/load_test.py
```

> "100 burst requests. Our p50 latency is under 20 milliseconds, p95 under 100ms, and we sustain over 50 requests per second. Zero errors."

> "On model quality: our XGBoost achieves a test PR-AUC of 0.5598 versus the z-score baseline's 0.35 — a 60% improvement. ROC-AUC is 0.8746. The system maintained 99%+ uptime during our testing window."

---

### 8. CI Pipeline & Wrap-Up (45s)

**Action:** Switch to browser, open the GitHub repo → Actions tab showing a green CI run.

> "Every push runs our CI pipeline: Black formatting check, ruff linting, pytest with 7 integration tests, and a Docker build smoke test."

> "To wrap up: one-command startup, sub-100ms predictions, instant rollback, full Prometheus-Grafana observability, automated drift detection, and a CI pipeline that catches issues before they hit main. Thanks for watching."

---

## Post-Recording

- [ ] Upload to YouTube as **unlisted**
- [ ] Copy the video URL
- [ ] Add it to README.md under "## Demo Video"
- [ ] Tag the final release: `git tag -a v1.0.0 -m "Final submission" && git push origin v1.0.0`
- [ ] Verify the YouTube link works in an incognito window (no sign-in required)
