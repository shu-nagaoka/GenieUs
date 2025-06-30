# GenieNest 🧞‍♂️

**見えない成長に、光をあてる。不安な毎日を、自信に変える。**

子育ての日々の記録と専門的なアドバイスを提供するAI子育て支援プラットフォーム

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)

## 🌟 特徴

- **マルチモーダル対応**: 音声・画像・テキストで簡単記録
- **Google AI統合**: 最新のVertex AIによる専門的育児アドバイス
- **成長可視化**: 見えない日々の成長を可視化
- **24時間サポート**: いつでも相談できるAIアシスタント

## 🚀 主要機能

### 成長記録
- 身長・体重・発達記録の管理
- 画像付きメモリー機能
- 成長グラフの自動生成

### 食事管理
- 食事記録・栄養分析
- 食事プランの提案
- アレルギー・離乳食対応

### スケジュール
- 予防接種・健診管理
- 日々のルーチン記録
- イベント・記念日管理

### AIチャット
- 育児相談チャット
- 専門エージェント（栄養・睡眠・発達）
- リアルタイム画像分析

## 🏗️ 技術スタック

### Frontend
- **Next.js 15** + React 19
- **TypeScript** 
- **Tailwind CSS** + shadcn/ui
- **React Query** for state management

### Backend
- **FastAPI** + Python
- **PostgreSQL** database
- **Google ADK** (Agent Development Kit)
- **Vertex AI** for AI capabilities

### Infrastructure
- **Google Cloud Run** (serverless)
- **Cloud SQL** (managed database)
- **Secret Manager** (credential management)

## ⚡ クイックスタート

### 前提条件
- Node.js 18+
- Python 3.11+
- uv (Python package manager)

### 1. リポジトリクローン
```bash
git clone https://github.com/shu-nagaoka/GenieUs.git
cd GenieUs
```

### 2. バックエンド起動
```bash
cd backend
uv install
uv run python -m src.main
```
→ http://localhost:8080 でAPI起動

### 3. フロントエンド起動
```bash
cd frontend
npm install
npm run dev
```
→ http://localhost:3000 でアプリ起動

### 4. 環境変数設定
各ディレクトリの `.env.example` を参考に `.env.local` を作成

## 📱 使い方

1. **家族構成登録**: 子どもの基本情報を入力
2. **日々の記録**: 成長・食事・スケジュールを記録
3. **AIチャット**: 気になることを相談
4. **レポート確認**: 成長の推移やインサイトを確認

## 🤝 コントリビューション

このプロジェクトは **Google for Startups AI Hackathon 2025** への提出作品です。

開発の詳細は `develop` ブランチをご確認ください。

## 📄 ライセンス

[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc-sa/4.0/)

このプロジェクトは **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** の下で提供されています。

### 🔓 利用について

- **✅ 学習・研究目的のみ利用可能**（完全非営利限定）
- **🚫 商用利用・企業利用は完全禁止**（フリーランス・副業含む）
- **🚫 営利に結びつく一切の活動を禁止**（間接的収益も含む）
- **📋 改変版は同じライセンスで公開が必要**
- **🏷️ 原著作者表示が必要**

詳細は [LICENSE](LICENSE) ファイルをご確認ください。

## 🙏 謝辞

- Google AI/ML Developer Relations team
- shadcn/ui コンポーネントライブラリ
- コミュニティの皆様

---

**「今日の小さな成長も、明日への大きな一歩」**  
毎日を頑張る親御さんを、AIが24時間サポートします。