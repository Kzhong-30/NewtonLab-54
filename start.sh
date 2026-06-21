#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "正在停止服务..."
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        wait "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "所有服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "=========================================="
echo "剧本杀平台 - 一键启动脚本"
echo "=========================================="

echo "[1/4] 初始化后端..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
if [ ! -f "script_kill.db" ]; then
    python init_db.py > /dev/null 2>&1
fi
echo "  后端初始化完成"

echo "[2/4] 初始化前端..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
fi
echo "  前端初始化完成"

echo "[3/4] 启动后端服务..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3
echo "  后端服务已启动 (PID: $BACKEND_PID)"

echo "[4/4] 启动前端服务..."
cd "$SCRIPT_DIR/frontend"
npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 3
echo "  前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "所有服务启动成功！"
echo "=========================================="
echo "前端应用: http://localhost:5173"
echo "后端 API: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "=========================================="
echo "按 Ctrl+C 停止所有服务"
echo ""

while true; do
    sleep 2
done
