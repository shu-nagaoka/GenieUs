# アーキテクチャ概要

GenieUs - Google ADKを使用したAI子育て支援フルスタックアプリケーションの設計思想と全体構成

## 🎯 プロジェクト概要

**「見えない成長に、光をあてる。不安な毎日を、自信に変える。」**

GenieUsは、Google Agent Development Kit (ADK)を核として構築された次世代AI子育て支援システムです。親の子育ての悩みに専門的なアドバイスを提供し、子どもの成長を支援します。

## 🏗️ 全体アーキテクチャ

### アプリケーション構造

```
┌─────────────────────────────────────────────────────────────┐
│                    GenieUs System                         │
├─────────────────────┬───────────────────────────────────────┤
│    Frontend         │           Backend                     │
│                     │                                       │
│  Next.js 15         │  FastAPI + Google ADK                 │
│  TypeScript         │  Python 3.12+                         │
│  Tailwind CSS       │                                       │
│  shadcn/ui          │  ┌─────────────────────────────────┐  │
│                     │  │        Agent Layer              │  │
│  ┌─────────────────┐│  │  - Childcare Agents             │  │
│  │ Chat Interface  ││  │  - ADK Integration              │  │
│  │ Dashboard       ││  │                                 │  │
│  │ Reports         ││  └─────────────────────────────────┘  │
│  └─────────────────┘│  ┌─────────────────────────────────┐  │
│                     │  │      Application Layer          │  │
│                     │  │  - UseCases (Business Logic)    │  │
│                     │  │  - DI Container (Composition)   │  │
│                     │  └─────────────────────────────────┘  │
│                     │  ┌─────────────────────────────────┐  │
│                     │  │    Infrastructure Layer         │  │
│                     │  │  - Gemini AI Services          │  │
│                     │  │  - File Operations              │  │
│                     │  │  - External APIs               │  │
│                     │  └─────────────────────────────────┘  │
└─────────────────────┴───────────────────────────────────────┘
```

## 🎨 設計思想

### 1. ADKファーストアプローチ

**「Agent中心の設計」** - 従来のWeb API中心からエージェント主導の判断・ルーティング中心へ

```python
# ADKネイティブなエージェント定義
agent = Agent(
    name="GenieConsultant",
    model="gemini-2.5-flash-preview",
    tools=[childcare_consultation_tool],
    instruction="子育ての専門家として..."
)
```

### 2. Clean Architecture + DI統合

**Composition Rootパターン + AgentManagerパターン**による明確な依存関係管理：

```python
# main.py - 中央集約的な組み立て（AgentManagerパターン）
def create_app() -> FastAPI:
    container = DIContainer()
    
    # AgentManagerによる一元管理（main.py肥大化防止）
    agent_manager = AgentManager(container)
    agent_manager.initialize_all_agents()
    
    app = FastAPI()
    app.container = container
    app.agent_manager = agent_manager
    
    # FastAPI Depends統合（グローバル変数不要）
    container.wire(modules=["src.presentation.api.routes.chat"])
    
    return app
```

### 3. 段階的複雑性管理

- **MVP**: シンプルなエージェント + 基本ツール
- **発展**: 専門エージェント + 高度なツール
- **未来**: マルチモーダル + 予測AI

## 📁 ディレクトリ構成

### バックエンド（`backend/`）

```
src/
├── agents/                 # 🤖 エージェント定義層
│   ├── agent_manager.py   # エージェント一元管理（main.py肥大化防止）
│   ├── di_based_childcare_agent.py    # DI対応エージェント
│   └── development_agent.py # 発育相談エージェント
├── tools/                  # 🔧 Agent-Application間アダプター
│   └── childcare_consultation_tool.py # 子育て相談ツール
├── application/            # 📋 アプリケーション層
│   ├── usecases/          # ビジネスロジック（プロンプト構築含む）
│   └── interface/protocols/ # インターフェース定義
├── infrastructure/         # 🔌 インフラストラクチャ層（純粋技術実装）
│   └── adapters/          # 外部システム統合（プロンプト構築禁止）
├── di_provider/           # 💉 依存性注入
│   ├── container.py       # 統合DIコンテナ
│   └── factory.py         # コンテナファクトリ
├── presentation/          # 🌐 プレゼンテーション層
│   └── api/routes/        # FastAPIエンドポイント
└── main.py                # 🚀 Composition Root（アプリケーションファクトリー）
```

### フロントエンド（`frontend/`）

```
src/
├── app/                   # Next.js App Router
├── components/
│   ├── ui/               # shadcn/ui基本コンポーネント
│   ├── features/         # 機能別コンポーネント
│   └── layout/           # レイアウトコンポーネント
├── hooks/                # カスタムフック
└── lib/                  # ユーティリティ
```

## 🔄 レイヤー責務

### Agent Layer（エージェント層）
- **責務**: AI判断・ルーティング・自然言語処理
- **技術**: Google ADK + Gemini
- **パターン**: エージェント組み合わせ、動的指示生成

### Tools Layer（ツール層）
- **責務**: Agent-Application間のアダプター
- **技術**: FunctionTool + 型変換
- **パターン**: 薄いアダプター、エラーハンドリング

### Application Layer（アプリケーション層）
- **責務**: ビジネスロジック調整・UseCase実行・プロンプト構築
- **技術**: Pure Python + DI Container
- **パターン**: UseCase、Repository、Factory
- **🎯重要**: AI用プロンプト構築はここで実装（Infrastructure層では禁止）

### Infrastructure Layer（インフラ層）
- **責務**: 外部システム統合・データアクセス（純粋技術実装のみ）
- **技術**: Gemini API、GCS、メモリDB
- **パターン**: Adapter、Protocol実装
- **🚨重要制約**: ビジネスロジック（プロンプト構築、child_id等）は絶対禁止

### Presentation Layer（プレゼンテーション層）
- **責務**: HTTP API・UI統合
- **技術**: FastAPI + Next.js
- **パターン**: REST API、React Components

## ⚡ 主要設計パターン

### 1. 動的エージェント指示
ユーザー入力に基づくコンテキスト適応型指示生成

### 2. ツールベースアーキテクチャ  
安全性チェック、年齢検出、アドバイス生成の専用ツール

### 3. AgentManagerパターン
main.py肥大化防止のためのエージェント一元管理と段階的初期化

### 4. Infrastructure/UseCase分離原則
**🚨最重要**: Infrastructure層でのプロンプト構築は絶対禁止
- **Infrastructure**: 「どうやって」APIを呼ぶか（技術実装）
- **UseCase**: 「何を」分析するか（ビジネスロジック・プロンプト構築）

### 5. Composition Rootパターン + FastAPI Depends統合
main.pyでの中央集約的な依存関係組み立て + container.wire()による自動配線

### 6. 全層ロガーDI統合
setup_logger個別呼び出しを廃止し、DIコンテナからの統一ロガー注入

### 7. 段階的フォールバック
プライマリ→セカンダリ→フォールバック応答の多層エラー処理

### 8. セキュリティファースト開発
入力検証、エラーハンドリング、安全なセッション管理

## 🚀 現在の実装状況

### ✅ 実装済み（MVP）
- [x] 基本エージェント（シンプル子育て相談）
- [x] DI統合アーキテクチャ（Composition Root + FastAPI Depends）
- [x] AgentManagerパターン（main.py肥大化防止）
- [x] Infrastructure/UseCase分離（プロンプト構築適正化）
- [x] 全層ロガーDI統合（個別初期化廃止）
- [x] RESTful API（チャット・ヘルス）
- [x] Next.js基本UI
- [x] 段階的エラーハンドリング

### 🔄 実装中
- [ ] 専門エージェント（睡眠・栄養・発達）
- [ ] 高度なツール（画像・音声解析）
- [ ] 認証システム統合

### 📋 計画中（V2）
- [ ] マルチモーダル対応（音声・画像・動画）
- [ ] 予測インサイト機能
- [ ] 努力肯定システム
- [ ] ゼロエフォート記録

## 🔗 関連ドキュメント

### 設計深掘り
- [ADKファースト設計](./adk-first-design.md) - ADK統合の核心思想
- [Clean Architecture](./clean-architecture.md) - 層責務と依存関係
- [DI Container設計](./di-container-design.md) - 依存注入の詳細

### 実装ガイド
- [開発クイックスタート](../development/quick-start.md)
- [新エージェント作成](../guides/new-agent-creation.md)
- [新ツール開発](../guides/new-tool-development.md)

### 技術詳細  
- [ADKベストプラクティス](../technical/adk-best-practices.md)
- [エラーハンドリング戦略](../technical/error-handling.md)

---

**💡 設計の核心**: ADKの力を最大限活用しつつ、保守性・テスタビリティ・拡張性を確保したハイブリッドアーキテクチャ