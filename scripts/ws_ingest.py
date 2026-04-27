#!/usr/bin/env python3
"""
Coinbase WebSocket → Kafka ingestor with exponential backoff reconnect.

Connects to Coinbase Advanced Trade public ticker channel,
receives real-time ticks for configured pairs, and publishes
JSON messages to the Kafka 'ticks.raw' topic.

Usage:
    python scripts/ws_ingest.py --pair BTC-USD --minutes 60
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone

import websockets
import asyncio
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
COINBASE_WS_URL = os.getenv("COINBASE_WS_URL", "wss://advanced-trade-ws.coinbase.com")
TOPIC = "ticks.raw"
MAX_BACKOFF = 60

shutdown_requested = False


def handle_signal(signum, frame):
    global shutdown_requested
    log.info("Shutdown signal received (signal %d)", signum)
    shutdown_requested = True


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def create_producer(retries=5):
    """Create Kafka producer with retry logic."""
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks=1,
                retries=3,
            )
            log.info("Kafka producer connected to %s", KAFKA_BOOTSTRAP)
            return producer
        except Exception as e:
            wait = min(2**attempt, MAX_BACKOFF)
            log.warning(
                "Kafka connection failed (attempt %d/%d): %s. Retrying in %ds...",
                attempt + 1,
                retries,
                e,
                wait,
            )
            time.sleep(wait)
    log.error("Could not connect to Kafka after %d attempts", retries)
    sys.exit(1)


async def ingest(pairs: list, minutes: int, save_dir: str = "data/raw"):
    """Connect to Coinbase WS and stream ticks to Kafka."""
    global shutdown_requested

    producer = create_producer()
    os.makedirs(save_dir, exist_ok=True)

    end_time = time.time() + minutes * 60
    tick_count = 0
    backoff = 1

    while not shutdown_requested and time.time() < end_time:
        try:
            log.info("Connecting to %s ...", COINBASE_WS_URL)
            async with websockets.connect(COINBASE_WS_URL) as ws:
                subscribe_msg = {
                    "type": "subscribe",
                    "product_ids": pairs,
                    "channel": "ticker",
                }
                await ws.send(json.dumps(subscribe_msg))
                log.info("Subscribed to ticker for %s", pairs)

                backoff = 1

                async for raw_msg in ws:
                    if shutdown_requested or time.time() >= end_time:
                        break

                    msg = json.loads(raw_msg)

                    if msg.get("channel") != "ticker":
                        continue

                    for event in msg.get("events", []):
                        for ticker in event.get("tickers", []):
                            tick = {
                                "ts": datetime.now(timezone.utc).timestamp(),
                                "product_id": ticker.get("product_id", ""),
                                "price": ticker.get("price", "0"),
                                "best_bid": ticker.get("best_bid", "0"),
                                "best_ask": ticker.get("best_ask", "0"),
                                "volume_24_h": ticker.get("volume_24_h", "0"),
                            }

                            producer.send(TOPIC, value=tick)
                            tick_count += 1

                            if tick_count % 100 == 0:
                                log.info(
                                    "Ticks: %d | %s @ %s",
                                    tick_count,
                                    tick["product_id"],
                                    tick["price"],
                                )

        except websockets.ConnectionClosed as e:
            log.warning("WebSocket closed: %s. Reconnecting in %ds...", e, backoff)
        except Exception as e:
            log.error("WebSocket error: %s. Reconnecting in %ds...", e, backoff)

        if not shutdown_requested and time.time() < end_time:
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)

    producer.flush()
    producer.close()
    log.info("Ingestion complete. Total ticks: %d", tick_count)


def main():
    parser = argparse.ArgumentParser(description="Coinbase WS → Kafka ingestor")
    parser.add_argument(
        "--pair", default="BTC-USD", help="Comma-separated pairs (e.g. BTC-USD,ETH-USD)"
    )
    parser.add_argument(
        "--minutes", type=int, default=60, help="Duration to ingest (minutes)"
    )
    args = parser.parse_args()

    pairs = [p.strip() for p in args.pair.split(",")]
    log.info("Starting ingestion: pairs=%s, duration=%d min", pairs, args.minutes)

    asyncio.run(ingest(pairs, args.minutes))


if __name__ == "__main__":
    main()
