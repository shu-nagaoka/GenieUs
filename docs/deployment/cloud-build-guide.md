# 🏗️ Cloud Build統合デプロイガイド

## 📋 概要

GenieUsアプリケーションをローカルDockerを使わずに、Cloud Buildで完全にクラウド上でビルド・デプロイできるシステムです。

## 🎯 Cloud Buildの利点

### ✅ メリット
- **ローカルDockerが不要** - マシンリソースを節約
- **並行ビルド** - フロント・バックエンドを同時処理
- **クラウドスケール** - 高速・安定ビルド
- **統一環境** - 開発・本番環境の一致
- **セキュリティ** - IAM統合でセキュア

### 🚀 従来型との比較

| 項目 | Cloud Build | 従来型 |
|------|------------|--------|
| **ローカルDocker** | ❌ 不要 | ✅ 必要 |
| **ビルド速度** | 🚀 高速 | 🐌 ローカル依存 |
| **リソース使用** | ☁️ クラウド | 💻 ローカル |
| **並行処理** | ✅ 可能 | ❌ 制限あり |
| **環境統一** | ✅ 完全 | ⚠️ 差異あり |

## 🎮 使用方法

### 1. entrypoint.shからの実行（推奨）

```bash
# 統一メニューから選択
./entrypoint.sh

# メニューで以下を選択:
# 14) 🏗️ Cloud Build デプロイ (ステージング)
# 15) 🏗️ Cloud Build デプロイ (本番)
```

### 2. 直接スクリプト実行

```bash
# ステージング環境
./scripts/deploy-cloudbuild.sh staging your-project-id

# 本番環境
./scripts/deploy-cloudbuild.sh production your-project-id

# 環境変数経由
export GCP_PROJECT_ID="your-project-id"
./scripts/deploy-cloudbuild.sh staging
```

## ⚙️ 設定方法

### 必須環境変数

```bash
# GCPプロジェクト（必須）
export GCP_PROJECT_ID="your-project-id"

# オプション設定
export GCP_REGION="asia-northeast1"
export GOOGLE_API_KEY="your-gemini-api-key"
export GOOGLE_AIPSK="your-adk-api-key"
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-your-secret"
export NEXTAUTH_SECRET="your-nextauth-secret"
export ROUTING_STRATEGY="enhanced"
export LOG_LEVEL="INFO"
export BUILD_TIMEOUT="20m"
```

## 🏗️ Cloud Build処理フロー

### ステップ1: 環境設定
- プロジェクト設定
- 環境変数確認

### ステップ2: API有効化
- Cloud Run API
- Cloud Build API
- Container Registry API
- Vertex AI API

### ステップ3: IAM設定
- サービスアカウント作成
- 必要権限付与

### ステップ4: 並行ビルド・デプロイ
- **バックエンド**: FastAPI + Python 3.12
- **フロントエンド**: Next.js + Node.js 20
- 依存関係解決とURL連携

### ステップ5: ヘルスチェック
- 自動動作確認
- URL表示

## 📊 デプロイ結果例

```
🏗️ ========================================
   GenieUs Cloud Build Deployment
   Environment: staging
   Project: my-project-2024
   Region: asia-northeast1
======================================== 🏗️

[BUILD] Cloud Buildでデプロイを開始...
[BUILD] ビルドログはCloud ConsoleのCloud Buildセクションで確認できます

[SUCCESS] Cloud Buildが完了しました
[INFO] Build ID: 12345678-1234-1234-1234-123456789abc

🎉 Cloud Buildデプロイ完了!

📋 ========================================
   Deployment Summary
======================================== 📋
Environment: staging
Project: my-project-2024
Region: asia-northeast1
Build Method: Cloud Build (No Local Docker)

🌐 URLs:
  Frontend:  https://genius-frontend-staging-abc123.a.run.app
  Backend:   https://genius-backend-staging-def456.a.run.app
  API Docs:  https://genius-backend-staging-def456.a.run.app/docs
```

## 🔧 トラブルシューティング

### よくある問題

#### 1. プロジェクトID未設定
```bash
[ERROR] プロジェクトIDが設定されていません
# 解決: export GCP_PROJECT_ID="your-project-id"
```

#### 2. gcloud認証エラー
```bash
[ERROR] GCPにログインしていません
# 解決: gcloud auth login
```

#### 3. API未有効化
```bash
[ERROR] Cloud Build APIが無効です
# 解決: Cloud Buildが自動で有効化（通常は自動解決）
```

#### 4. ビルドタイムアウト
```bash
# 解決: BUILD_TIMEOUTを延長
export BUILD_TIMEOUT="30m"
```

### ログ確認方法

```bash
# Cloud Buildログ確認
gcloud builds list --limit=10

# 特定ビルドの詳細
gcloud builds log BUILD_ID

# Web UIでの確認
https://console.cloud.google.com/cloud-build/builds?project=YOUR_PROJECT_ID
```

## 🎛️ 高度な設定

### カスタム置換変数

`cloudbuild.yaml`の置換変数をカスタマイズ可能：

```yaml
substitutions:
  _GCP_PROJECT_ID: 'your-project-id'
  _ENVIRONMENT: 'staging'
  _GCP_REGION: 'asia-northeast1'
  _ROUTING_STRATEGY: 'enhanced'
  _LOG_LEVEL: 'INFO'
```

### パフォーマンス調整

```bash
# マシンタイプ変更（cloudbuild.yamlで設定）
machineType: 'E2_HIGHCPU_8'  # デフォルト
machineType: 'E2_HIGHCPU_32' # 高速化

# タイムアウト調整
timeout: 1200s  # 20分（デフォルト）
timeout: 1800s  # 30分
```

## 📚 関連ファイル

- **`cloudbuild.yaml`** - Cloud Build設定
- **`scripts/deploy-cloudbuild.sh`** - デプロイスクリプト
- **`entrypoint.sh`** - 統一インターフェース
- **`backend/.env.production`** - バックエンド環境設定
- **`frontend/.env.production`** - フロントエンド環境設定

## 💡 ベストプラクティス

1. **環境変数設定** - デプロイ前に必須変数を設定
2. **段階的デプロイ** - staging → production の順番
3. **ログ監視** - デプロイ後の動作確認
4. **設定管理** - 環境別設定ファイルの適切な管理

## 🔗 参考リンク

- [Google Cloud Build](https://cloud.google.com/build)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GenieUs Architecture Guide](docs/architecture/overview.md)