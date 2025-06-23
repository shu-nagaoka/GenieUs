# Linx Backend

SA 専用 RAG のフルスタックアプリケーションリポジトリのバックエンドです。

## アーキテクチャ概要

このバックエンドアプリケーションは、クリーンアーキテクチャの原則に基づいて設計されており、以下の主要なディレクトリ構造を持っています。

- **`src/agents/`**: AIエージェント（RAGエージェント、サーチエージェント等）を開発・管理します。Agent Development Kit (ADK) を活用し、モジュール化されたエージェントコンポーネントを構築します。
- **`src/application/`**: ドメイン層として、不変なビジネスロジックやアプリケーションのコアとなるルールをインターフェースとして定義し、具体的なユースケースを実装します。
- **`src/config/`**: アプリケーション全体の設定情報（環境変数、定数など）を管理します。主に `di_provider` 層から利用されます。
- **`src/di_provider/`**: 依存性注入（DI）コンテナ（`dependency-injector` を使用）を管理し、アプリケーション全体の依存関係の解決や設定の注入を行います。`infrastructure` 層と `application` 層を結合する役割も担います。
- **`src/infrastructure/`**: `application` 層で定義されたインターフェースを、具体的な技術（データベースアクセス、外部API連携など）を用いて実装します。Google Cloud Platform 関連のサービスアダプターや永続化層アダプターなどが含まれます。
- **`src/presentation/`**: アプリケーションのユーザーインターフェースや外部システムとの接点を担当します。RESTful API、Model Context Protocol (MCP)、ツールコーリングなどのインターフェースを提供します。
- **`src/share/`**: アプリケーション全体で共通して利用されるユーティリティ（ロガー、共通関数など）を配置します。

## 技術スタック

- Python 3.12+
- FastAPI: Webフレームワーク
- Pydantic: データバリデーション
- dependency-injector: 依存性注入
- Google Cloud Services:
    - Discovery Engine
    - Cloud Storage
    - Generative AI (Vertex AI)
    - AI Platform
- Ruff: リンター、フォーマッター

詳細な依存関係は `pyproject.toml` を参照してください。

## プロジェクトの始め方 (uv を使用)

### 1. Pythonのインストール

このプロジェクトは Python 3.12 以降が必要です。もしまだインストールしていない場合は、適切な方法でインストールしてください。

### 2. uv のインストール

`uv` は Rust 製の高速な Python パッケージインストーラー兼リゾルバーです。
以下のコマンドで `uv` をインストールします（macOS / Linux の場合）。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows の場合は、[公式ドキュメント](https://astral.sh/uv)を参照してください。

### 3. 仮想環境の作成と有効化

プロジェクトのルートディレクトリ（この `README.md` があるディレクトリの親、つまり `Linx/backend/`）で、以下のコマンドを実行して仮想環境を作成し、有効化します。

```bash
# 仮想環境の作成 (例: .venv という名前の仮想環境)
uv venv
# 仮想環境の有効化 (シェルによってコマンドが異なります)
# bash/zsh の場合
source .venv/bin/activate
# fish の場合
source .venv/bin/activate.fish
# PowerShell の場合
.venv\Scripts\Activate.ps1
```

### 4. 依存関係のインストール

仮想環境が有効化されていることを確認し、以下のコマンドを実行してプロジェクトの依存関係をインストールします。

```bash
# pyproject.toml から直接インストール
uv pip install .
# 開発用依存関係もインストールする場合
uv pip install .[dev]
```
**注釈:** `pyproject.toml` には直接的な `requirements.txt` の記述はありませんが、`dependencies` と `optional-dependencies` が定義されています。`uv pip install .` で基本的な依存関係が、 `uv pip install .[dev]` で開発用も含めた依存関係がインストールされます。

### 5. 環境変数の設定と認証

アプリケーションを実行するためには、必要な環境変数を設定する必要があります。

**環境変数ファイル:**

環境ごとに設定ファイルを用意します。
- `.env.dev`: 開発環境用
- `.env.prod`: 本番環境用
- `.env.staging`: ステージング環境用

これらのファイルを基に、実行環境に応じた `.env` ファイルを作成するか、アプリケーションが適切なファイルを読み込むように設定してください。
開発が進んだ段階で、必要な環境変数のリストとその例を記載した `.env.example` ファイルを更新・管理してください。

例 (`.env.dev` ファイル):

```bash
PROJECT_ID="your-gcp-project-id"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

**Google Cloud への認証 (ローカル開発時):**

ローカル環境で Google Cloud のサービスを利用する際の認証は、以下のいずれかの方法で行います。

1.  **Application Default Credentials (ADC) を使用する方法:**
    開発者個人のアカウントで認証します。
    ```bash
    gcloud auth application-default login
    ```
    このコマンドを実行すると、ブラウザが開きGoogleアカウントでのログインを求められます。認証後、ADCが設定され、ローカル環境からGCPサービスへのアクセスが可能になります。

2.  **サービスアカウントの権限借用 (Impersonation):**
    特定のサービスアカウントの権限を一時的に借用して開発を行います。事前に権限借用の設定が必要です。
    ```bash
    gcloud auth application-default login --impersonate-service-account=SERVICE_ACCOUNT_EMAIL
    ```
    または、環境変数 `GOOGLE_APPLICATION_CREDENTIALS` にサービスアカウントキーのパスを設定する代わりに、コード内で権限借用を行うライブラリ（例: `google-auth`）を使用します。

    より詳細な設定や組織のポリシーに応じて、適切な認証方法を選択してください。

### 6. アプリケーションの実行 (FastAPI の場合)

FastAPI アプリケーションを実行するには、Uvicorn などの ASGI サーバーを使用します。
エントリーポイントとなるファイル（例: `src/main.py` や `src/presentation/api/main.py` など、プロジェクト構造によります）を指定して実行します。

```bash
# 例: src/main.py がエントリーポイントの場合
uvicorn src.main:app --reload
```
`--reload` オプションは開発中に便利で、コード変更時にサーバーを自動的にリロードします。

### 7. Linter と Formatter の実行 (Ruff)

コードの品質を保つために、Ruff を使用してリンティングとフォーマットを行います。

```bash
# リンティング
ruff check .
# フォーマット
ruff format .
# リンティングと自動修正
ruff check . --fix
```

## その他

- **`.gitignore`**: プロジェクトルートにある `.gitignore` は汎用的な設定になっています。開発の過程で、プロジェクト固有の無視ファイルやディレクトリが出てきた場合は、適宜更新してください。
- **依存関係 (`pyproject.toml`)**: 新しいライブラリが必要になった場合は、`pyproject.toml` の `[project.dependencies]` または `[project.optional-dependencies.dev]` に追記し、`uv pip install .` または `uv pip install .[dev]` を実行して環境に反映させてください。
- **`cloudbuild.yaml`**: プロジェクトルートにある `cloudbuild.yaml` は現時点では仮のものです。CI/CDパイプラインの要件に合わせて、必要に応じて更新してください。