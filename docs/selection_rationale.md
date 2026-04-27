# Model Selection Rationale

## Candidate Models

Each team member trained their own volatility spike detector during Part A. We compared test-set metrics to select the best candidate for the team deployment.

| Team Member | Model Type | Test PR-AUC | Test ROC-AUC | Test Best-F1 | Notes |
|-------------|-----------|-------------|-------------|-------------|-------|
| **Eshita Raj Vegesna** | XGBoost (300 est, depth 4) | **0.5598** | **0.8746** | **0.4348** | Time-based windows (10s/30s/60s), 20 features |
| Vaishnavi Athrey Ramesh | XGBoost (200 est, depth 5) | 0.121 | 0.682 | 0.201 | Tick-based windows, 18 features |
| Litesha Nagendra | Random Forest | 0.098 | 0.641 | 0.175 | Tick-based windows, 15 features |
| Tejas Goyal | XGBoost (100 est, depth 3) | 0.143 | 0.712 | 0.218 | Mixed windows, 16 features |

## Selection: Eshita's XGBoost

**Why this model wins:**

1. **Highest PR-AUC (0.5598):** PR-AUC is the primary metric for imbalanced classification (14.8% spike rate). It is ~4x higher than the next best candidate.

2. **Strong ROC-AUC (0.8746):** Confirms the model has good discriminative power, not just threshold-gaming.

3. **Feature engineering quality:** Time-based sliding windows (10s, 30s, 60s) capture multi-scale volatility patterns better than fixed tick-count windows. The 20-feature set covers return statistics, tick counts, spread dynamics, and trade intensity at each scale.

4. **Production-ready artifacts:** Model saved as XGBoost JSON (portable, no pickle security concerns), with separate metadata files for threshold and feature ordering.

5. **Baseline comparison:** The z-score baseline (ret_std_60s > mean + 1.5*std) provides a meaningful lower bound. The XGBoost model substantially outperforms it, confirming the ML approach adds value.

## Deployment Configuration

- **Model format:** XGBoost JSON (`xgboost_model.json`)
- **Best threshold (from validation):** 0.001376
- **Features:** 20 numeric features computed from streaming tick data
- **Rollback:** Set `MODEL_VARIANT=baseline` to fall back to z-score rule
