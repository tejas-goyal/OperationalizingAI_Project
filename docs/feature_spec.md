# Feature Specification

## Overview

20 numeric features computed from streaming Coinbase tick data using time-based sliding windows. Features are computed per-tick as new data arrives.

## Window Sizes

- **10 seconds** — captures micro-scale volatility bursts
- **30 seconds** — medium-term trend signals
- **60 seconds** — broader regime context

## Features

### Per-Window Features (×3 windows = 18 features)

| Feature | Description | Window Sizes |
|---------|-------------|-------------|
| `ret_mean_{w}s` | Mean log return over window | 10s, 30s, 60s |
| `ret_std_{w}s` | Standard deviation of log returns | 10s, 30s, 60s |
| `ret_abs_{w}s` | Mean absolute log return | 10s, 30s, 60s |
| `tick_count_{w}s` | Number of ticks in window | 10s, 30s, 60s |
| `spread_mean_{w}s` | Mean bid-ask spread | 10s, 30s, 60s |
| `trade_intensity_{w}s` | Ticks per second (tick_count / window_seconds) | 10s, 30s, 60s |

### Global Features (2 features)

| Feature | Description |
|---------|-------------|
| `spread_bps` | Current bid-ask spread in basis points: `(ask - bid) / mid × 10000` |
| `mid_price` | Current mid price: `(bid + ask) / 2` |

## Label Definition

- **future_vol:** Forward 60-second rolling standard deviation of log returns
- **Spike threshold (τ):** 85th percentile of future_vol = 0.000054
- **label:** 1 if future_vol > τ, else 0
- **Spike rate:** 14.8%

## Feature Computation

Features are computed by the `WindowBuffer` class in `featurizer.py`, which maintains a time-based deque of recent ticks (max 120 seconds). On each incoming tick, the buffer evicts expired entries and computes features across all three window sizes.
