#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
HOST="0.0.0.0"
PORT="8000"

echo "=========================================="
echo "剧本杀平台 - 后端启动脚本"
echo "=========================================="

cd "$BACKEND_DIR"

echo "[1/4] 检查 Python 环境..."
python3 --version

echo "[2/4] 安装依赖..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "[3/4] 初始化数据库..."
if [ ! -f "script_kill.db" ]; then
    python init_db.py
fi

echo "[4/4] 启动后端服务..."
echo "服务地址: http://$HOST:$PORT"
echo "API 文档: http://$HOST:$PORT/docs"
exec uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
