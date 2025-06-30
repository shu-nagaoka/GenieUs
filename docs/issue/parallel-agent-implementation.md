# Issue: パラレルエージェント機能実装

**Issue ID**: PAR-001
**優先度**: High
**カテゴリ**: フルスタック新機能開発

## 📋 概要

3つの専門エージェントが同時にパラレル処理で動作し、ユーザーの悩みに対して協働回答する「マルチエージェントモード」を実装する。

## 🎯 目的

- **ユーザー体験向上**: 複数の専門家からの包括的な回答を得られる
- **ADKパラレル機能活用**: 既存のADK基盤を最大限活用
- **音声ボタン再活用**: 使用されていない音声ボタンをマルチエージェントモード切り替えに転用

## 🔍 現状分析

### **既存の技術基盤**

1. **パラレル処理基盤**:
   - `agent_registry.py`にParallelAgent基本実装済み
   - coordinator, nutrition_specialist, development_specialist, sleep_specialist, behavior_specialistの5エージェント対応

2. **ADK統合**:
   - `adk_routing_coordinator.py`のtransfer_to_agent()機能
   - 意図ベースルーティング戦略実装済み
   - パラレル処理キーワード検出機能あり

3. **フロントエンド基盤**:
   - 音声ボタン基本実装済み（現在未使用）
   - 検索・カメラアイコン制御機能あり
   - 会話UIとメッセージ表示機能完備

### **実装が必要な部分**

1. **バックエンド**: レスポンス統合・協働分析機能
2. **フロントエンド**: マルチエージェントモードUI
3. **ルーティング**: パラレル処理への動的切り替え

## 🚀 実装プラン

### **Phase 1: バックエンド パラレル処理拡張**

#### **1.1 パラレルエージェント統合機能**

**ファイル**: `backend/src/agents/parallel_agent_coordinator.py` (新規作成)

```python
@dataclass
class ParallelAgentRequest:
    """パラレルエージェント処理リクエスト"""
    user_message: str
    selected_agents: list[str]
    user_id: str
    session_id: str

@dataclass  
class ParallelAgentResponse:
    """パラレルエージェント統合レスポンス"""
    agents_responses: dict[str, str]
    integrated_summary: str
    confidence_scores: dict[str, float]
    processing_time: float

class ParallelAgentCoordinator:
    """複数エージェントの並列実行と結果統合"""
    
    def __init__(self, agent_manager: AgentManager, logger: logging.Logger):
        self.agent_manager = agent_manager
        self.logger = logger
    
    async def execute_parallel_analysis(
        self, request: ParallelAgentRequest
    ) -> ParallelAgentResponse:
        """複数エージェントでの並列分析実行"""
        # 1. 各エージェントで並列処理
        # 2. 結果統合とサマリー生成
        # 3. 信頼度スコア計算
```

#### **1.2 ADKルーティング拡張**

**ファイル**: `backend/src/agents/routing_executor.py` (既存拡張)

```python
async def execute_parallel_routing(
    self, 
    message: str, 
    forced_agents: list[str] | None = None
) -> dict[str, Any]:
    """強制パラレルモード実行"""
    if forced_agents:
        # マルチエージェントモード: 指定エージェントで並列実行
        return await self._execute_forced_parallel(message, forced_agents)
    
    # 通常のパラレル判定ロジック
    return await self._execute_auto_parallel(message)
```

### **Phase 2: フロントエンド マルチエージェントモードUI**

#### **2.1 音声ボタン→マルチエージェントボタン変更**

**ファイル**: `frontend/src/app/chat/page.tsx` (既存修正)

```typescript
// 音声ボタンを削除し、マルチエージェントモードボタンに変更
const [isMultiAgentMode, setIsMultiAgentMode] = useState(false)
const [selectedAgents, setSelectedAgents] = useState<string[]>([])

const toggleMultiAgentMode = () => {
  setIsMultiAgentMode(!isMultiAgentMode)
  if (!isMultiAgentMode) {
    // エージェント選択モーダル表示
    setShowAgentSelector(true)
  }
}

// マルチエージェントモードボタン
<Button 
  onClick={toggleMultiAgentMode}
  className={isMultiAgentMode ? "bg-purple-500" : ""}
>
  <Users className="h-4 w-4" />
  {isMultiAgentMode ? "マルチモード" : "エージェント"}
</Button>
```

#### **2.2 エージェント選択モーダル**

**ファイル**: `frontend/src/components/features/chat/agent-selector-modal.tsx` (新規作成)

```typescript
interface AgentSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onAgentsSelected: (agents: string[]) => void
  availableAgents: Agent[]
}

export function AgentSelectorModal({ 
  isOpen, 
  onClose, 
  onAgentsSelected,
  availableAgents 
}: AgentSelectorModalProps) {
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  
  // 3つまで選択可能
  const handleAgentToggle = (agentId: string) => {
    if (selectedAgents.length < 3 || selectedAgents.includes(agentId)) {
      // 選択/選択解除ロジック
    }
  }
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      {/* エージェント選択UI */}
    </Dialog>
  )
}
```

#### **2.3 マルチエージェント結果表示**

**ファイル**: `frontend/src/components/features/chat/multi-agent-response.tsx` (新規作成)

```typescript
interface MultiAgentResponseProps {
  response: {
    agents_responses: Record<string, string>
    integrated_summary: string
    confidence_scores: Record<string, number>
  }
}

export function MultiAgentResponse({ response }: MultiAgentResponseProps) {
  return (
    <div className="space-y-4">
      {/* 統合サマリー */}
      <Card className="bg-gradient-to-r from-purple-500 to-indigo-600">
        <CardContent>
          <h3>📊 統合分析結果</h3>
          <p>{response.integrated_summary}</p>
        </CardContent>
      </Card>
      
      {/* 各エージェントの個別回答 */}
      <div className="grid md:grid-cols-3 gap-4">
        {Object.entries(response.agents_responses).map(([agent, answer]) => (
          <Card key={agent}>
            <CardHeader>
              <Badge>{agent}</Badge>
              <Progress value={response.confidence_scores[agent] * 100} />
            </CardHeader>
            <CardContent>
              <p>{answer}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

### **Phase 3: API統合**

#### **3.1 パラレルエージェントAPI**

**ファイル**: `backend/src/presentation/api/routes/streaming_chat.py` (既存拡張)

```python
@router.post("/parallel-chat")
@inject
async def parallel_chat_endpoint(
    request: ParallelChatRequest,
    coordinator: ParallelAgentCoordinator = Depends(),
    logger: logging.Logger = Depends()
) -> ParallelChatResponse:
    """マルチエージェント並列チャット"""
    try:
        result = await coordinator.execute_parallel_analysis(request)
        return ParallelChatResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Parallel chat error: {e}")
        return ParallelChatResponse(success=False, error=str(e))
```

#### **3.2 フロントエンドAPI呼び出し**

**ファイル**: `frontend/src/libs/api/parallel-chat.ts` (新規作成)

```typescript
export interface ParallelChatRequest {
  message: string
  selectedAgents: string[]
  userId: string
  sessionId: string
}

export const useParallelChat = () => {
  return useMutation({
    mutationFn: async (request: ParallelChatRequest) => {
      const response = await fetch('/api/v1/parallel-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })
      return response.json()
    },
    onSuccess: (data) => {
      // パラレル回答の処理
    }
  })
}
```

## 🧪 テストプラン

### **Unit Tests**

1. **ParallelAgentCoordinator**のレスポンス統合機能
2. **AgentSelectorModal**の選択ロジック
3. **MultiAgentResponse**の表示機能

### **Integration Tests**

1. フロントエンド→バックエンドのパラレル処理フロー
2. 3エージェント同時実行とレスポンス統合
3. エラー時のフォールバック動作

### **UX Tests**

1. マルチエージェントモード切り替えの直感性
2. パラレル処理中のローディング表示
3. 検索・カメラアイコンの動的無効化

## 📊 成功指標

### **機能面**

- [ ] 3つの専門エージェントによる同時並列処理
- [ ] 統合回答の生成と適切な表示
- [ ] 音声ボタン→マルチエージェントボタンの置き換え
- [ ] マルチエージェントモード時の検索・カメラアイコン無効化

### **技術面**

- [ ] 既存コーディング規約100%準拠
- [ ] DI統合パターン完全適用
- [ ] 型アノテーション完備
- [ ] エラーハンドリング実装

### **性能面**

- [ ] パラレル処理時間 < 10秒
- [ ] UI応答性の維持
- [ ] メモリ使用量の最適化

## ⚠️ リスク・注意事項

### **技術リスク**

1. **ADK並列処理の制約**: 同時実行数の上限やレート制限
2. **レスポンス統合の複雑性**: 3つの異なる回答の適切な統合
3. **フロントエンド状態管理**: マルチエージェントモード状態の複雑性

### **UXリスク**

1. **処理時間の延長**: パラレル処理による待機時間増加
2. **情報過多**: 複数エージェントからの情報による混乱
3. **モード切り替えの複雑性**: ユーザーの学習コスト

### **対策**

1. **段階的実装**: Phase毎の動作確認
2. **プログレス表示**: パラレル処理中の進捗可視化
3. **フォールバック**: エラー時の単一エージェント処理

## 🔄 ロールバック計画

### **Phase 1失敗時**

- ParallelAgentCoordinatorの無効化
- 既存単一エージェント処理への自動フォールバック

### **Phase 2失敗時**

- 音声ボタンの復元
- マルチエージェントUI の一時無効化

### **Phase 3失敗時**

- 新規APIエンドポイントの無効化
- 既存チャットAPIのみ使用

## 📚 参考技術資料

1. **[ADK制約とベストプラクティス](../technical/adk-constraints-and-best-practices.md)**
2. **[コーディング規約](../development/coding-standards.md)**
3. **[アーキテクチャ概要](../architecture/overview.md)**
4. **[新エージェント作成](../guides/new-agent-creation.md)**

## 🔗 関連Issue

- 音声機能改善（未実装機能の活用）
- マルチモーダル対応強化
- ADKパフォーマンス最適化

---

**作成日**: 2025-06-29
**担当**: Claude Code AI
**レビュー**: 要実装前レビュー