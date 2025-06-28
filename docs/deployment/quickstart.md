# 🚀 GenieUs Cloud Run デプロイメント クイックスタート

## 前提条件確認

### 1. 必要なツール
```bash
# gcloud CLI インストール確認
gcloud --version

# Docker インストール確認  
docker --version

# Node.js & npm 確認
node --version
npm --version
```

### 2. GCP プロジェクト準備
```bash
# プロジェクト作成
gcloud projects create your-project-id

# プロジェクト選択
gcloud config set project your-project-id

# 課金設定確認
gcloud billing projects describe your-project-id
```

## 🔧 設定手順

### Step 1: 環境変数設定

**詳細な環境変数設定については [overview.md#環境変数設定](overview.md#環境変数設定) を参照してください。**

最小設定での動作確認:
```bash
# 必須項目のみ
export GCP_PROJECT_ID="your-actual-project-id"
export GOOGLE_API_KEY="your-gemini-api-key"
```

### Step 2: Google OAuth設定

**詳細なOAuth設定については [infrastructure.md#認証設定](infrastructure.md#認証設定) を参照してください。**

基本設定:
1. Google Cloud Console → API & Services → Credentials
2. OAuth 2.0 Client ID を作成
3. リダイレクトURI を設定（詳細は上記リンク参照）

### Step 3: GCP 環境変数設定
```bash
export GCP_PROJECT_ID="your-actual-project-id"
export GCP_REGION="asia-northeast1"
```

## 🚀 デプロイ実行

### ワンコマンドデプロイ（推奨）
```bash
# ステージング環境
./scripts/deploy-cloud-run.sh staging

# 本番環境
./scripts/deploy-cloud-run.sh production
```

### 段階的デプロイ（デバッグ時）

#### 1. バックエンドのみ
```bash
cd backend
gcloud run deploy genius-backend-production \\
  --source . \\
  --platform managed \\
  --region asia-northeast1 \\
  --allow-unauthenticated \\
  --env-vars-file .env.production
```

#### 2. フロントエンドのみ
```bash
cd frontend
gcloud run deploy genius-frontend-production \\
  --source . \\
  --platform managed \\
  --region asia-northeast1 \\
  --allow-unauthenticated \\
  --env-vars-file .env.production
```

## 📋 デプロイ後の確認

### 1. ヘルスチェック
```bash
# バックエンドAPI
curl https://genius-backend-production-xxx.run.app/health

# フロントエンド
curl https://genius-frontend-production-xxx.run.app
```

### 2. ログ確認
```bash
# バックエンドログ
gcloud run services logs tail genius-backend-production \\
  --region=asia-northeast1

# フロントエンドログ  
gcloud run services logs tail genius-frontend-production \\
  --region=asia-northeast1
```

### 3. 動作テスト
1. フロントエンドURLにアクセス
2. Google認証でログイン
3. チャット機能をテスト
4. エージェント機能をテスト

## 🐛 トラブルシューティング

### よくある問題

#### 1. 認証エラー
```bash
# OAuth設定確認
echo $GOOGLE_CLIENT_ID
echo $NEXTAUTH_URL

# リダイレクトURI確認
# 実際のデプロイURLと設定が一致しているか
```

#### 2. APIキーエラー
```bash
# Gemini API有効化確認
gcloud services list --enabled | grep aiplatform

# APIキー権限確認
```

#### 3. CORS エラー
```bash
# CORS_ORIGINS設定確認（backend/.env.production）
# フロントエンドURLが正しく設定されているか
```

## 📊 運用監視

### モニタリング設定
```bash
# エラー率アラート設定
gcloud alpha monitoring policies create \\
  --policy-from-file=monitoring/error-rate-alert.yaml

# レスポンス時間監視
gcloud alpha monitoring policies create \\
  --policy-from-file=monitoring/response-time-alert.yaml
```

### コスト監視
- 月額想定: $22-48
- Cloud Run使用料: $15-25
- Vertex AI使用料: $5-20  
- Storage使用料: $2-3

## 🎉 デプロイ成功後のURL

デプロイ成功後、以下のURLでアクセス可能:

- **フロントエンド**: https://genius-frontend-production-xxx.run.app
- **バックエンドAPI**: https://genius-backend-production-xxx.run.app
- **API仕様書**: https://genius-backend-production-xxx.run.app/docs

## 次のステップ

1. **カスタムドメイン設定** (オプション)
2. **CDN設定** (Cloud CDN)
3. **バックアップ設定** (Cloud SQL移行時)
4. **監視ダッシュボード作成**