"""快速测试：订阅 Redis 频道查看实时价格"""
import json
import sys
import redis
import config

CHANNELS = {
    "spot": config.SPOT_PRICE_CHANNEL,
    "futures": config.FUTURES_PRICE_CHANNEL,
}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "spot"
    channel = CHANNELS.get(mode)
    if not channel:
        print(f"用法: python subscriber.py [spot|futures|all]")
        return

    r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        db=config.REDIS_DB,
        decode_responses=True,
    )

    sub = ["spot", "futures"] if mode == "all" and len(sys.argv) > 1 and sys.argv[1] == "all" else [mode]
    ps = r.pubsub()
    channels = [CHANNELS[s] for s in sub]
    ps.subscribe(*channels)
    print(f"已订阅: {channels}，等待消息... (Ctrl+C 退出)")

    for msg in ps.listen():
        if msg["type"] == "message":
            data = json.loads(msg["data"])
            print(f"[{msg['channel']}] {data['symbol']}: {data['price']}")


if __name__ == "__main__":
    main()
