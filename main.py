"""币安 WebSocket 实时价格 → Redis Pub/Sub"""
from ws_stream import run_stream
import config

if __name__ == "__main__":
    run_stream(config)
