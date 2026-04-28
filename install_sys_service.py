#!/usr/bin/env python3
"""一键安装 crypto-price-api 为 systemd 服务"""
import os
import shutil
import subprocess
import sys

SERVICE_NAME = "crypto-price-api"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
SERVICE_DIR = "/etc/systemd/system"


def get_python_path():
    return sys.executable


def check_env_file():
    if not os.path.exists(ENV_FILE):
        print(f"错误: 未找到 .env 文件，请先创建:")
        print(f"  cp .env.example .env")
        print(f"  vim .env")
        sys.exit(1)


def generate_service(python_path):
    return f"""[Unit]
Description=Crypto Price API - Binance Spot WebSocket to Redis
After=network.target redis.service

[Service]
Type=simple
WorkingDirectory={SCRIPT_DIR}
EnvironmentFile={ENV_FILE}
ExecStart={python_path} main.py
Restart=always
RestartSec=5
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
"""


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"命令失败: {cmd}")
        print(r.stderr.strip())
        sys.exit(1)
    return r.stdout.strip()


def main():
    if os.geteuid() != 0:
        print("请使用 sudo 运行此脚本")
        sys.exit(1)

    check_env_file()

    python_path = get_python_path()
    service_content = generate_service(python_path)
    service_path = os.path.join(SERVICE_DIR, f"{SERVICE_NAME}.service")

    # 写入 service 文件
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"已生成: {service_path}")
    print(f"  工作目录: {SCRIPT_DIR}")
    print(f"  Python:   {python_path}")

    # reload + enable + start
    run("systemctl daemon-reload")
    run(f"systemctl enable {SERVICE_NAME}")
    run(f"systemctl restart {SERVICE_NAME}")
    print(f"\n服务已启动并设为开机自启 ✓")

    # 打印状态
    print()
    run(f"systemctl status {SERVICE_NAME} --no-pager")


if __name__ == "__main__":
    main()
