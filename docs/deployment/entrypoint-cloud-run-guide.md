# 🚀 GenieUs Cloud Run 統合デプロイメントガイド

エントリーポイント `./entrypoint.sh` からCloud Runデプロイメントを統合管理するためのガイドです。

## 📋 クイックスタート

### 1. エントリーポイント起動

```bash
# プロジェクトルートから実行
./entrypoint.sh
```

### 2. Cloud Run メニュー使用

エントリーポイントメニューから以下のオプションが利用可能:

```
☁️  Cloud Run デプロイメント
  12) Cloud Run ステージング デプロイ
  13) Cloud Run 本番 デプロイ
  14) Cloud Run サービス状態確認
  15) Cloud Run ログ確認
  16) Cloud Run 設定・環境確認
```

## 🔧 事前設定

### 必要な環境変数

```bash
# ~/.bashrc または ~/.zshrc に追加
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="asia-northeast1"
export GCP_SERVICE_ACCOUNT="genius-backend-sa"
```

### 認証設定

```bash
# Google Cloud認証
gcloud auth login
gcloud config set project your-project-id

# Docker認証
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
```

## 📱 使用方法

### デプロイメント操作

#### 🟡 ステージング環境デプロイ (オプション 12)
```bash
./entrypoint.sh
# メニューで「12」を選択
```

- **自動実行内容**:
  - 前提条件チェック
  - ステージング環境へのデプロイ
  - ヘルスチェック

#### 🔴 本番環境デプロイ (オプション 13)
```bash
./entrypoint.sh
# メニューで「13」を選択
# 確認のため「production」と入力
```

- **安全機能**:
  - 2重確認（「production」入力必須）
  - 前提条件チェック
  - 詳細ログ出力

### 監視・運用操作

#### 📊 サービス状態確認 (オプション 14)
```bash
./entrypoint.sh
# メニューで「14」を選択
```

- **確認内容**:
  - 全サービス一覧表示
  - 個別サービス詳細
  - URL・ステータス確認

#### 📝 ログ確認 (オプション 15)
```bash
./entrypoint.sh
# メニューで「15」を選択
```

- **ログタイプ**:
  - リアルタイムログ
  - 最新ログ（50行）
  - エラーログのみ

#### ⚙️ 環境設定確認 (オプション 16)
```bash
./entrypoint.sh
# メニューで「16」を選択
```

- **チェック項目**:
  - 環境変数設定
  - gcloud CLI状態
  - Docker状態
  - 必要ファイル存在確認

## 🎯 典型的なワークフロー

### 初回デプロイ

1. **環境設定確認**
   ```bash
   ./entrypoint.sh → 16 (Cloud Run 設定・環境確認)
   ```

2. **ステージング デプロイ**
   ```bash
   ./entrypoint.sh → 12 (Cloud Run ステージング デプロイ)
   ```

3. **動作確認**
   ```bash
   ./entrypoint.sh → 14 (Cloud Run サービス状態確認)
   ```

4. **本番デプロイ**
   ```bash
   ./entrypoint.sh → 13 (Cloud Run 本番 デプロイ)
   ```

### 日常運用

1. **ログ監視**
   ```bash
   ./entrypoint.sh → 15 (Cloud Run ログ確認)
   ```

2. **サービス状態確認**
   ```bash
   ./entrypoint.sh → 14 (Cloud Run サービス状態確認)
   ```

3. **更新デプロイ**
   ```bash
   ./entrypoint.sh → 12/13 (デプロイ)
   ```

## 🔍 トラブルシューティング

### よくあるエラーと対処法

#### ❌ "gcloud CLIがインストールされていません"
```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
```

#### ❌ "GCPにログインしていません"
```bash
gcloud auth login
gcloud config set project your-project-id
```

#### ❌ "Dockerが起動していません"
```bash
# Docker Desktopを起動
open -a Docker

# またはコマンドライン
sudo systemctl start docker  # Linux
```

#### ❌ "GCP_PROJECT_ID環境変数が未設定"
```bash
export GCP_PROJECT_ID="your-project-id"
# または ~/.bashrc に永続化
echo 'export GCP_PROJECT_ID="your-project-id"' >> ~/.bashrc
```

### デプロイ失敗時の対処

1. **環境設定確認**
   ```bash
   ./entrypoint.sh → 16
   ```

2. **ログ確認**
   ```bash
   ./entrypoint.sh → 15
   ```

3. **手動デプロイ実行**
   ```bash
   ./scripts/deploy-cloud-run.sh staging --debug
   ```

## 🔄 CI/CD連携

エントリーポイントからのデプロイとGitHub Actionsの使い分け:

### 手動デプロイ（エントリーポイント）
- **用途**: 開発・テスト・緊急デプロイ
- **利点**: インタラクティブ・即座実行
- **実行**: `./entrypoint.sh → 12/13`

### 自動デプロイ（GitHub Actions）
- **用途**: 本番リリース・定期デプロイ
- **利点**: 履歴管理・品質ゲート
- **実行**: `git push origin main`

## 📋 チェックリスト

### デプロイ前チェック

- [ ] GCP_PROJECT_ID設定済み
- [ ] gcloud認証済み
- [ ] Docker起動済み
- [ ] 環境ファイル作成済み
- [ ] Google OAuth設定済み

### デプロイ後チェック

- [ ] サービス状態確認
- [ ] URL動作確認
- [ ] ログエラー確認
- [ ] 環境変数確認

## 🆘 緊急時対応

### サービス停止
```bash
# 緊急停止
gcloud run services update genius-backend-production \
  --region=asia-northeast1 \
  --min-instances=0 \
  --max-instances=0
```

### ロールバック
```bash
# 前バージョンに戻す
gcloud run services update genius-backend-production \
  --region=asia-northeast1 \
  --image=gcr.io/PROJECT_ID/genius-backend:previous-tag
```

---

## 🔗 関連ドキュメント

- [Cloud Run インフラ設計](docs/architecture/cloud-infrastructure.md)
- [詳細デプロイガイド](docs/DEPLOYMENT.md)
- [GitHub Actions設定](.github/workflows/deploy-cloud-run.yml)

---

これで `./entrypoint.sh` から完全にCloud Runデプロイメントを管理できます！🎉