#!/bin/bash

# GenieUs 停止スクリプト

echo "🛑 GenieUs を停止しています..."

# PIDファイルから停止
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm .backend.pid
    echo "✅ バックエンドを停止しました"
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm .frontend.pid
    echo "✅ フロントエンドを停止しました"
fi

# ポートベースで強制停止
echo "🔍 残プロセスをチェック中..."

# ポート8000のプロセスを停止
BACKEND_PROC=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$BACKEND_PROC" ]; then
    kill -9 $BACKEND_PROC 2>/dev/null || true
    echo "✅ ポート8000のプロセスを停止しました"
fi

# ポート3000のプロセスを停止
FRONTEND_PROC=$(lsof -ti:3000 2>/dev/null || true)
if [ ! -z "$FRONTEND_PROC" ]; then
    kill -9 $FRONTEND_PROC 2>/dev/null || true
    echo "✅ ポート3000のプロセスを停止しました"
fi

echo "🎉 GenieUs を完全に停止しました"