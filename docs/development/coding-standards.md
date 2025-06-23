# コーディング規約・標準

GenieUsプロジェクトにおけるコーディング規約とベストプラクティス。**新規実装・コードレビュー時の必須参照文書**

## 🎯 基本原則

### 1. 一貫性の維持
- プロジェクト全体で統一されたコーディングスタイル
- 既存コードパターンの踏襲
- レイヤー責務の明確な分離

### 2. 可読性の最優先
- 自己説明的なコード
- 適切な命名規則
- 必要最小限のコメント

### 3. 保守性の確保
- 依存関係の明確化
- エラーハンドリングの統一
- テスタビリティの考慮

## 📝 バックエンドコーディング規約

### Import文配置規約（最重要）

**🚨 すべてのimport文はファイルの先頭に配置し、関数内やクラス内でのimportは絶対禁止**

```python
# ✅ 正しい例 - ファイル先頭にすべてのimportを配置
from typing import Dict, Any, Optional
from dataclasses import dataclass
from google.adk.tools import FunctionTool
from google.adk.core import ToolContext
from src.application.interface.protocols.child_carer import ChildCarerProtocol
from src.share.logger import setup_logger

def create_childcare_tool(context: ToolContext) -> FunctionTool:
    """ADK用の子育て相談ツール"""
    # 実装
    pass

# ❌ 絶対に避けるべき例 - 関数内でのimport
def create_childcare_tool(context: ToolContext) -> FunctionTool:
    from google.adk.tools import FunctionTool  # これは禁止
    from typing import Dict, Any  # これも禁止
    # 実装
    pass
```

**理由:**
- **依存関係の明確化**: ファイルを開いた瞬間にすべての依存関係が把握できる
- **パフォーマンス向上**: 関数呼び出しのたびにimportが実行されることを防ぐ  
- **コードの可読性**: import部分とロジック部分が明確に分離される
- **ADK開発での重要性**: エージェントやツールの依存関係が明確になる
- **静的解析の支援**: Ruffやmypyがより効果的に動作する

### Import文の順序

```python
# 1. 標準ライブラリ
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 2. サードパーティライブラリ
from google.adk import Agent
from google.adk.tools import FunctionTool
from dependency_injector import containers, providers

# 3. プロジェクト内モジュール（絶対パス）
from src.application.interface.protocols.child_carer import SafetyAssessorProtocol
from src.infrastructure.adapters.childcare_safety_assessor import GeminiSafetyAssessor
from src.share.logger import setup_logger
```

### 型アノテーション

**🔒 必須**: すべての関数・メソッドに型ヒントを追加

```python
# ✅ 正しい例
def create_childcare_agent(
    agent_type: str, 
    childcare_tool: FunctionTool,
    **kwargs: Any
) -> Agent:
    """エージェント作成（型アノテーション完備）"""
    pass

# ✅ dataclass使用例
@dataclass
class PureChildcareRequest:
    """子育て相談リクエスト"""
    message: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None

# ❌ 避けるべき例
def create_agent(agent_type, tool):  # 型アノテーションなし
    pass
```

### エラーハンドリング

**段階的フォールバック戦略**を実装：

```python
def safe_operation(request: SomeRequest) -> SomeResponse:
    """段階的エラーハンドリング例"""
    try:
        # プライマリ処理
        result = primary_operation(request)
        return create_success_response(result)
        
    except SpecificError as e:
        # セカンダリ処理
        logger.warning(f"Primary failed, trying secondary: {e}")
        try:
            result = secondary_operation(request)
            return create_success_response(result)
        except Exception as secondary_error:
            logger.error(f"Secondary also failed: {secondary_error}")
            
    except Exception as e:
        # フォールバック処理
        logger.error(f"Unexpected error: {e}")
        
    # 最終フォールバック
    return create_fallback_response(
        "申し訳ございません。一時的な問題が発生しました。",
        request.session_id
    )
```

### 構造化ログ

```python
from src.share.logger import setup_logger

logger = setup_logger(__name__)

def process_request(request: SomeRequest) -> SomeResponse:
    """構造化ログの使用例"""
    logger.info(
        "Processing request",
        extra={
            "user_id": request.user_id,
            "session_id": request.session_id,
            "request_type": type(request).__name__,
            "message_length": len(request.message)
        }
    )
    
    try:
        result = do_processing(request)
        logger.info(
            "Request processed successfully",
            extra={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "response_length": len(result.response),
                "processing_time_ms": 150
            }
        )
        return result
        
    except Exception as e:
        logger.error(
            "Request processing failed",
            extra={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise
```

### DI統合パターン

#### **全層ロガーDI化（必須）**

**🚨 重要**: すべての層でロガーはDIコンテナから注入し、個別初期化は禁止

```python
# ✅ 正しいパターン: DI注入
class SomeUseCase:
    """全層でDI注入パターンを採用"""
    
    def __init__(
        self,
        safety_assessor: SafetyAssessorProtocol,
        logger: logging.Logger  # DIコンテナから注入
    ):
        self.safety_assessor = safety_assessor
        self.logger = logger
    
    def execute(self, request: SomeRequest) -> SomeResponse:
        """ビジネスロジック実行"""
        self.logger.info("処理開始", extra={"request_id": request.id})
        # 実装
        pass

# ✅ エージェント作成パターン（ロガー注入版）
def create_childcare_agent(
    childcare_tool: FunctionTool,
    logger: logging.Logger  # 追加：ロガーも注入
) -> Agent:
    """注入されたツールとロガーを使用する子育て相談エージェント"""
    logger.info("子育て相談エージェント作成開始")
    
    try:
        agent = Agent(
            model="gemini-2.5-flash-preview-05-20",
            name="GenieChildcareConsultant",
            tools=[childcare_tool],
            instruction="..."
        )
        logger.info("子育て相談エージェント作成完了")
        return agent
    except Exception as e:
        logger.error(f"子育て相談エージェント作成エラー: {e}")
        raise

# ✅ ツール作成パターン（ロガー注入版）
def create_childcare_consultation_tool(
    usecase: PureChildcareUseCase,
    logger: logging.Logger  # 追加：ロガーも注入
) -> FunctionTool:
    """ファクトリーパターンでツール作成（ロガー注入版）"""
    
    def tool_function(message: str, **kwargs) -> Dict[str, Any]:
        """ADK用ツール関数"""
        try:
            logger.info("ツール実行開始", extra={"message_length": len(message)})
            request = SomeRequest(message=message, **kwargs)
            response = usecase.execute(request)
            logger.info("ツール実行完了", extra={"success": True})
            return {
                "success": True,
                "response": response.message,
                "metadata": response.metadata
            }
        except Exception as e:
            logger.error(
                "ツール実行エラー",
                extra={
                    "error": str(e),
                    "message": message
                }
            )
            return {
                "success": False,
                "response": "エラーが発生しました",
                "metadata": {"error": str(e)}
            }
    
    return FunctionTool(func=tool_function)

# ❌ 避けるべき例：個別ロガー初期化
def bad_function():
    logger = setup_logger(__name__)  # これは禁止
    logger = logging.getLogger(__name__)  # これも禁止
```

#### **FastAPI Depends統合パターン（推奨）**

```python
# ✅ FastAPI Depends + DI統合例
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@inject  # DI注入を有効化
async def chat_endpoint(
    request: ChatRequest,
    # FastAPI Depends + DI統合
    tool = Depends(Provide[DIContainer.childcare_consultation_tool]),
    logger = Depends(Provide[DIContainer.logger]),
):
    """チャットエンドポイント（DI完全統合版）"""
    logger.info(
        "チャット要求受信",
        extra={
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message_length": len(request.message)
        }
    )
    
    try:
        # ツール使用（DIから注入済み）
        tool_result = tool.func(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        logger.info("チャット処理完了", extra={"session_id": request.session_id})
        return ChatResponse(...)
        
    except Exception as e:
        logger.error(
            "チャット処理エラー",
            extra={
                "error": str(e),
                "session_id": request.session_id
            }
        )
        raise HTTPException(status_code=500, detail="...")

# ❌ 避けるべき例：グローバル変数
_container = None  # これは避ける
_childcare_agent = None  # これも避ける

def setup_routes(container, agent):  # この方式は非推奨
    global _container, _childcare_agent
    _container = container
    _childcare_agent = agent
```

#### **アプリケーションファクトリーパターン（必須）**

```python
# ✅ main.py アプリケーションファクトリー化
from dependency_injector.wiring import inject, Provide
from src.di_provider.container import DIContainer
from src.agents.agent_manager import AgentManager

def create_app() -> FastAPI:
    """FastAPIアプリケーションファクトリー"""
    # DIコンテナ初期化
    container = DIContainer()
    
    # ⭐ 新規追加: AgentManager による一元管理
    agent_manager = AgentManager(container)
    agent_manager.initialize_all_agents()
    
    app = FastAPI(...)
    app.container = container  # アプリケーションに関連付け
    app.agent_manager = agent_manager  # エージェント管理を関連付け
    
    # ⭐ 重要: wiringでFastAPI Dependsと統合
    container.wire(modules=[
        "src.presentation.api.routes.chat",
        "src.presentation.api.routes.health",
    ])
    
    # ルーター登録（グローバル変数不要）
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    
    return app

# アプリケーション作成
app = create_app()

# ❌ 避けるべき例：グローバル初期化
logger = setup_logger(__name__)  # main.pyでも個別初期化は避ける

# ❌ 避けるべき例：個別エージェント初期化
childcare_tool = container.childcare_consultation_tool()  # AgentManagerで集約
childcare_agent = get_childcare_agent("simple", childcare_tool)  # 個別初期化は避ける
```

#### **AgentManagerパターン（推奨）**

```python
# ✅ src/agents/agent_manager.py
from typing import Dict
from google.adk.agents import Agent
from src.agents.di_based_childcare_agent import get_childcare_agent
from src.agents.development_agent import get_development_agent
from src.di_provider.container import DIContainer

class AgentManager:
    """エージェント一元管理クラス
    
    main.pyの肥大化を防ぎ、エージェント関連の処理を集約する
    """
    
    def __init__(self, container: DIContainer):
        self.container = container
        self.logger = container.logger()
        self._agents: Dict[str, Agent] = {}
    
    def initialize_all_agents(self) -> None:
        """全エージェントを初期化"""
        self.logger.info("全エージェント初期化開始")
        
        try:
            # 各エージェントを順次初期化
            self._initialize_childcare_agent()
            self._initialize_development_agent()
            # 将来: self._initialize_nutrition_agent()
            # 将来: self._initialize_sleep_agent()
            
            self.logger.info(f"全エージェント初期化完了: {len(self._agents)}個のエージェント")
            
        except Exception as e:
            self.logger.error(f"エージェント初期化エラー: {e}")
            raise
    
    def _initialize_childcare_agent(self) -> None:
        """子育て相談エージェント初期化"""
        try:
            childcare_tool = self.container.childcare_consultation_tool()
            agent = get_childcare_agent("simple", childcare_tool, self.logger)
            self._agents["childcare"] = agent
            self.logger.info("子育て相談エージェント初期化完了")
        except Exception as e:
            self.logger.error(f"子育て相談エージェント初期化エラー: {e}")
            raise
    
    def _initialize_development_agent(self) -> None:
        """発育相談エージェント初期化"""
        try:
            development_tool = self.container.development_consultation_tool()
            agent = get_development_agent("simple", development_tool, self.logger)
            self._agents["development"] = agent
            self.logger.info("発育相談エージェント初期化完了")
        except Exception as e:
            self.logger.error(f"発育相談エージェント初期化エラー: {e}")
            raise
    
    def get_agent(self, agent_type: str) -> Agent:
        """指定されたタイプのエージェントを取得"""
        if agent_type not in self._agents:
            available = list(self._agents.keys())
            raise ValueError(f"エージェント '{agent_type}' が見つかりません. 利用可能: {available}")
        
        return self._agents[agent_type]

# ❌ 避けるべき例：AgentGatewayパターン（over-engineering）
class AgentGateway:  # この設計は複雑すぎるため使用禁止
    pass
```

### リンティング・フォーマット

```bash
# Ruffによる品質管理
uv run ruff check           # リンター実行
uv run ruff format          # コードフォーマット
uv run ruff check --fix     # 自動修正
```

**pyproject.toml設定に従う**（プロジェクトルートを参照）

## 🎨 フロントエンドコーディング規約

### TypeScript規約

```typescript
// ✅ 正しい例 - import文をファイル先頭に配置
'use client'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { MessageCircle, Send } from 'lucide-react'
import { ChatMessage } from '@/types/types'

interface ChatComponentProps {
  initialMessages?: ChatMessage[]
  onMessageSend?: (message: string) => void
}

export default function ChatComponent({ 
  initialMessages = [], 
  onMessageSend 
}: ChatComponentProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  
  // コンポーネント実装
  return (
    <Card className="w-full max-w-2xl mx-auto">
      {/* JSX実装 */}
    </Card>
  )
}

// ❌ 避けるべき例 - 関数内import
export default function ChatComponent() {
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = () => {
    import('@/lib/api').then(api => {  // これは避ける
      // 実装
    })
  }
}
```

### コンポーネント構成

```typescript
// ✅ shadcn/ui + Tailwind パターン
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function FeatureComponent() {
  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>機能タイトル</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input placeholder="入力してください" />
        <Button className="w-full">
          実行
        </Button>
      </CardContent>
    </Card>
  )
}
```

### 型定義

```typescript
// src/types/types.ts
export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'genie'
  timestamp: Date
  metadata?: Record<string, any>
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}
```

### API連携

```typescript
// ✅ 型安全なAPI呼び出し
import { ApiResponse, ChatMessage } from '@/types/types'

interface SendMessageRequest {
  message: string
  user_id?: string
  session_id?: string
}

interface SendMessageResponse {
  response: string
  status: string
  session_id: string
  follow_up_questions?: string[]
}

export async function sendMessage(
  request: SendMessageRequest
): Promise<ApiResponse<SendMessageResponse>> {
  try {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return { success: true, data }
    
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }
  }
}
```

## 🧪 テスト規約

### バックエンドテスト

```python
# tests/test_usecase.py
import pytest
from src.di_provider.factory import get_container
from src.application.usecases.pure_childcare_usecase import PureChildcareRequest

class TestPureChildcareUseCase:
    """UseCase単体テスト"""
    
    def setup_method(self):
        """テストセットアップ"""
        self.container = get_container()
        self.usecase = self.container.pure_childcare_usecase()
    
    def test_successful_consultation(self):
        """正常な相談処理のテスト"""
        request = PureChildcareRequest(
            message="3ヶ月の赤ちゃんが夜泣きします",
            user_id="test_user",
            session_id="test_session"
        )
        
        response = self.usecase.consult(request)
        
        assert response.success is True
        assert "睡眠" in response.advice
        assert response.age_group == "乳児前期"
        assert len(response.recommendations) > 0
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # エラーケースのテスト実装
        pass
```

### フロントエンドテスト

```typescript
// src/__tests__/components/ChatComponent.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ChatComponent from '@/components/features/chat/ChatComponent'

describe('ChatComponent', () => {
  it('should render initial messages', () => {
    const initialMessages = [
      { id: '1', content: 'Hello', sender: 'user' as const, timestamp: new Date() }
    ]
    
    render(<ChatComponent initialMessages={initialMessages} />)
    
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
  
  it('should send message on submit', async () => {
    const onMessageSend = jest.fn()
    
    render(<ChatComponent onMessageSend={onMessageSend} />)
    
    const input = screen.getByPlaceholderText('メッセージを入力...')
    const sendButton = screen.getByRole('button', { name: '送信' })
    
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(onMessageSend).toHaveBeenCalledWith('Test message')
    })
  })
})
```

## 🔧 開発ツール設定

### VS Code設定

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  }
}
```

### Git Hook設定

`.git/hooks/pre-commit`:
```bash
#!/bin/bash
# バックエンド品質チェック
cd backend && uv run ruff check

# フロントエンド品質チェック  
cd frontend && npm run lint

# 型チェック
cd frontend && npm run type-check
```

## 📊 品質メトリクス

### 必須品質基準

- **型カバレッジ**: 95%以上
- **テストカバレッジ**: 80%以上
- **リント違反**: 0件
- **型エラー**: 0件

### 品質確認コマンド

```bash
# バックエンド品質確認
cd backend
uv run ruff check                    # リント確認
uv run pytest --cov=src            # テストカバレッジ
uv run mypy src                     # 型チェック

# フロントエンド品質確認
cd frontend
npm run lint                        # ESLint確認
npm run test:coverage              # テストカバレッジ
npm run type-check                 # TypeScript型チェック
```

## 📋 コードレビューチェックリスト

### ✅ 基本事項
- [ ] Import文がファイル先頭に配置されている
- [ ] 型アノテーションが完備されている
- [ ] エラーハンドリングが実装されている
- [ ] 構造化ログが使用されている
- [ ] テストケースが追加されている

### ✅ DI統合（重要）
- [ ] **ロガーはDIコンテナから注入されている**（個別初期化禁止）
- [ ] **エージェント作成関数にlogger引数が追加されている**
- [ ] **ツール作成関数にlogger引数が追加されている**
- [ ] **FastAPI Dependsパターンが使用されている**（@inject + Depends(Provide[])）
- [ ] **グローバル変数を使用していない**（_container, _agentなど）

### ✅ アーキテクチャ
- [ ] レイヤー責務が守られている
- [ ] DI統合が適切に実装されている
- [ ] Protocol/Interface使用が適切
- [ ] 依存関係の方向が正しい
- [ ] **アプリケーションファクトリーパターンが使用されている**（main.pyのcreate_app）

### ✅ ADK統合
- [ ] ADK制約が遵守されている
- [ ] ツール実装が薄いアダプターになっている
- [ ] エージェント指示が適切
- [ ] セッション管理が実装されている

### ✅ Agent管理（新規追加）
- [ ] **AgentManagerパターンが使用されている**（main.py肥大化防止）
- [ ] **AgentGatewayパターンを使用していない**（over-engineering回避）
- [ ] **エージェント初期化がAgentManagerに集約されている**
- [ ] **新エージェント追加時にAgentManagerが更新されている**
- [ ] **エージェント取得がget_agent()メソッド経由である**

### ✅ FastAPI統合
- [ ] **container.wire()が設定されている**（main.pyで）
- [ ] **setup_routes関数を使用していない**（非推奨パターン）
- [ ] **@injectデコレータが使用されている**
- [ ] **Depends(Provide[])パターンが使用されている**

## 🔗 関連ドキュメント

### 開発関連
- [開発クイックスタート](./quick-start.md) - 環境構築・起動
- [デバッグガイド](./debugging.md) - トラブルシューティング
- [テスト戦略](./testing-strategy.md) - テスト実行方法

### アーキテクチャ関連
- [アーキテクチャ概要](../architecture/overview.md) - 全体設計
- [DI設計](../architecture/di-container-design.md) - 依存注入詳細

### 技術詳細
- [ADKベストプラクティス](../technical/adk-best-practices.md) - ADK制約・パターン
- [エラーハンドリング](../technical/error-handling.md) - 段階的フォールバック

---

**💡 重要**: この規約は**プロジェクトの品質基盤**です。新規実装・コードレビュー時は必ずこの文書を参照し、一貫性を保ってください。

---

## 🤖 Claude Code向け特別指示

**🚨 Claude Code実装者へ**: このドキュメントは**実装前必読**です。以下の規約に従わない実装は品質基準を満たしません。

### **実装時の必須確認事項**
1. **Import文配置**: ファイル先頭配置（最重要）
2. **型アノテーション**: 全関数に必須
3. **エラーハンドリング**: 段階的フォールバック実装
4. **DI統合**: main.py経由のComposition Root
5. **ログ記録**: 構造化ログ使用
6. **Agent管理**: AgentManagerパターン使用（AgentGateway禁止）

### **新エージェント実装時の手順**
1. **エージェント定義**: `src/agents/`に新エージェント作成
2. **UseCase実装**: ビジネスロジックをApplication層に実装
3. **Tool実装**: 薄いアダプターとしてTool層に実装
4. **AgentManager更新**: `_initialize_{agent_name}_agent()`メソッド追加
5. **DIコンテナ統合**: 必要な依存関係をcontainer.pyに追加

### **Infrastructure層プロンプト構築禁止ルール（最重要）**

**🚨 Infrastructure層でのプロンプト構築は絶対禁止**

```python
# ❌ 絶対に避けるべき例 - Infrastructure層でプロンプト構築
class GeminiImageAnalyzer(ImageAnalyzerProtocol):
    async def analyze_image(self, image_path: str, child_id: str) -> dict:
        # child_id = ビジネス概念！Infrastructure層が知るべきではない
        prompt = f"子供ID: {child_id}の画像を分析してください"  # ビジネスロジック！
        response = await self.model.generate_content_async(prompt)
        return response

# ✅ 正しい実装パターン
# Infrastructure層 - 純粋な技術実装
class GeminiImageAnalyzer(ImageAnalyzerProtocol):
    async def analyze_image_with_prompt(self, image_path: str, prompt: str) -> dict:
        # プロンプトをそのまま使用してAPIコール（ビジネス概念を知らない）
        response = await self.model.generate_content_async(prompt)
        return {"raw_response": response.text, "success": True}

# UseCase層 - ビジネスロジック（プロンプト構築も含む）
class ImageAnalysisUseCase:
    async def analyze_child_image(self, image_path: str, child_id: str) -> dict:
        # ビジネス専用プロンプト構築
        prompt = self._build_childcare_analysis_prompt(child_id, image_path)
        
        # Infrastructure層は純粋なAPIコール
        raw_result = await self.image_analyzer.analyze_image_with_prompt(image_path, prompt)
        
        # ビジネス概念への変換
        return self._transform_to_childcare_analysis(raw_result, child_id)
```

**理由:**
- **Infrastructure層の責務**: 「どうやって」APIを呼ぶか（技術的実装）
- **UseCase層の責務**: 「何を」分析するか（ビジネスロジック）
- **プロンプト**: ビジネス要件を含むため、UseCase層の責務
- **child_id等**: ビジネス概念はInfrastructure層が知ってはいけない

**適用対象:**
- 画像分析（Gemini API）
- 音声分析（Gemini API）
- LLM呼び出し全般
- 外部AI API統合

**違反検出サイン:**
- Infrastructure層でchild_id, user_id等のビジネス概念を引数に持つ
- Infrastructure層でビジネス専用プロンプトを構築している
- Protocol定義にビジネス概念が含まれている

**❌ 違反例を発見した場合**: 即座に修正し、該当パターンを学習してください。

### **Agent中心アーキテクチャ設計ルール（2024年12月追加）**

**🤖 重要**: GenieUsはAgent-Firstアーキテクチャを採用。以下のルールを必ず遵守してください。

#### **1. Agent中心設計原則**

```python
# ✅ Agent中心設計
AgentManagerでマルチエージェントルーティング
    ↓
各AgentがGemini-poweredで判断・アドバイス・安全性評価を実行
    ↓
Toolは純粋にマルチモーダル機能（画像・音声・ファイル・記録）のみ
    ↓
UseCase/Infrastructureも画像・音声・ファイル・記録管理のみ
```

#### **2. 重複実装の絶対禁止**

**🚨 以下のコンポーネントは実装禁止**（Agentが担当）：

```python
# ❌ 絶対実装禁止
- ChildcareAdviserProtocol（子育てアドバイス生成）
- SafetyAssessorProtocol（安全性評価）
- AgeDetectorProtocol（年齢検出）
- DevelopmentAdviserProtocol（発達評価）
- childcare_consultation_tool（子育て相談ツール）
- development_consultation_tool（発達相談ツール）
- pure_childcare_usecase（子育て相談UseCase）
- development_consultation_usecase（発達相談UseCase）

# ✅ 実装OK（Agentが使用するマルチモーダル機能）
- ImageAnalyzer（画像分析技術）
- VoiceAnalyzer（音声分析技術）
- FileOperator（ファイル操作技術）
- RecordManagement（記録管理技術）
```

#### **3. Tool/UseCase/Infrastructure実装範囲の制限**

**許可される機能のみ**：

```python
# ✅ 実装可能な技術機能
class ImageAnalysisUseCase:
    """画像分析技術（ビジネス概念なし）"""
    
class VoiceAnalysisUseCase:
    """音声分析技術（ビジネス概念なし）"""
    
class FileManagementUseCase:
    """ファイル操作技術（ビジネス概念なし）"""
    
class RecordManagementUseCase:
    """記録管理技術（ビジネス概念なし）"""

# ❌ 実装禁止（Agentが担当）
class ChildcareConsultationUseCase:  # Agent内で実装
class DevelopmentConsultationUseCase:  # Agent内で実装
class SafetyAssessmentUseCase:  # Agent内で実装
```

#### **4. Protocol定義の制限**

```python
# ✅ 技術的Protocol（実装OK）
class ImageAnalyzerProtocol(Protocol):
    """画像分析の技術的インターフェース"""
    def analyze_image_with_prompt(self, image_path: str, prompt: str) -> dict:
        ...

class VoiceAnalyzerProtocol(Protocol):
    """音声分析の技術的インターフェース"""
    def analyze_voice_with_prompt(self, voice_path: str, prompt: str) -> dict:
        ...

# ❌ ビジネス的Protocol（実装禁止）
class ChildcareAdviserProtocol(Protocol):  # Agent内で実装
class SafetyAssessorProtocol(Protocol):  # Agent内で実装
```

#### **5. DIコンテナ構成の制限**

```python
# ✅ 正しいDIコンテナ構成
class DIContainer(containers.DeclarativeContainer):
    """Agent中心のシンプル構成"""
    
    # Core Layer
    config = providers.Singleton(get_settings)
    logger = providers.Singleton(setup_logger)
    
    # Infrastructure Layer（マルチモーダル機能のみ）
    image_analyzer = providers.Singleton(GeminiImageAnalyzer, logger=logger)
    voice_analyzer = providers.Singleton(GeminiVoiceAnalyzer, logger=logger)
    file_operator = providers.Singleton(GcsFileOperator, logger=logger)
    
    # Application Layer（マルチモーダル機能のみ）
    image_analysis_usecase = providers.Factory(ImageAnalysisUseCase, ...)
    voice_analysis_usecase = providers.Factory(VoiceAnalysisUseCase, ...)
    file_management_usecase = providers.Factory(FileManagementUseCase, ...)
    
    # Tools Layer（マルチモーダル機能のみ）
    image_analysis_tool = providers.Factory(create_image_analysis_tool, ...)
    voice_analysis_tool = providers.Factory(create_voice_analysis_tool, ...)
    
    # Agent Manager
    agent_manager = providers.Singleton(AgentManager)

# ❌ 削除された設定（Agent内で実装）
# childcare_adviser = ...  # 削除
# safety_assessor = ...   # 削除
# age_detector = ...      # 削除
# childcare_consultation_tool = ...  # 削除
```

#### **6. chat.pyルーティングパターン**

```python
# ✅ Agent中心ルーティング
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """AgentManager中心のシンプルルーティング"""
    
    # AgentManagerでマルチエージェント処理
    response_text = _agent_manager.route_query(request.message)
    
    return ChatResponse(response=response_text, ...)

# ❌ 旧パターン（削除済み）
# tool = _container.childcare_consultation_tool()  # 削除
# tool_result = tool(message=request.message)      # 削除
```

#### **7. 新機能実装時のチェックリスト**

**新機能実装前に確認**：

- [ ] この機能はAgentで実装すべきか？（判断・アドバイス系は YES）
- [ ] この機能は技術的機能か？（画像・音声・ファイル・記録系は YES）
- [ ] 既存のAgent機能と重複していないか？
- [ ] Tool/UseCaseにビジネスロジックを含んでいないか？
- [ ] Protocol定義にビジネス概念が含まれていないか？

#### **8. 違反パターンの検出方法**

**以下を発見したら即座に修正**：

```python
# 🚨 違反パターン検出
- "childcare"という名前のtool/usecase/protocol実装
- "development"という名前のtool/usecase/protocol実装
- "safety"という名前のtool/usecase/protocol実装
- "age"という名前のtool/usecase/protocol実装
- "advice"という名前のtool/usecase/protocol実装

# 🚨 引数の違反パターン
def some_function(child_id: str, advice_type: str):  # ビジネス概念
def some_function(user_consultation: str):          # ビジネス概念
```

#### **9. アーキテクチャ進化の方向性**

```
現在（Agent中心）:
Agent（Gemini判断） + Tool（マルチモーダル技術）

将来（さらにシンプル化）:
Agent（Gemini判断） + 最小限のTool
```

**結論**: Agentが中心となり、Tool/UseCase/Infrastructureは純粋な技術機能（画像・音声・ファイル・記録）のみに特化。ビジネスロジック・判断・アドバイス生成はすべてGemini-poweredなAgentが担当。