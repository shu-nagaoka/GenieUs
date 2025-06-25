# Cloud Runインフラストラクチャ設計

GenieUsアプリケーションのGoogle Cloud Platform Cloud Runデプロイメント設計

## 📋 概要

### 目標
- フロントエンド（Next.js）とバックエンド（FastAPI）のCloud Runデプロイ
- Google認証統合による セキュアな認証基盤
- スケーラブルで本番運用可能なインフラ構築
- CI/CDパイプライン整備

### アーキテクチャ原則
1. **マイクロサービス指向**: フロントエンド・バックエンド分離
2. **サーバーレス優先**: Cloud Runによる自動スケーリング
3. **セキュリティファースト**: Google認証・IAM・VPC統合
4. **可観測性**: ログ・メトリクス・トレーシング完備

## 🏗️ システム構成

### 高レベルアーキテクチャ
```
Internet
    │
    ├── Cloud Load Balancer (Frontend)
    │   └── Cloud Run (Next.js Frontend)
    │
    └── Cloud Load Balancer (API)
        └── Cloud Run (FastAPI Backend)
            ├── Cloud Storage (Files)
            ├── Vertex AI (Gemini)
            └── Cloud Logging
```

### コンポーネント詳細

#### 1. フロントエンド (Cloud Run Service)
```
Container: genius-frontend
├── Image: gcr.io/{PROJECT_ID}/genius-frontend:latest
├── Port: 3000 (Next.js)
├── Environment: production
├── Auth: Google OAuth 2.0
└── CDN: Cloud CDN (静的アセット)
```

#### 2. バックエンド (Cloud Run Service)
```
Container: genius-backend
├── Image: gcr.io/{PROJECT_ID}/genius-backend:latest
├── Port: 8000 (FastAPI)
├── Environment: production
├── ADK: Agent Development Kit
└── APIs: Vertex AI Gemini
```

#### 3. 共有リソース
```
Storage & AI:
├── Cloud Storage (画像・ファイル保存)
├── Vertex AI (Gemini 2.5 Flash)
├── Cloud Logging (統合ログ)
└── Cloud Monitoring (メトリクス)

Security:
├── Identity and Access Management (IAM)
├── Google OAuth 2.0
├── Cloud Armor (DDoS保護)
└── VPC (ネットワーク分離)
```

## 🔐 認証・認可設計

### シンプル認証アーキテクチャ (推奨)

GenieUsでは**ユーザビリティ重視**のシンプル認証方式を採用します。

#### 1. 認証設計原則
```
✅ Google OAuth 2.0 のみ使用 (JWT発行不要)
✅ フロントエンド: NextAuth.js による認証
✅ バックエンド: Google IDトークン検証のみ
✅ Cloud Run: パブリックアクセス (--allow-unauthenticated)
✅ セキュリティ: Google OAuth + HTTPS で十分
```

#### 2. 認証フロー (簡略化版)
```
1. ユーザー → Google OAuth login (NextAuth.js)
2. Google → ID Token 発行
3. Frontend → Backend API (Google ID Token付き)
4. Backend → Google ID Token 検証
5. Backend → ユーザー識別 (email) → Response
```

#### 3. 実装詳細

##### フロントエンド認証 (NextAuth.js)
```typescript
// 既存のNextAuth設定使用
import { getSession } from 'next-auth/react'

// API呼び出し時
const session = await getSession()
const response = await fetch('/api/backend', {
  headers: { 
    'Authorization': `Bearer ${session?.idToken}` // Google IDトークンをそのまま使用
  }
})
```

##### バックエンド認証 (Google ID Token検証)
```python
# シンプルなGoogle認証のみ
from google.auth.transport import requests
from google.oauth2 import id_token
from fastapi import HTTPException, Depends, Header

async def verify_google_token(authorization: str = Header(None)):
    """Google ID Tokenを検証してユーザー情報を返す"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "認証が必要です")
    
    token = authorization.split(' ')[1]
    try:
        # Google ID Token検証 (JWTライブラリ不要)
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # ユーザー情報返却
        return {
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo['picture']
        }
    except ValueError as e:
        raise HTTPException(401, f"無効なトークンです: {str(e)}")

# API使用例
@app.post("/api/chat")
async def chat(request: ChatRequest, user = Depends(verify_google_token)):
    # user['email'] でユーザー識別
    return await process_chat(request.message, user['email'])
```

#### 4. Cloud Run設定
```bash
# パブリックアクセス設定 (認証はアプリレベルで実装)
gcloud run deploy genius-frontend \
  --allow-unauthenticated \
  --region asia-northeast1

gcloud run deploy genius-backend \
  --allow-unauthenticated \
  --region asia-northeast1

# セキュリティはGoogle OAuth + HTTPS で確保
```

#### 5. 環境変数設定
```env
# フロントエンド (.env.production)
NEXTAUTH_URL=https://genius-frontend-xxx.run.app
NEXTAUTH_SECRET=your-nextauth-secret
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxx
BACKEND_API_URL=https://genius-backend-xxx.run.app

# バックエンド (.env.production)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
ALLOWED_ORIGINS=https://genius-frontend-xxx.run.app
```

#### 6. セキュリティ考慮事項

##### ✅ 実装するセキュリティ
- **HTTPS通信**: Cloud Runで自動提供
- **CORS設定**: 特定フロントエンドのみ許可
- **Google OAuth**: Googleによる認証・認可
- **トークン有効期限**: Google IDトークンの自動期限管理

##### ❌ 不要な複雑化
- **独自JWT発行**: Google IDトークンで十分
- **Cloud Run認証**: パブリックアクセスでシンプル化
- **複雑な認可制御**: 基本的なユーザー識別のみ

#### 7. 開発・運用メリット
```
👍 開発効率:
  - 認証ロジックがシンプル
  - デバッグが容易
  - テストが簡単

👍 運用面:
  - Google認証の信頼性
  - セッション管理不要
  - スケーラビリティ確保

👍 ユーザー体験:
  - スムーズなログイン
  - セッション切れの心配なし
  - レスポンシブ対応
```

### セキュリティ強化オプション (将来拡張)

必要に応じて段階的にセキュリティを強化:

#### Phase 2: 追加セキュリティ
```python
# レート制限
from slowapi import Limiter

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    pass

# IP制限
ALLOWED_IPS = ["frontend-ip-range"]
```

#### Phase 3: 高度な認証
```bash
# Cloud Runサービス間認証 (内部API)
gcloud run deploy internal-service \
  --no-allow-unauthenticated
```

## 🚀 デプロイメント戦略

### 1. Docker化

#### フロントエンド Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

#### バックエンド Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash genius
USER genius

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Cloud Run設定

#### サービス設定例
```yaml
# cloud-run-frontend.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: genius-frontend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/{PROJECT_ID}/genius-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: GOOGLE_CLIENT_ID
          value: "{GOOGLE_CLIENT_ID}"
        - name: NEXTAUTH_URL
          value: "https://genius-frontend-{HASH}.run.app"
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "0.5"
            memory: "512Mi"
```

### 3. デプロイスクリプト

#### 自動デプロイ用スクリプト
```bash
#!/bin/bash
# scripts/deploy-cloud-run.sh

set -e

PROJECT_ID="your-project-id"
REGION="asia-northeast1"

echo "🚀 Starting Cloud Run deployment..."

# Build and push frontend
echo "📦 Building frontend..."
cd frontend
docker build -t gcr.io/${PROJECT_ID}/genius-frontend:latest .
docker push gcr.io/${PROJECT_ID}/genius-frontend:latest

# Deploy frontend
echo "🌐 Deploying frontend..."
gcloud run deploy genius-frontend \
  --image gcr.io/${PROJECT_ID}/genius-frontend:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10

# Build and push backend
echo "📦 Building backend..."
cd ../backend
docker build -t gcr.io/${PROJECT_ID}/genius-backend:latest .
docker push gcr.io/${PROJECT_ID}/genius-backend:latest

# Deploy backend
echo "⚙️ Deploying backend..."
gcloud run deploy genius-backend \
  --image gcr.io/${PROJECT_ID}/genius-backend:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 5

echo "✅ Deployment completed!"
```

## 🔧 環境設定

### 必要なGCPサービス有効化
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### IAMロール設定
```bash
# Cloud Run Service Account
gcloud iam service-accounts create genius-backend-sa \
    --display-name="Genius Backend Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:genius-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:genius-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

## 📊 可観測性

### ログ設定
```python
# Structured logging for Cloud Logging
import google.cloud.logging

def setup_cloud_logging():
    client = google.cloud.logging.Client()
    client.setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    return logger
```

### メトリクス監視
- **Frontend**: レスポンス時間、エラー率、リクエスト数
- **Backend**: API応答時間、Gemini API使用量、エラー率
- **Infrastructure**: CPU使用率、メモリ使用率、スケーリング頻度

## 💰 コスト最適化

### リソース最適化
1. **Auto-scaling**: 最小1インスタンス、最大10インスタンス
2. **CPU throttling**: 無効化（レスポンス重視）
3. **Memory allocation**: Frontend 512MB、Backend 1GB
4. **Regional deployment**: asia-northeast1（東京リージョン）

### 予想コスト（月額）
```
Cloud Run Frontend:
- 100,000 requests/month: $5-10

Cloud Run Backend:
- 50,000 requests/month: $10-15

Vertex AI (Gemini):
- 100,000 tokens/month: $5-20

Cloud Storage:
- 10GB storage: $2-3

Total: $22-48/month (想定)
```

## 🔄 CI/CD設計

### GitHub Actions設定例
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - id: 'auth'
      uses: 'google-github-actions/auth@v1'
      with:
        credentials_json: '${{ secrets.GCP_SA_KEY }}'
    
    - name: 'Set up Cloud SDK'
      uses: 'google-github-actions/setup-gcloud@v1'
    
    - name: 'Deploy Frontend'
      run: |
        cd frontend
        gcloud run deploy genius-frontend \
          --source . \
          --region asia-northeast1
    
    - name: 'Deploy Backend'
      run: |
        cd backend
        gcloud run deploy genius-backend \
          --source . \
          --region asia-northeast1
```

## 📅 実装ロードマップ

### Phase 1: 基盤構築 (1-2週間)
- [ ] Docker化完了
- [ ] 基本Cloud Runデプロイ
- [ ] Google認証統合

### Phase 2: 本番化 (1週間)
- [ ] セキュリティ設定
- [ ] 監視・ログ設定
- [ ] CI/CDパイプライン

### Phase 3: 最適化 (継続)
- [ ] パフォーマンス調整
- [ ] コスト最適化
- [ ] スケーリング調整

## 🚨 セキュリティ考慮事項

### 重要な設定
1. **環境変数**: Secret Managerで管理
2. **CORS設定**: 適切なオリジン制限
3. **Rate limiting**: Cloud Armor設定
4. **VPC設定**: 内部通信のセキュア化
5. **SSL/TLS**: 自動HTTPS化

---

この設計に基づいて、順次実装を進めていきます。まずはDocker化から始めて、段階的にCloud Runデプロイを実現しましょう。