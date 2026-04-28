import os

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PWD")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis Pub/Sub 频道
SPOT_PRICE_CHANNEL = "crypto:spot:price"

# Redis Hash 缓存 key（用于 REST API 读取）
SPOT_PRICE_HASH = "crypto:spot:prices"

# Binance WebSocket 地址 — 订阅所有现货币种 miniTicker
SPOT_WS_URL = "wss://stream.binance.com:9443/ws/!miniTicker@arr"

# 重连间隔（秒）
RECONNECT_INTERVAL = 5
