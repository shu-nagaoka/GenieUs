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

# 依存関係のインストール（本番用のみ、インストールキャッシュ無効化）
RUN uv sync --frozen --no-dev --no-cache

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

# アプリケーションコードのコピー（dataディレクトリ除外）
COPY --chown=genius:genius src/ ./src/

# 非rootユーザーに切り替え
USER genius

# ポートを動的に設定（Cloud RunはPORT=8080を設定）
EXPOSE 8080

# Cloud Run用環境変数（PORTは実行時に設定される）
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ヘルスチェック（Cloud Run用に最適化 - 長い起動時間を考慮）
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
  CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# アプリケーションの起動（main.pyの設定を使用）
CMD ["python", "-m", "src.main"]