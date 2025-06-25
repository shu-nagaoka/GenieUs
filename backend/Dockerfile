# Cloud Run optimized Dockerfile for FastAPI backend
FROM python:3.12.8-slim as builder

# システムの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
RUN pip install uv

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピー
COPY pyproject.toml uv.lock* ./

# 依存関係のインストール（本番用のみ）
RUN uv sync --frozen --no-dev

# 実行用ステージ
FROM python:3.12.8-slim as runner

# 必要最小限のシステムパッケージ
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 非rootユーザーの作成
RUN useradd --create-home --shell /bin/bash genius

WORKDIR /app

# Pythonの依存関係をコピー
COPY --from=builder /app/.venv /app/.venv

# 仮想環境をPATHに追加
ENV PATH="/app/.venv/bin:$PATH"

# アプリケーションコードのコピー
COPY --chown=genius:genius src/ ./src/

# 非rootユーザーに切り替え
USER genius

# ポート8000を公開
EXPOSE 8000

# Cloud Run用環境変数
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# アプリケーションの起動（Cloud Run用に最適化）
CMD uvicorn src.main:app --host ${HOST} --port ${PORT} --workers 1