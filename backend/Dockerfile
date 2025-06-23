FROM python:3.12-slim

# システムの更新と必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
RUN pip install uv

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピー
COPY pyproject.toml ./

# 依存関係のインストール
RUN uv sync --no-dev

# アプリケーションコードのコピー
COPY src/ ./src/

# ポート8000を公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# アプリケーションの起動
CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]