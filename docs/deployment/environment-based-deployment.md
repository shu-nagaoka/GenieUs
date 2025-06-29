# 環境変数ベースデプロイメントガイド

## 概要

GenieUsは環境変数ファイルを使用して、一貫性のあるデプロイメントを実現します。

## ディレクトリ構造

```
environments/
├── .env.local        # ローカル開発環境
├── .env.staging      # Staging環境  
└── .env.production   # Production環境
```

## 使用方法

### 1. ローカル開発

```bash
# 環境変数ファイルを使用してローカル開発環境を起動
./scripts/start-local-with-env.sh
```

### 2. Stagingデプロイ

```bash
# 環境変数ファイルを使用してStagingにデプロイ
./scripts/deploy-with-env.sh staging
```

### 3. Productionデプロイ

```bash
# 環境変数ファイルを使用してProductionにデプロイ
./scripts/deploy-with-env.sh production
```

### 4. 環境変数の更新

```bash
# 既存サービスの環境変数を更新
./scripts/update-service-env.sh staging frontend GOOGLE_CLIENT_ID=new-id
./scripts/update-service-env.sh production backend LOG_LEVEL=DEBUG
```

## 環境変数ファイルの設定

### 必須項目

各環境の`.env`ファイルで以下の項目を設定してください：

1. **GCP設定**
   - `GCP_PROJECT_ID`: GCPプロジェクトID
   - `GCP_REGION`: デプロイリージョン

2. **OAuth設定**（認証を使用する場合）
   - `GOOGLE_CLIENT_ID`: Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret
   - `NEXTAUTH_SECRET`: NextAuth.jsシークレット

3. **API Keys**
   - `GOOGLE_API_KEY`: Gemini API Key

### 動的に設定される項目

以下の項目はデプロイ時に自動的に設定されます：

- `NEXT_PUBLIC_API_BASE_URL`: バックエンドURL
- `NEXTAUTH_URL`: フロントエンドURL
- `CORS_ORIGINS`: フロントエンドURL

## OAuth設定手順

### ローカル開発用

1. Google Cloud Console > APIとサービス > 認証情報
2. OAuth 2.0 クライアントIDを作成
3. 承認済みリダイレクトURIに追加:
   ```
   http://localhost:3000/api/auth/callback/google
   ```
4. `environments/.env.local`を更新

### Staging/Production用

1. デプロイ完了後、表示されるURLを確認
2. Google Cloud Consoleで承認済みリダイレクトURIに追加:
   ```
   https://[your-frontend-url]/api/auth/callback/google
   ```
3. 環境変数を更新:
   ```bash
   ./scripts/update-service-env.sh staging frontend \
     GOOGLE_CLIENT_ID=your-client-id \
     GOOGLE_CLIENT_SECRET=your-secret
   ```

## セキュリティ注意事項

1. **環境変数ファイルはGitにコミットしない**
   - `.gitignore`に追加済み
   - サンプルファイルを提供

2. **本番環境のシークレット**
   - Google Secret Managerの使用を推奨
   - 環境変数ファイルには開発用の値のみ記載

## トラブルシューティング

### OAuth認証エラー

- リダイレクトURIが正しく設定されているか確認
- NEXTAUTH_URLが実際のフロントエンドURLと一致しているか確認

### CORS エラー

- バックエンドのCORS_ORIGINSが更新されているか確認
- デプロイ後に自動更新されない場合は手動で更新:
  ```bash
  ./scripts/update-service-env.sh staging backend \
    CORS_ORIGINS=https://your-frontend-url
  ```