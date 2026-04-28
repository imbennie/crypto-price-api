import asyncio
import json
import logging
import time

import websockets

from redis_client import get_redis, save_and_publish

logger = logging.getLogger(__name__)


async def _connect_and_stream(ws_url: str, channel: str, hash_key: str, label: str, config):
    """连接单个 WebSocket 并持续推送价格到 Redis"""
    r = get_redis(config)
    while True:
        try:
            logger.info("[%s] 正在连接 %s ...", label, ws_url)
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
                logger.info("[%s] 连接成功，开始接收数据", label)
                batch_count = 0
                async for raw in ws:
                    # !miniTicker@arr 返回数组
                    tickers = json.loads(raw)
                    if not isinstance(tickers, list):
                        tickers = [tickers]
                    for t in tickers:
                        symbol = t.get("s")
                        price = t.get("c")          # 最新价 close
                        event_time = t.get("E", int(time.time() * 1000))
                        if symbol and price:
                            save_and_publish(r, channel, hash_key, symbol, price, event_time)
                    batch_count += 1
                    logger.info("[%s] 币安数据已获取并写入Redis，本批 %d 个币种（第 %d 批）",
                                label, len(tickers), batch_count)
        except (
            websockets.exceptions.ConnectionClosed,
            websockets.exceptions.InvalidStatusCode,
            asyncio.TimeoutError,
            OSError,
        ) as e:
            logger.warning("[%s] 连接断开: %s，%ds 后重连", label, e, config.RECONNECT_INTERVAL)
        except Exception as e:
            logger.error("[%s] 异常: %s", label, e, exc_info=True)

        await asyncio.sleep(config.RECONNECT_INTERVAL)


def run_stream(config):
    """启动现货 WebSocket 流"""
    import config as cfg

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    asyncio.run(
        _connect_and_stream(cfg.SPOT_WS_URL, cfg.SPOT_PRICE_CHANNEL, cfg.SPOT_PRICE_HASH, "SPOT", cfg)
    )
