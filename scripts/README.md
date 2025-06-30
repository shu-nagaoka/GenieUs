# GenieUs Scripts Directory

整理されたスクリプト集 - 特定用途向けツール

## 📁 スクリプト分類

### 🚀 開発環境管理
- **`start-dev.sh`** - 統合開発環境起動（フロントエンド+バックエンド）
  - ポート: フロントエンド 3000、バックエンド 8080
  - 環境ファイル: `.env.dev`

### 🔗 API整合性管理
- **`check-api-consistency.js`** - フロントエンド⇔バックエンドAPI整合性チェック
- **`check-api.sh`** - API整合性チェック実行スクリプト
- **`update-api-mapping.js`** - API URLマッピング自動更新
- **`update-api.sh`** - APIマッピング更新実行スクリプト

### 📚 ドキュメント管理
- **`generate-docs-navigation.js`** - ドキュメントナビゲーション自動生成
- **`regenerate-index-html.js`** - ドキュメントインデックス再生成
- **`watch-docs.js`** - ドキュメント変更監視・自動更新

### ☁️ GCP管理
- **`setup-gcp-cicd.sh`** - GCP CI/CD環境自動構築
- **`setup-github-secrets.sh`** - GitHub Secrets自動設定
- **`check-staging-env.sh`** - ステージング環境確認
- **`cleanup-old-revisions.sh`** - 古いCloud Runリビジョンクリーンアップ

### 🔧 開発ツール
- **`claude-code-check.py`** - Claude Code支援チェックツール
- **`package.json`** - Node.js依存関係管理

## 🚫 削除された機能

以下の機能は削除され、新しいシステムに置き換わりました：

### デプロイメント → `deployment/` に移行
- ❌ `deploy-cloud-run.sh`
- ❌ `deploy-cloudbuild.sh`
- ❌ `deploy-combined.sh`
- ❌ `deploy-staging.sh`
- ❌ `deploy-with-env.sh`
- ❌ `simple-deploy.sh`
- ❌ `setup-deploy-env.sh`

### Docker関連 → Cloud Runに統一
- ❌ `run.sh`
- ❌ `start.sh`
- ❌ `stop.sh`
- ❌ `start_dev.sh`
- ❌ `stop_dev.sh`

### ADK Web UI → entrypoint.shに統合
- ❌ `start-adk.sh`

### 環境管理 → 統合済み
- ❌ `migrate-env.sh`
- ❌ `load-env.sh`
- ❌ `start-local-with-env.sh`
- ❌ `update-service-env.sh`

## 📋 使用方法

### 日常開発
```bash
# 開発環境起動
./scripts/start-dev.sh

# API整合性チェック
./scripts/check-api.sh

# ドキュメント更新
./scripts/generate-docs-navigation.js
```

### デプロイメント
```bash
# 新しいデプロイメントシステムを使用
./deployment/cloud-build/staging.sh
./deployment/gcloud-direct/production.sh

# または統合メニューから
./entrypoint.sh  # Option 20-23
```

### GCP管理
```bash
# CI/CD環境構築
./scripts/setup-gcp-cicd.sh

# ステージング環境確認
./scripts/check-staging-env.sh
```

## 🎯 entrypoint.sh統合

多くの機能は統合エントリーポイントから利用可能：

```bash
./entrypoint.sh
```

- **Option 1**: 開発環境起動 (start-dev.sh)
- **Option 14**: API整合性チェック (check-api.sh)
- **Option 15**: APIマッピング更新 (update-api.sh)
- **Option 30**: GCP CI/CD構築 (setup-gcp-cicd.sh)

## 📈 整理の効果

| 項目 | 整理前 | 整理後 | 効果 |
|------|--------|--------|------|
| ファイル数 | 32個 | 15個 | 53%削減 |
| 重複機能 | 多数 | なし | 保守性向上 |
| 用途不明 | あり | なし | 理解容易性向上 |
| 機能分散 | 分散 | 統合 | 操作性向上 |

---

**💡 原則**: 特定用途のツールのみ`scripts/`に配置。汎用機能は`entrypoint.sh`または`deployment/`から利用。