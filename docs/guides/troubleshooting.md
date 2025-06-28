# トラブルシューティングガイド

GenieUs開発時によくある問題と解決策の完全ガイド

## 🚀 環境構築・起動の問題

### ポート使用中エラー
```bash
Error: Port 3000/8080 is already in use
```

**解決策:**
```bash
# 全サービス停止
./scripts/stop_dev.sh

# 再起動
./scripts/start-dev.sh
```

### 依存関係エラー

#### バックエンド依存関係問題
```bash
Error: Module not found / Import error
```

**解決策:**
```bash
cd backend
uv sync
uv run pip install --upgrade pip
```

#### フロントエンド依存関係問題
```bash
Error: Cannot resolve module / Package not found
```

**解決策:**
```bash
cd frontend
npm install
npm audit fix
```

### Docker関連問題

#### Docker起動失敗
```bash
Error: Cannot connect to Docker daemon
```

**解決策:**
```bash
# Docker Desktop起動確認
open -a Docker

# Dockerサービス再起動
sudo systemctl restart docker  # Linux
brew services restart docker   # macOS Homebrew
```

#### コンテナビルド失敗
```bash
Error: failed to build image
```

**解決策:**
```bash
# キャッシュクリア
docker system prune -a

# 再ビルド
docker-compose -f docker-compose.dev.yml build --no-cache
```

## 🤖 ADK・エージェント関連の問題

### ADK初期化エラー
```python
Error: ADK initialization failed
```

**解決策:**
1. **環境変数確認**
   ```bash
   # .env.devファイル確認
   cat backend/.env.dev
   
   # 必須環境変数
   GOOGLE_API_KEY=your_api_key
   GOOGLE_PROJECT_ID=your_project_id
   ```

2. **API Key検証**
   ```bash
   # Google AI Studio確認
   # https://aistudio.google.com/app/apikey
   ```

### エージェント応答なし・異常応答

#### 症状: エージェントが応答しない
**解決策:**
```bash
# ログ確認
tail -f backend/logs/app.log

# エージェント初期化状況確認
grep "エージェント作成完了" backend/logs/app.log
```

#### 症状: transfer_to_agent()が動作しない
**解決策:**
```python
# AdkRoutingCoordinator確認
# backend/src/agents/adk_routing_coordinator.py

# 1. specialist_agentsが正しく登録されているか
# 2. coordinator_agentのsub_agentsにspecialist_agentsが含まれているか
# 3. 指示文に適切な転送例が記載されているか
```

## 🐛 バックエンドAPI問題

### 500 Internal Server Error

#### FastAPI起動エラー
```python
Error: Application startup failed
```

**解決策:**
```bash
# 詳細ログ確認
cd backend
uv run python -m src.main

# Composition Root初期化確認
grep "CompositionRoot" logs/app.log
```

#### DI注入エラー
```python
Error: Service 'xxx' not found
```

**解決策:**
```python
# backend/src/di_provider/composition_root.py 確認
# 1. _build_xxx_layer()でサービス登録されているか
# 2. ServiceRegistry.register()が呼ばれているか
# 3. 依存関係の循環参照がないか
```

### 認証・権限エラー

#### JWT Token Invalid
```json
{"detail": "Could not validate credentials"}
```

**解決策:**
```bash
# トークン再生成
# フロントエンドでログアウト→ログイン

# Auth0設定確認（本番環境）
# backend/.env.prodのAUTH0_xxx設定確認
```

## 🎨 フロントエンド問題

### Next.js起動エラー

#### Module Resolution Failed
```bash
Error: Module not found: Can't resolve '@/components/xxx'
```

**解決策:**
```bash
# tsconfig.jsonのpath aliases確認
cat frontend/tsconfig.json

# 期待される設定:
# "@/*": ["./src/*"]
```

#### Tailwind CSS未適用
```bash
Error: Class 'bg-blue-500' not working
```

**解決策:**
```bash
# Tailwind設定確認
cat frontend/tailwind.config.js

# PostCSS設定確認
cat frontend/postcss.config.js

# CSS再ビルド
cd frontend && npm run build
```

### API連携問題

#### CORS Error
```bash
Error: Access to fetch blocked by CORS policy
```

**解決策:**
```python
# backend/src/main.py CORS設定確認
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### API Endpoint Not Found (404)
```json
{"detail": "Not Found"}
```

**解決策:**
```python
# 1. ルーター登録確認 - main.py
app.include_router(router, prefix="/api/v1")

# 2. エンドポイント定義確認
# backend/src/presentation/api/routes/

# 3. API整合性チェック
./scripts/check-api.sh
```

## 🧪 テスト関連問題

### Pytest実行エラー

#### Import Error in Tests
```python
ModuleNotFoundError: No module named 'src'
```

**解決策:**
```bash
cd backend

# PYTHONPATH設定
export PYTHONPATH=$PYTHONPATH:$(pwd)

# または pytest設定ファイル確認
cat pytest.ini
# 期待値: pythonpath = src
```

#### Mock Object Errors
```python
Error: Mock object has no attribute 'xxx'
```

**解決策:**
```python
# tests/conftest.py でのMock設定確認
@pytest.fixture
def mock_composition_root():
    mock_root = Mock(spec=CompositionRoot)
    # spec指定でモックの属性を制限
    return mock_root
```

### フロントエンドテストエラー

#### Jest Configuration Error
```bash
Error: Jest configuration not found
```

**解決策:**
```bash
# Jest設定確認
cat frontend/jest.config.js

# Testing Library設定確認
cat frontend/setupTests.ts
```

## 🔧 開発ツール問題

### Linter・Formatter問題

#### Ruff設定エラー
```bash
Error: Ruff configuration invalid
```

**解決策:**
```bash
# pyproject.toml設定確認
cat backend/pyproject.toml

# Ruff手動実行
cd backend
uv run ruff check --fix
uv run ruff format
```

#### ESLint設定エラー
```bash
Error: ESLint configuration error
```

**解決策:**
```bash
# ESLint設定確認
cat frontend/.eslintrc.json

# 手動実行
cd frontend
npm run lint -- --fix
```

### IDE・VS Code問題

#### Python Path not found
```bash
Error: Python interpreter not found
```

**解決策:**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python"
}
```

#### TypeScript Path Mapping不動作
```bash
Error: Cannot find module '@/components/xxx'
```

**解決策:**
```json
// .vscode/settings.json
{
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

## 📊 パフォーマンス問題

### 応答速度遅延

#### Gemini API遅延
**症状:** エージェント応答に10秒以上かかる

**解決策:**
```python
# backend/src/infrastructure/adapters/gemini_image_analyzer.py
# モデル変更
model = "gemini-2.5-flash"  # より高速なモデル使用

# タイムアウト設定
generation_config = {
    "timeout": 30  # 30秒タイムアウト
}
```

#### メモリ使用量増大
**症状:** Docker container memory usage > 2GB

**解決策:**
```bash
# メモリ使用量確認
docker stats

# 不要なプロセス終了
docker-compose -f docker-compose.dev.yml restart
```

## 🔍 ログ・デバッグ手法

### 構造化ログの活用

#### 重要ログの場所
```bash
# アプリケーションログ
tail -f backend/logs/app.log

# エージェント専用ログ
grep "AgentManager\|AdkRoutingCoordinator" backend/logs/app.log

# API呼び出しログ
grep "POST\|GET" backend/logs/app.log
```

#### ログレベル変更
```python
# backend/src/config/settings.py
LOG_LEVEL = "DEBUG"  # より詳細なログ出力
```

### デバッグ用エンドポイント

#### ヘルスチェック
```bash
curl http://localhost:8080/health
# 期待値: {"status": "healthy"}
```

#### エージェント状態確認
```bash
curl http://localhost:8080/api/v1/agents/status
# エージェント初期化状況確認
```

## 🆘 緊急時対応

### 全サービス再起動
```bash
# 完全停止
./scripts/stop_dev.sh
docker-compose -f docker-compose.dev.yml down -v

# キャッシュクリア
docker system prune -f
npm cache clean --force

# 完全再起動
./scripts/start-dev.sh
```

### 設定リセット
```bash
# 環境設定リセット
cp backend/.env.example backend/.env.dev
cp frontend/.env.example frontend/.env.local

# 依存関係再インストール
cd backend && rm -rf .venv && uv sync
cd frontend && rm -rf node_modules && npm install
```

### バックアップからの復元
```bash
# 設定バックアップ（事前準備）
cp backend/.env.dev backend/.env.dev.backup
cp frontend/.env.local frontend/.env.local.backup

# 復元
cp backend/.env.dev.backup backend/.env.dev
cp frontend/.env.local.backup frontend/.env.local
```

## 📞 追加サポート

### チェックリスト実行
問題が解決しない場合、以下を順番に実行：

1. **基本確認**
   - [ ] Docker Desktop起動済み
   - [ ] 依存関係最新 (`uv sync`, `npm install`)
   - [ ] 環境変数設定済み (`.env.dev`, `.env.local`)
   - [ ] ポート競合なし (3000, 8080, 8001)

2. **ログ確認**
   - [ ] `backend/logs/app.log`でエラー確認
   - [ ] ブラウザDevToolsでフロントエンドエラー確認
   - [ ] `docker-compose logs`でコンテナログ確認

3. **設定確認**
   - [ ] [コーディング規約](../development/coding-standards.md)に準拠
   - [ ] [アーキテクチャ概要](../architecture/overview.md)の設計に準拠

### 最終手段
上記で解決しない場合は、プロジェクトチームに以下の情報と共に相談：

1. **エラーの詳細** (エラーメッセージ、スタックトレース)
2. **実行環境** (OS, Docker version, Node.js version)
3. **再現手順** (何をしたときにエラーが発生したか)
4. **ログファイル** (`backend/logs/app.log`の関連部分)

---

**💡 予防のコツ**: 定期的な`./scripts/check-api.sh`実行と、コミット前の品質チェック (`uv run ruff check`, `npm run lint`) で多くの問題を未然に防げます。