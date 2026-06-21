#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
HOST="0.0.0.0"
PORT="5173"

echo "=========================================="
echo "剧本杀平台 - 前端启动脚本"
echo "=========================================="

cd "$FRONTEND_DIR"

echo "[1/3] 检查 Node.js 环境..."
node --version
npm --version

echo "[2/3] 安装依赖..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "[3/3] 启动前端开发服务器..."
echo "服务地址: http://localhost:$PORT"
echo "后端 API: http://localhost:8000"
npm run dev -- --host "$HOST" --port "$PORT"
