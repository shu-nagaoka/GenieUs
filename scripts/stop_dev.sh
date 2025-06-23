#!/bin/bash

# GenieUs開発環境停止スクリプト
# フロントエンドとバックエンドを停止

echo "🛑 GenieUs開発環境を停止します..."

# プロセス停止
echo "📛 プロセスを停止中..."
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート3000のプロセスを停止" || echo "   ポート3000: プロセスなし"
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8000のプロセスを停止" || echo "   ポート8000: プロセスなし"
lsof -ti:8001 | xargs kill -9 2>/dev/null && echo "   ✅ ポート8001のプロセスを停止" || echo "   ポート8001: プロセスなし"

# プロセスも念のため停止
pkill -f "next dev" 2>/dev/null && echo "   ✅ Next.jsプロセスを停止" || true
pkill -f "uvicorn" 2>/dev/null && echo "   ✅ Uvicornプロセスを停止" || true
pkill -f "adk web" 2>/dev/null && echo "   ✅ ADK Web UIプロセスを停止" || true

echo "✅ 停止完了!"