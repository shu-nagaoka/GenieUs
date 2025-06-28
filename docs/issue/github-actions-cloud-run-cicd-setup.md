# Issue: GitHub Actions CI/CD → GCP Cloud Run 自動デプロイパイプライン構築

**Issue ID**: INFRA-001  
**作成日**: 2025-06-28  
**優先度**: High  
**カテゴリ**: インフラ・CI/CD・DevOps  

## 📋 概要

mainブランチへのPRマージ時に、GitHub ActionsでCI/CDパイプラインが自動実行され、GCP Cloud Runへフロントエンド・バックエンドを自動デプロイする仕組みを完全構築する。

**現状**: ワークフローファイルは実装済み、GCP設定・認証が未完了  
**目標**: 完全自動化されたプロダクション対応CI/CDパイプライン

## 🎯 目的

- **開発効率化**: mainブランチマージ → 即座に本番反映
- **デプロイ品質向上**: 自動テスト → ビルド → デプロイの確実な実行
- **運用負荷軽減**: 手動デプロイ作業の完全撤廃
- **環境統一**: staging/production環境の自動管理

## 🔍 現状分析

### ✅ 実装済み項目

**GitHub Actions ワークフロー** (`.github/workflows/deploy-cloud-run.yml`)
- mainブランチマージ時の自動トリガー
- PR時の自動テスト実行
- 環境分離（main=production, develop=staging）
- Frontend/Backend並行デプロイ
- ヘルスチェック機能

**Docker設定**
- `backend/Dockerfile`: Python 3.12.8 + uv + FastAPI最適化
- `frontend/Dockerfile`: Node.js 20 + Next.js standalone
- `Dockerfile.combined`: Nginx + Supervisor統合版

**Cloud Build設定** (`cloudbuild.yaml`)
- GCP特化の完全自動化パイプライン
- IAM自動設定
- 並行ビルド対応

### ❌ 未対応項目

**GitHub Secrets設定**
```yaml
必要なSecrets:
- GCP_PROJECT_ID: 未設定
- GCP_SA_KEY: 未設定  
- NEXTAUTH_SECRET: 未設定
- GOOGLE_CLIENT_ID: 未設定
- GOOGLE_CLIENT_SECRET: 未設定
```

**GCP環境準備**
- プロジェクト作成・選択
- Cloud Run API有効化
- Artifact Registry設定
- サービスアカウント作成

**初回デプロイ**
- Cloud Runサービス初回作成
- 動作検証・E2Eテスト

## 🚀 実装プラン

### Phase 1: GCP環境構築
**実装内容**:
1. **GCPプロジェクト準備**
   - 新規プロジェクト作成または既存プロジェクト選択
   - 課金アカウント紐付け確認
   - プロジェクトID確定

2. **GCP API有効化**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   ```

3. **サービスアカウント作成**
   ```bash
   # バックエンド用サービスアカウント
   gcloud iam service-accounts create genius-backend-sa \
     --display-name="Genius Backend Service Account"
   
   # CI/CD用サービスアカウント  
   gcloud iam service-accounts create genius-cicd-sa \
     --display-name="Genius CI/CD Service Account"
   ```

4. **IAM権限設定**
   ```bash
   # バックエンドサービス用権限
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:genius-backend-sa@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   
   # CI/CD用権限
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:genius-cicd-sa@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   ```

**期待結果**: GCP環境の完全準備完了

### Phase 2: GitHub Secrets設定
**実装内容**:
1. **GCPサービスアカウントキー生成**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=genius-cicd-sa@PROJECT_ID.iam.gserviceaccount.com
   ```

2. **GitHub Secrets登録**
   - Repository Settings → Secrets and variables → Actions
   - 以下のSecretsを追加:

   ```yaml
   GCP_PROJECT_ID: "確定したプロジェクトID"
   GCP_SA_KEY: "生成したJSONキーの内容"
   NEXTAUTH_SECRET: "ランダム生成文字列"
   GOOGLE_CLIENT_ID: "Google OAuth設定後のID"
   GOOGLE_CLIENT_SECRET: "Google OAuth設定後のSecret"
   ```

3. **Google OAuth設定**
   - Google Cloud Console → APIs & Services → Credentials
   - OAuth 2.0クライアントID作成
   - 承認済みリダイレクトURI設定

**期待結果**: GitHub ActionsからGCPへの認証基盤完成

### Phase 3: 初回デプロイ実行
**実装内容**:
1. **手動初回デプロイ**
   ```bash
   # ローカルから初回サービス作成
   cd backend
   gcloud run deploy genius-backend-production \
     --source . \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated
   
   cd ../frontend  
   gcloud run deploy genius-frontend-production \
     --source . \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated
   ```

2. **GitHub Actions動作テスト**
   - テスト用PRを作成してマージ
   - ワークフロー実行ログ確認
   - デプロイ成功確認

3. **E2Eテスト実行**
   - フロントエンド画面アクセス確認
   - バックエンドAPI動作確認
   - 統合動作テスト

**期待結果**: 完全自動化CI/CDパイプラインの動作確認完了

### Phase 4: 運用最適化
**実装内容**:
1. **モニタリング設定**
   - Cloud Runサービスメトリクス確認
   - ログ集約設定
   - アラート設定

2. **パフォーマンス最適化**
   - インスタンス数調整
   - メモリ・CPU設定最適化
   - Cold Start対策

3. **セキュリティ強化**
   - IAM最小権限の原則適用
   - VPC設定検討
   - HTTPS強制設定

**期待結果**: プロダクション対応の安定運用基盤

## 🧪 テストプラン

### 機能テスト
- [ ] GitHub Actions ワークフロー正常実行
- [ ] Backend Cloud Runサービス正常デプロイ
- [ ] Frontend Cloud Runサービス正常デプロイ
- [ ] 環境変数正常設定
- [ ] ヘルスチェック正常動作

### 統合テスト
- [ ] フロントエンド → バックエンドAPI通信
- [ ] 認証機能動作確認
- [ ] マルチエージェント機能動作確認
- [ ] ファイルアップロード機能動作確認
- [ ] Web検索機能動作確認

### パフォーマンステスト
- [ ] 冷間開始時間測定
- [ ] 同時接続負荷テスト
- [ ] レスポンス時間測定
- [ ] リソース使用量監視

## 📊 成功指標

### 定量的指標
- **デプロイ時間**: 5分以内で完了
- **成功率**: 95%以上
- **Cold Start時間**: 5秒以内
- **レスポンス時間**: 1秒以内
- **可用性**: 99.5%以上

### 定性的指標
- mainブランチマージ → 自動デプロイ完全動作
- 開発者のデプロイ作業ゼロ化
- 本番環境の安定稼働
- エラー時の自動ロールバック対応

## ⚠️ リスク・注意事項

### 技術的リスク
- **GCP課金**: 予期しない高額課金の可能性
  - **対策**: Cloud Run料金上限設定、アラート設定
- **サービスアカウント権限**: 過剰な権限付与のリスク
  - **対策**: 最小権限の原則、定期的な権限監査
- **シークレット管理**: GitHub Secretsの漏洩リスク
  - **対策**: 定期的なキーローテーション

### 運用リスク
- **初回デプロイ失敗**: 設定不備による失敗
  - **対策**: ローカル環境での事前テスト
- **DNS設定**: カスタムドメイン設定時の問題
  - **対策**: 段階的なドメイン移行
- **データベース**: 永続化データの管理
  - **対策**: Cloud SQLまたはFirestore検討

## 🔄 ロールバック計画

**デプロイ失敗時の対処**:
1. **自動ロールバック**: GitHub Actions履歴から前バージョンに復元
2. **手動ロールバック**: gcloudコマンドで直前リビジョンに戻す
3. **緊急対応**: Cloud Runコンソールから手動復旧

**設定変更失敗時の対処**:
1. **Secrets復元**: GitHub Secretsの前バージョンに戻す
2. **IAM復元**: GCP IAM設定の復元
3. **サービス削除**: 完全に削除して再作成

## 📅 実装スケジュール

### Week 1: 基盤構築
- **Day 1-2**: GCP環境構築・API有効化
- **Day 3-4**: サービスアカウント・IAM設定
- **Day 5**: GitHub Secrets設定

### Week 2: デプロイ実装
- **Day 1-2**: 初回手動デプロイ実行
- **Day 3-4**: GitHub Actions自動化テスト
- **Day 5**: E2E統合テスト

### Week 3: 運用最適化
- **Day 1-2**: モニタリング・アラート設定
- **Day 3-4**: パフォーマンス最適化
- **Day 5**: ドキュメント整備・運用手順作成

## 📚 参考資料

### 既存ドキュメント
- `.github/workflows/deploy-cloud-run.yml`: GitHub Actions設定
- `cloudbuild.yaml`: Cloud Build設定
- `backend/Dockerfile`: バックエンドDocker設定
- `frontend/Dockerfile`: フロントエンドDocker設定

### GCP公式ドキュメント
- [Cloud Run デプロイメント](https://cloud.google.com/run/docs/deploying)
- [GitHub Actions と Cloud Run](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
- [サービスアカウント認証](https://cloud.google.com/docs/authentication/production)

---

## ✅ 実装完了報告

### 自動化スクリプト実装完了（2025-06-28）

#### 完成した自動化ツール ✅
- **`scripts/setup-gcp-cicd.sh`**: GCP CI/CD環境完全自動構築
  - 既存GCPプロジェクト対応（blog-*プロジェクト）
  - サービスアカウント自動作成・権限設定
  - API有効化・Artifact Registry作成
  - セキュリティキー生成・管理

- **`scripts/setup-github-secrets.sh`**: GitHub Secrets完全自動設定
  - GitHub CLI使用によるCLI自動化対応
  - 全必要Secrets自動登録
  - Repository Variables設定
  - セキュリティファイル自動清掃

#### entrypoint.sh統合完了 ✅
- **選択肢29**: GCP CI/CD環境自動構築
- **選択肢30**: GitHub Secrets自動設定
- **選択肢31**: CI/CDパイプライン動作テスト
- **ワンストップ対応**: `./entrypoint.sh`でCI/CD全機能アクセス

### 使用方法

**ステップ1**: GCP環境構築
```bash
./entrypoint.sh
# → 選択肢29を選択
# → blog-*プロジェクトから選択入力
```

**ステップ2**: GitHub Secrets設定
```bash
./entrypoint.sh  
# → 選択肢30を選択
# → GitHub CLI認証済み前提
```

**ステップ3**: CI/CDテスト
```bash
./entrypoint.sh
# → 選択肢31を選択
# → PR作成またはプッシュテスト
```

### 成功指標達成状況

| 指標 | 目標 | 実績 | 状況 |
|-----|------|------|------|
| 自動化スクリプト完成 | 100% | 100% | ✅ 達成 |
| entrypoint.sh統合 | 統合完了 | 統合完了 | ✅ 達成 |
| CLI自動化対応 | GitHub CLI対応 | GitHub CLI完全対応 | ✅ 達成 |
| ワンコマンド化 | 実現 | 実現 | ✅ 達成 |

**🎯 Issue完了条件**: 
- ~~自動化スクリプト完成~~ ✅ 完了
- ~~GitHub Secrets CLI自動化~~ ✅ 完了  
- ~~entrypoint.sh統合~~ ✅ 完了
- mainブランチマージ → 自動デプロイの完全動作確認（次フェーズ）
- staging/production環境の正常稼働（次フェーズ）

**関連Issue**: なし  
**依存関係**: GitHub repository access, GCP project access  
**影響範囲**: 全体インフラ・デプロイプロセス