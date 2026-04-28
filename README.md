# Crypto Price API

通过 Binance WebSocket 实时获取所有现货币种最新价格，写入 Redis 缓存并发布到 Pub/Sub 频道，方便下游服务消费或提供 REST API。

## 架构

```
Binance WebSocket (!miniTicker@arr)
        │
        ▼
  Python 服务（本项目）
        │
        ├── HSET  crypto:spot:prices  {SYMBOL: price_json}   ← Redis 缓存
        └── PUBLISH crypto:spot:price  price_json             ← Redis Pub/Sub
```

## 数据格式

**Redis Hash** — `crypto:spot:prices`

| Field | Value |
|---|---|
| BTCUSDT | `{"symbol":"BTCUSDT","price":"95000.00","time":1745846400000}` |
| ETHUSDT | `{"symbol":"ETHUSDT","price":"3600.00","time":1745846400000}` |
| ... | ... |

下游 REST API 可直接 `HGETALL crypto:spot:prices` 获取全部价格，或 `HGET crypto:spot:prices BTCUSDT` 获取单个。

## 快速开始

### 依赖

- Python 3.8+
- Redis
- pip: `websockets`, `redis`

```bash
pip install websockets redis
```

### 配置

通过环境变量配置：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `REDIS_PWD` | Redis 密码（必填） | - |
| `REDIS_HOST` | Redis 地址 | `127.0.0.1` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_DB` | Redis 数据库编号 | `0` |

复制示例配置文件并填入实际值：

```bash
cp .env.example .env
```

### 启动

```bash
# 方式一：直接运行
python3 main.py

# 方式二：一键安装为 systemd 服务（推荐生产环境）
sudo python3 install_sys_service.py
```

### 测试订阅

```bash
python3 subscriber.py spot
```

## 项目结构

```
crypto-price-api/
├── config.py          # 环境变量配置
├── redis_client.py    # Redis 连接池 + 数据写入/发布
├── ws_stream.py       # WebSocket 核心逻辑
├── main.py            # 启动入口
├── install_sys_service.py  # 一键安装 systemd 服务
├── subscriber.py      # 订阅测试工具
├── .env.example       # 环境变量示例
└── README.md
```

## License

MIT
