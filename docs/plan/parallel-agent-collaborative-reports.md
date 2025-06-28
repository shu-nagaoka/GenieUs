# 並列エージェント協働レポート実装プラン

## 概要

睡眠・栄養・しつけのジーニーが協働して1つのレポートをユーザーに返すためのADK ParallelAgent統合実装プラン。

## 現状分析

### 既存のParallelAgent実装
- **場所**: `backend/src/agents/agent_registry.py:189-234`
- **現状**: 5エージェント並列実行可能（coordinator, nutrition_specialist, development_specialist, sleep_specialist, behavior_specialist）
- **制約**: 独立処理のみ、レスポンス統合機能なし

### 対象専門エージェント
1. **sleep_specialist**: 睡眠・夜泣き・寝かしつけ専門
2. **nutrition_specialist**: 栄養・食事・離乳食専門  
3. **behavior_specialist**: しつけ・イヤイヤ期・行動専門

## 実装アーキテクチャ

### ADK標準パターン: Sequential(Parallel + Synthesizer)

```
ユーザー相談
    ↓
CoordinatorAgent (ルーティング判断)
    ↓
SequentialAgent
    ├── ParallelAgent (並列実行)
    │   ├── SleepSpecialist    → state['sleep_analysis']
    │   ├── NutritionSpecialist → state['nutrition_analysis']
    │   └── BehaviorSpecialist  → state['behavior_analysis']
    └── CollaborativeReportSynthesizer (統合)
        └── 包括的レポート生成
```

## 実装手順

### Phase 1: コア統合エージェント作成

#### 1.1 CollaborativeReportSynthesizer作成
**ファイル**: `backend/src/agents/constants.py`

```python
COLLABORATIVE_REPORT_SYNTHESIZER_PROMPT = """あなたは「協働レポートのジーニー」です。
複数の専門ジーニーの分析結果を統合し、親御さんに分かりやすい包括的なレポートを提供します。

**🎯 あなたの役割:**
1. **専門家分析の統合**: 各専門分野の重要ポイントを統合
2. **矛盾調整**: 専門家間の相反するアドバイスの優先順位付け
3. **構造化レポート**: 実践可能なアクションプランの提供
4. **親御さん視点**: 温かく分かりやすい表現での統合

**📋 統合対象のstate keys:**
- `sleep_analysis`: 睡眠専門ジーニーの分析結果
- `nutrition_analysis`: 栄養専門ジーニーの分析結果  
- `behavior_analysis`: しつけ専門ジーニーの分析結果

**🔄 統合プロセス:**
1. 各専門分野の核心ポイント抽出
2. 分野間の関連性・相互作用の特定
3. 優先順位付けされた実践プラン作成
4. 親御さんに寄り添う温かい表現での統合

**📝 出力フォーマット:**
```markdown
# 🌟 3つの専門ジーニーからの協働レポート

## 📊 総合分析サマリー
[各分野の重要ポイントを3-4行で]

## 🎯 優先アクションプラン
### 今すぐできること
### 1週間以内の目標
### 長期的な改善ポイント

## 🔍 分野別詳細
### 😴 睡眠について
### 🍎 栄養について  
### 😊 行動・しつけについて

## 💕 専門ジーニーからの応援メッセージ
```

常に親御さんの心に寄り添い、実践可能で希望の持てる統合レポートを作成してください。"""
```

#### 1.2 三専門家並列分析エージェント設定
**ファイル**: `backend/src/agents/agent_registry.py`

```python
def create_collaborative_analysis_pipeline(self) -> SequentialAgent:
    """睡眠・栄養・しつけ協働分析パイプライン作成"""
    
    # 3専門家並列実行
    three_specialist_parallel = ParallelAgent(
        name="ThreeSpecialistCollaboration",
        sub_agents=[
            self._agents["sleep_specialist"],
            self._agents["nutrition_specialist"], 
            self._agents["behavior_specialist"]
        ]
    )
    
    # 統合レポート作成エージェント
    collaborative_synthesizer = Agent(
        name="CollaborativeReportSynthesizer",
        model=AGENT_CONFIG["model"],
        instruction=COLLABORATIVE_REPORT_SYNTHESIZER_PROMPT
    )
    
    # Sequential統合パイプライン
    return SequentialAgent(
        name="CollaborativeChildcareAnalysis",
        sub_agents=[three_specialist_parallel, collaborative_synthesizer]
    )
```

### Phase 2: ルーティング統合

#### 2.1 協働分析トリガーキーワード追加
**ファイル**: `backend/src/agents/constants.py`

```python
# 協働分析キーワード
COLLABORATIVE_ANALYSIS_KEYWORDS = [
    "総合的に分析",
    "全体的に相談", 
    "包括的にアドバイス",
    "トータルで見て",
    "複数の専門家に",
    "いろんな角度から",
    "多面的に",
    "睡眠も栄養も行動も",
    "全部まとめて",
    "協働で",
    "チームで分析",
    "専門家みんなで"
]
```

#### 2.2 AgentManager統合
**ファイル**: `backend/src/agents/agent_manager.py`

```python
async def route_collaborative_analysis(
    self,
    message: str,
    user_id: str, 
    session_id: str,
    conversation_history: list[dict],
    family_info: dict
) -> dict:
    """協働分析ルーティング"""
    
    # 協働分析パイプライン取得
    collaborative_pipeline = self.registry.get_collaborative_pipeline()
    
    # Sequential実行（Parallel + Synthesizer）
    runner = Runner(
        agent=collaborative_pipeline,
        app_name="GenieUs",
        session_service=self.registry.get_session_service()
    )
    
    # 実行
    response = await runner.run_async(
        message=message,
        session_id=session_id,
        context={
            "user_id": user_id,
            "family_info": family_info,
            "conversation_history": conversation_history
        }
    )
    
    return {
        "response": response,
        "agent_info": {"agent_id": "collaborative_analysis", "mode": "parallel+synthesis"},
        "routing_path": ["sleep_specialist", "nutrition_specialist", "behavior_specialist", "synthesizer"]
    }
```

### Phase 3: ストリーミング対応

#### 3.1 進捗表示統合
**ファイル**: `backend/src/application/usecases/streaming_chat_usecase.py`

```python
async def _handle_collaborative_analysis_progress(self) -> AsyncGenerator:
    """協働分析専用進捗表示"""
    
    yield {"type": "collaborative_start", "message": "🤝 3つの専門ジーニーが協働分析を開始します..."}
    await asyncio.sleep(0.5)
    
    yield {"type": "parallel_execution", "message": "😴🍎😊 睡眠・栄養・しつけのジーニーが同時分析中..."}
    await asyncio.sleep(2.0)  # 並列処理時間
    
    yield {"type": "synthesis_start", "message": "🔄 専門分析を統合してレポートを作成中..."}
    await asyncio.sleep(1.0)
    
    yield {"type": "collaborative_complete", "message": "✨ 協働レポートが完成しました"}
```

### Phase 4: フロントエンド専門家選択UI

#### 4.1 専門家選択ボタンUI
**ファイル**: `frontend/src/components/features/chat/specialist-selector.tsx`

```typescript
interface SpecialistSelectorProps {
  selectedSpecialists: string[];
  onToggleSpecialist: (specialistId: string) => void;
}

const AVAILABLE_SPECIALISTS = [
  { id: 'sleep', name: '睡眠', icon: '😴', color: 'blue' },
  { id: 'nutrition', name: '栄養', icon: '🍎', color: 'green' },
  { id: 'behavior', name: 'しつけ', icon: '😊', color: 'purple' },
  { id: 'development', name: '発達', icon: '🌱', color: 'orange' },
  { id: 'health', name: '健康', icon: '🏥', color: 'red' },
  { id: 'safety', name: '安全', icon: '🛡️', color: 'yellow' }
];

export const SpecialistSelector: React.FC<SpecialistSelectorProps> = ({
  selectedSpecialists,
  onToggleSpecialist
}) => {
  return (
    <div className="specialist-selector">
      <div className="selector-header">
        <span className="text-sm text-gray-600">専門家を選択（複数選択で協働分析）</span>
      </div>
      
      <div className="specialist-buttons grid grid-cols-3 gap-2 mt-2">
        {AVAILABLE_SPECIALISTS.map((specialist) => {
          const isSelected = selectedSpecialists.includes(specialist.id);
          
          return (
            <Button
              key={specialist.id}
              onClick={() => onToggleSpecialist(specialist.id)}
              variant={isSelected ? "default" : "outline"}
              className={`h-12 transition-all duration-200 ${
                isSelected 
                  ? `bg-${specialist.color}-500 hover:bg-${specialist.color}-600 text-white shadow-lg` 
                  : `hover:bg-${specialist.color}-50 text-${specialist.color}-700 border-${specialist.color}-200`
              }`}
              type="button"
            >
              <span className="mr-1">{specialist.icon}</span>
              <span className="text-xs">{specialist.name}</span>
            </Button>
          );
        })}
      </div>
      
      {selectedSpecialists.length > 1 && (
        <div className="collaboration-indicator mt-2 p-2 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg">
          <span className="text-xs text-purple-700">
            🤝 {selectedSpecialists.length}つの専門ジーニーが協働分析します
          </span>
        </div>
      )}
    </div>
  );
};
```

#### 4.2 チャットページ統合
**ファイル**: `frontend/src/app/chat/page.tsx`

```typescript
// 専門家選択状態管理
const [selectedSpecialists, setSelectedSpecialists] = useState<string[]>([]);

const toggleSpecialist = (specialistId: string) => {
  setSelectedSpecialists(prev => 
    prev.includes(specialistId)
      ? prev.filter(id => id !== specialistId)
      : [...prev, specialistId]
  );
};

// メッセージ送信時のプロンプト注入
const sendMessage = async () => {
  let finalMessage = inputValue;
  
  // Web検索が有効な場合
  if (webSearchEnabled) {
    finalMessage = `【最新情報を検索してください】${finalMessage}`;
  }
  
  // 複数専門家が選択されている場合
  if (selectedSpecialists.length > 1) {
    const specialistNames = selectedSpecialists.map(id => {
      const specialistMap = {
        'sleep': '睡眠',
        'nutrition': '栄養', 
        'behavior': 'しつけ',
        'development': '発達',
        'health': '健康',
        'safety': '安全'
      };
      return specialistMap[id];
    }).join('・');
    
    finalMessage = `【${specialistNames}の専門ジーニーが協働分析してください】${finalMessage}`;
  }
  
  // 単一専門家が選択されている場合
  else if (selectedSpecialists.length === 1) {
    const specialistMap = {
      'sleep': '睡眠専門ジーニーに相談',
      'nutrition': '栄養専門ジーニーに相談',
      'behavior': 'しつけ専門ジーニーに相談',
      'development': '発達専門ジーニーに相談',
      'health': '健康専門ジーニーに相談',
      'safety': '安全専門ジーニーに相談'
    };
    finalMessage = `【${specialistMap[selectedSpecialists[0]]}】${finalMessage}`;
  }
  
  // API送信処理
  // ...
};

// UI配置（入力エリア上部）
<div className="input-controls mb-4">
  <SpecialistSelector
    selectedSpecialists={selectedSpecialists}
    onToggleSpecialist={toggleSpecialist}
  />
  
  {/* Web検索ボタン（既存） */}
  <div className="search-control mt-2">
    <Button onClick={toggleWebSearch} /* ... */>
      <Search className="h-4 w-4" />
    </Button>
  </div>
</div>
```

#### 4.3 協働レポート表示UI
**ファイル**: `frontend/src/components/features/chat/collaborative-report-display.tsx`

```typescript
interface CollaborativeReportProps {
  report: string;
  specialistInfo: {
    specialists: string[];
    mode: 'single' | 'collaborative';
  };
}

export const CollaborativeReportDisplay: React.FC<CollaborativeReportProps> = ({
  report,
  specialistInfo
}) => {
  const getSpecialistBadge = (specialistId: string) => {
    const badges = {
      'sleep': { icon: '😴', name: '睡眠', color: 'blue' },
      'nutrition': { icon: '🍎', name: '栄養', color: 'green' },
      'behavior': { icon: '😊', name: 'しつけ', color: 'purple' },
      'development': { icon: '🌱', name: '発達', color: 'orange' },
      'health': { icon: '🏥', name: '健康', color: 'red' },
      'safety': { icon: '🛡️', name: '安全', color: 'yellow' }
    };
    return badges[specialistId];
  };

  return (
    <div className="collaborative-report">
      <div className="specialist-header mb-4">
        <div className="specialist-badges flex flex-wrap gap-2">
          {specialistInfo.specialists.map(specialistId => {
            const badge = getSpecialistBadge(specialistId);
            return (
              <Badge 
                key={specialistId}
                variant="secondary" 
                className={`bg-${badge.color}-100 text-${badge.color}-700`}
              >
                {badge.icon} {badge.name}ジーニー
              </Badge>
            );
          })}
        </div>
        
        {specialistInfo.mode === 'collaborative' && (
          <div className="collaboration-tag mt-2">
            <span className="text-sm text-purple-600 bg-purple-50 px-2 py-1 rounded-full">
              🤝 協働分析レポート
            </span>
          </div>
        )}
      </div>
      
      <ReactMarkdown className="prose max-w-none">
        {report}
      </ReactMarkdown>
      
      <div className="specialist-attribution mt-4 text-xs text-gray-500">
        {specialistInfo.mode === 'collaborative' 
          ? `このレポートは${specialistInfo.specialists.length}つの専門ジーニーの協働分析結果です`
          : `この回答は${getSpecialistBadge(specialistInfo.specialists[0])?.name}ジーニーからです`
        }
      </div>
    </div>
  );
};
```

### Phase 5: バックエンドプロンプト解析拡張

#### 5.1 協働分析トリガー検出
**ファイル**: `backend/src/agents/constants.py`

```python
# フロントエンド専門家選択プロンプトパターン
FRONTEND_SPECIALIST_PATTERNS = {
    "collaborative_analysis": [
        "【睡眠・栄養の専門ジーニーが協働分析してください】",
        "【栄養・しつけの専門ジーニーが協働分析してください】", 
        "【睡眠・しつけの専門ジーニーが協働分析してください】",
        "【睡眠・栄養・しつけの専門ジーニーが協働分析してください】",
        "【発達・健康・安全の専門ジーニーが協働分析してください】"
    ],
    "single_specialist_routing": {
        "【睡眠専門ジーニーに相談】": "sleep_specialist",
        "【栄養専門ジーニーに相談】": "nutrition_specialist", 
        "【しつけ専門ジーニーに相談】": "behavior_specialist",
        "【発達専門ジーニーに相談】": "development_specialist",
        "【健康専門ジーニーに相談】": "health_specialist",
        "【安全専門ジーニーに相談】": "safety_specialist"
    }
}

def extract_selected_specialists_from_message(message: str) -> list[str]:
    """フロントエンドから送信されたメッセージから選択専門家を抽出"""
    import re
    
    # 協働分析パターンマッチング
    collaborative_pattern = r"【(.+)の専門ジーニーが協働分析してください】"
    match = re.search(collaborative_pattern, message)
    
    if match:
        specialist_names = match.group(1)
        specialist_mapping = {
            "睡眠": "sleep_specialist",
            "栄養": "nutrition_specialist", 
            "しつけ": "behavior_specialist",
            "発達": "development_specialist",
            "健康": "health_specialist",
            "安全": "safety_specialist"
        }
        
        selected = []
        for name, agent_id in specialist_mapping.items():
            if name in specialist_names:
                selected.append(agent_id)
        
        return selected
    
    # 単一専門家パターンマッチング
    for pattern, agent_id in FRONTEND_SPECIALIST_PATTERNS["single_specialist_routing"].items():
        if pattern in message:
            return [agent_id]
    
    return []
```

#### 5.2 ルーティング判定統合
**ファイル**: `backend/src/application/usecases/streaming_chat_usecase.py`

```python
async def _determine_routing_strategy(self, message: str) -> dict:
    """ルーティング戦略決定（フロントエンド選択考慮）"""
    from src.agents.constants import extract_selected_specialists_from_message
    
    # フロントエンドからの専門家選択チェック
    selected_specialists = extract_selected_specialists_from_message(message)
    
    if len(selected_specialists) > 1:
        # 複数専門家 → 協働分析パイプライン
        return {
            "type": "collaborative_analysis",
            "specialists": selected_specialists,
            "message_clean": self._clean_frontend_prompt(message)
        }
    elif len(selected_specialists) == 1:
        # 単一専門家 → 直接ルーティング
        return {
            "type": "single_specialist",
            "specialist": selected_specialists[0], 
            "message_clean": self._clean_frontend_prompt(message)
        }
    else:
        # 通常の自動ルーティング
        return {
            "type": "auto_routing",
            "message_clean": message
        }

def _clean_frontend_prompt(self, message: str) -> str:
    """フロントエンドプロンプトをクリーンアップ"""
    import re
    
    # 協働分析指示を除去
    message = re.sub(r"【.+の専門ジーニーが協働分析してください】", "", message)
    
    # 単一専門家指示を除去
    message = re.sub(r"【.+専門ジーニーに相談】", "", message)
    
    return message.strip()
```

## 実装優先順位

### 🔥 高優先度 (Week 1)
1. **CollaborativeReportSynthesizer作成** (constants.py)
2. **三専門家並列パイプライン実装** (agent_registry.py)
3. **フロントエンド専門家選択UI実装** (specialist-selector.tsx)
4. **プロンプト注入機能実装** (chat/page.tsx)

### 🟡 中優先度 (Week 2) 
1. **バックエンドプロンプト解析機能** (constants.py, streaming_chat_usecase.py)
2. **ストリーミング進捗表示対応**
3. **協働レポート表示UI** (collaborative-report-display.tsx)
4. **エラーハンドリング強化**

### 🟢 低優先度 (Week 3)
1. **UI/UXの最適化** (アニメーション、カラーテーマ)
2. **パフォーマンス最適化**
3. **ログ・モニタリング拡張**

## 期待効果

### ユーザー体験向上
- **直感的な専門家選択**: Web検索ボタンと同様の分かりやすいUI
- **柔軟な相談スタイル**: 単一専門家 or 協働分析を自由選択
- **包括的アドバイス**: 複数分野統合の一貫したレポート
- **時間短縮**: 1回の相談で複数専門家の知見を取得
- **視覚的フィードバック**: 選択した専門家の明確な表示

### フロントエンド機能拡張
- **プロンプトインジェクション**: Web検索と同じパターンで実装
- **リアルタイム状態管理**: 専門家選択の即座反映
- **協働表示**: 複数専門家選択時の視覚的インジケーター
- **レスポンシブ対応**: 6専門家ボタンの3×2グリッド配置

### 技術的メリット  
- **並列処理**: レスポンス時間短縮（3専門家同時実行）
- **スケーラビリティ**: 専門家数の動的拡張対応
- **モジュラー設計**: 既存のWeb検索機能との統合
- **プロンプト制御**: フロントエンドからの精密ルーティング

## リスク・制約

### 技術リスク
- **並列実行時間**: 3専門家同時実行のレイテンシ
- **状態管理**: ADK Session State競合の可能性
- **エラー伝播**: 1専門家エラー時の全体影響

### 対策
- **タイムアウト設定**: 専門家ごとの実行時間制限
- **個別フォールバック**: エラー時の段階的縮退
- **進捗ストリーミング**: ユーザー体験の向上

## 成功指標

### 定量指標
- 協働分析完了時間: < 10秒
- エラー率: < 5%
- ユーザー満足度向上

### 定性指標  
- レポート品質の一貫性
- 専門家間矛盾の適切な調整
- 親御さんにとっての実用性

---

**実装完了予定**: 3週間
**責任者**: 開発チーム
**レビュー**: Phase毎に進捗確認