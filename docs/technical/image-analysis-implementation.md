# 画像分析機能実装ガイド

子育て支援AI画像分析機能の包括的な実装ドキュメント

## 🎯 概要

GenieUsシステムにおける画像分析機能は、親御さんがアップロードした子どもの写真をAIが分析し、発達状況・安全性・栄養状態などについて専門的なアドバイスを提供する機能です。

### 主要機能
- 子どもの表情・感情分析
- 食事内容・栄養バランス評価
- 安全性チェック（誤飲リスク、環境安全性等）
- 発達段階に応じたアドバイス生成
- フォローアップ質問の自動提案

## 🏗️ システム全体アーキテクチャ

```
Frontend (Next.js) → Backend API → Agent Routing → Image Analysis Tool → Gemini AI
     ↓                    ↓              ↓                ↓              ↓
画像アップロード    ファイル保存    image_specialist   analyze_child_image  画像解析実行
```

## 📱 フロントエンド実装

### ファイル構成
- **メインコンポーネント**: `frontend/src/app/chat/page.tsx`
- **API統合**: `frontend/src/libs/api/file-upload.ts`
- **進捗表示**: `frontend/src/components/features/chat/genie-style-progress.tsx`

### 画像アップロード処理

#### 1. 画像選択とプレビュー
```typescript
// frontend/src/app/chat/page.tsx
const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0]
  if (file) {
    setSelectedImage(file)
    const reader = new FileReader()
    reader.onload = (e) => setImagePreview(e.target?.result as string)
    reader.readAsDataURL(file)
  }
}
```

#### 2. ローカルファイルパス取得
```typescript
// 重要: 実際のファイルパスを取得する関数
const getLocalFilePath = async (file: File): Promise<string | null> => {
  try {
    const uploadResult = await uploadImage(file, 'frontend_user')
    if (uploadResult.success && uploadResult.file_url) {
      const filename = uploadResult.file_url.split('/').pop()
      // バックエンドの実際のファイルパス構造に合わせる
      const localFilePath = `/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/${filename}`
      return localFilePath
    }
    return null
  } catch (error) {
    console.error('ファイルアップロードエラー:', error)
    return null
  }
}
```

#### 3. ストリーミングチャットAPI呼び出し
```typescript
const streamingMessage: Message = {
  id: streamingMessageId,
  content: JSON.stringify({
    message: finalStreamingMessage, // 強制ルーティング指示付き
    conversation_history: conversationHistory,
    session_id: sessionId,
    user_id: 'frontend_user',
    family_info: familyInfo,
    // 🎯 重要: 画像関連パラメータ
    message_type: 'image',           // メッセージタイプ
    has_image: true,                 // 画像添付フラグ
    image_path: imagePath,           // 実際のローカルファイルパス
    multimodal_context: {
      type: 'image',
      image_description: 'ユーザーが画像をアップロードしました'
    },
    web_search_enabled: false
  })
}
```

### 強制ルーティング指示
```typescript
// 画像添付時の特別なメッセージ構造
const finalStreamingMessage = `🖼️ FORCE_IMAGE_ANALYSIS_ROUTING 🖼️
SYSTEM_INSTRUCTION: この画像は必ず画像分析エージェント(image_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
画像添付時は画像分析を最優先してください。
コーディネーターをスキップして直接image_specialistにルーティングしてください。
画像分析要求: ${query || '画像を分析してください'}
END_SYSTEM_INSTRUCTION`
```

## 🖥️ バックエンド実装

### ファイル構成
- **ファイルアップロードAPI**: `backend/src/presentation/api/routes/file_upload.py`
- **ストリーミングチャットAPI**: `backend/src/presentation/api/routes/streaming_chat.py`
- **ルーティング実行**: `backend/src/agents/routing_executor.py`
- **メッセージ処理**: `backend/src/agents/message_processor.py`

### 1. ファイルアップロードAPI

#### エンドポイント: `/api/upload-image`
```python
@router.post("/upload-image")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    user_id: str = Form(default="default_user"),
    file_manager: FileManagementTool = Depends(get_file_management_tool),
    logger: logging.Logger = Depends(get_logger),
):
    """画像ファイルアップロード（マルチパート形式）"""
    
    # ファイル保存処理
    result = file_manager.save_uploaded_image(
        file_content=await file.read(),
        filename=file.filename,
        user_id=user_id,
    )
    
    # レスポンス
    return {
        "success": True,
        "file_url": f"/api/files/images/{result['filename']}",
        "filename": result['filename'],
        "message": "画像アップロード成功"
    }
```

#### ファイル保存処理
```python
# backend/src/tools/file_management_tool.py
def save_uploaded_image(self, file_content: bytes, filename: str, user_id: str) -> dict:
    """アップロードされた画像をローカルディスクに保存"""
    
    # 保存ディレクトリ: backend/src/data/uploads/images/
    upload_dir = self.base_path / "data" / "uploads" / "images"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # ユニークファイル名生成
    safe_filename = self._generate_unique_filename(filename)
    file_path = upload_dir / safe_filename
    
    # ファイル書き込み
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return {
        "success": True,
        "filename": safe_filename,
        "file_path": str(file_path),
        "user_id": user_id
    }
```

### 2. ストリーミングチャットAPI

#### データモデル
```python
class StreamingChatMessage(BaseModel):
    message: str
    user_id: str = "frontend_user"
    session_id: str = "default_session"
    conversation_history: list = []
    family_info: dict = None
    web_search_enabled: bool = False
    
    # 🎯 画像関連フィールド
    message_type: str = "text"      # "text", "image", "voice", "multimodal"
    has_image: bool = False         # 画像添付フラグ
    image_path: str = None          # ローカルファイルパスまたはBase64データ
    multimodal_context: dict = None # マルチモーダルコンテキスト情報
```

#### UseCase層への橋渡し
```python
@router.post("/streaming-chat")
async def streaming_chat_endpoint(
    chat_message: StreamingChatMessage,
    streaming_chat_usecase: StreamingChatUseCase = Depends(get_streaming_chat_usecase),
):
    # 🎯 画像関連パラメータをUseCaseに渡す
    async for data in streaming_chat_usecase.create_progress_stream(
        agent_manager,
        chat_message.message,
        chat_message.user_id,
        chat_message.session_id,
        chat_message.conversation_history or [],
        chat_message.family_info or {},
        chat_message.web_search_enabled,
        # 画像・マルチモーダル対応パラメータ
        chat_message.message_type,    # 🔑 重要
        chat_message.has_image,       # 🔑 重要  
        chat_message.image_path,      # 🔑 重要
        chat_message.multimodal_context,
    ):
        yield data
```

## 🤖 エージェント層実装

### ルーティング戦略

#### 1. 画像優先ルーティング
```python
# backend/src/agents/routing_executor.py
def _determine_agent_type(
    self, 
    message: str, 
    conversation_history: list | None = None,
    family_info: dict | None = None,
    has_image: bool = False,
    message_type: str = "text"
) -> str:
    # 🖼️ **最優先**: 画像添付検出（戦略に依存しない）
    if has_image or message_type == "image":
        self.logger.info(f"🎯 RoutingExecutor: 画像添付最優先検出 has_image={has_image}, message_type={message_type} → image_specialist")
        return "image_specialist"
    
    # 他のルーティングロジック...
```

### MessageProcessor - コンテキスト生成

#### 画像情報の詳細指示生成
```python
# backend/src/agents/message_processor.py
def create_message_with_context(
    self,
    message: str,
    conversation_history: list[dict] | None = None,
    family_info: dict | None = None,
    image_path: str = None,           # 🔑 重要パラメータ
    multimodal_context: dict = None,
) -> str:
    # 画像情報セクション（画像がある場合）
    if image_path:
        # ファイルパスかBase64データかを判定
        if image_path.startswith("data:image/"):
            data_type = "Base64データ"
        elif "/" in image_path or "\\" in image_path:
            data_type = "ファイルパス"
        else:
            data_type = "不明な形式"
        
        # 🎯 重要: AIに実際のファイルパスを明示的に指示
        image_text = f"【画像情報】\n画像タイプ: 子どもの写真が添付されています（{data_type}）\n"
        image_text += f"画像パス: {image_path}\n"
        image_text += f"分析指示: analyze_child_imageツールを使用して、上記の画像パス（{image_path}）を指定して画像を分析してください\n"
        
        context_parts.append(image_text)
```

## 🔧 画像分析ツール実装

### ファイル構成
- **画像分析ツール**: `backend/src/tools/image_analysis_tool.py`
- **UseCase**: `backend/src/application/usecases/image_analysis_usecase.py`
- **Gemini統合**: `backend/src/infrastructure/external_services/gemini_image_analyzer.py`

### 1. 画像分析ツール
```python
# backend/src/tools/image_analysis_tool.py
async def analyze_child_image(image_path: str, child_id: str = "default_child", analysis_type: str = "general") -> dict:
    """子どもの画像を分析"""
    
    # 🔑 重要: ローカルファイルパス処理
    if _is_local_file_path(image_path):
        self.logger.info(f"ローカルファイルパス検出: {image_path}")
        
        # セキュリティチェック
        if not _is_safe_file_path(image_path):
            raise ValueError(f"不正なファイルパス: {image_path}")
        
        # ローカルファイルをBase64に変換
        base64_image = _read_local_file_as_base64(image_path)
        if not base64_image:
            raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
        
        # UseCaseに渡すのはBase64データ
        result = await self.image_analysis_usecase.analyze_child_image(
            image_data=base64_image,  # Base64変換済み
            child_id=child_id,
            analysis_type=analysis_type
        )
    else:
        # Base64データの場合はそのまま渡す
        result = await self.image_analysis_usecase.analyze_child_image(
            image_data=image_path,
            child_id=child_id,
            analysis_type=analysis_type
        )
```

#### セキュリティ関数
```python
def _is_local_file_path(image_path: str) -> bool:
    """ローカルファイルパスかBase64データかを判定"""
    if image_path.startswith("data:image/"):
        return False
    if "/" in image_path or "\\" in image_path:
        return True
    return False

def _is_safe_file_path(file_path: str) -> bool:
    """パストラバーサル攻撃対策"""
    uploads_dir = Path(__file__).parent.parent / "data" / "uploads"
    
    try:
        resolved_path = Path(file_path).resolve()
        uploads_dir_resolved = uploads_dir.resolve()
        
        # アップロードディレクトリ配下かチェック
        return str(resolved_path).startswith(str(uploads_dir_resolved))
    except Exception:
        return False
```

### 2. 画像分析UseCase
```python
# backend/src/application/usecases/image_analysis_usecase.py
async def analyze_child_image(
    self, 
    image_data: str,           # Base64画像データ
    child_id: str = "default_child", 
    analysis_type: str = "general"
) -> dict:
    """子どもの画像分析ビジネスロジック"""
    
    try:
        # Gemini画像分析サービス呼び出し
        analysis_result = await self.gemini_analyzer.analyze_image_with_prompt(
            image_data=image_data,
            custom_prompt=self._create_analysis_prompt(analysis_type)
        )
        
        # 結果の構造化・バリデーション
        structured_result = self._structure_analysis_result(analysis_result, child_id)
        
        # 安全性チェック
        safety_result = self._validate_analysis_result(structured_result)
        
        return {
            **structured_result,
            **safety_result,
            "timestamp": datetime.now().isoformat(),
            "ai_model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        self.logger.error(f"画像分析エラー: {e}")
        return self._create_error_response(str(e))
```

### 3. Gemini統合サービス
```python
# backend/src/infrastructure/external_services/gemini_image_analyzer.py
async def analyze_image_with_prompt(self, image_data: str, custom_prompt: str = None) -> dict:
    """Gemini APIで画像解析実行"""
    
    # Base64データから画像読み込み
    if image_data.startswith("data:image/"):
        # Base64ヘッダー除去
        header, base64_str = image_data.split(",", 1)
        image_bytes = base64.b64decode(base64_str)
        
        # PIL Imageに変換
        image = Image.open(io.BytesIO(image_bytes))
        self.logger.info(f"Base64画像データから画像を読み込み成功: サイズ={image.size}")
    
    # Gemini APIコール
    response = await self.model.generate_content_async([
        custom_prompt or self.default_prompt,
        image
    ])
    
    # JSON解析
    return self._parse_response_to_json(response.text)
```

## 📊 データフロー詳細

### 1. フロントエンド → バックエンド
```
画像ファイル選択
    ↓
FileReader.readAsDataURL() でプレビュー生成
    ↓  
uploadImage() でファイルアップロードAPI呼び出し
    ↓
ローカルファイルパス取得: /Users/.../backend/src/data/uploads/images/{uuid}.jpg
    ↓
ストリーミングチャットAPI呼び出し（image_path含む）
```

### 2. バックエンド内部処理
```
ストリーミングチャットAPI受信
    ↓
StreamingChatUseCase.create_progress_stream()
    ↓
RoutingExecutor.execute_with_routing()
    ↓
has_image=True 検出 → image_specialist選択
    ↓
MessageProcessor.create_message_with_context()
    ↓
「analyze_child_imageツールを使用して、{image_path}を分析」指示生成
    ↓
image_specialist Agent実行
```

### 3. エージェント → ツール実行
```
image_specialist Agent
    ↓
「analyze_child_image」ツール実行指示認識
    ↓
ImageAnalysisTool.analyze_child_image(image_path="実際のファイルパス")
    ↓
ローカルファイル読み取り → Base64変換
    ↓
ImageAnalysisUseCase.analyze_child_image(image_data="base64...")
    ↓
GeminiImageAnalyzer.analyze_image_with_prompt()
    ↓
Gemini AI実行 → 結果返却
```

## 🔍 重要な実装ポイント

### 1. グローバル変数排除
**旧実装（問題あり）**:
```python
# ❌ グローバル変数使用（非推奨）
_current_image_path = None

def set_current_image_path(path: str):
    global _current_image_path
    _current_image_path = path
```

**新実装（推奨）**:
```python
# ✅ ローカルファイルパス直接処理
def analyze_child_image(image_path: str):
    if _is_local_file_path(image_path):
        base64_image = _read_local_file_as_base64(image_path)
        # 処理続行...
```

### 2. MessageProcessorでの明示的指示
**重要**: AIが確実に正しいファイルパスを使用するよう、明示的な指示を生成
```python
image_text += f"分析指示: analyze_child_imageツールを使用して、上記の画像パス（{image_path}）を指定して画像を分析してください\n"
```

### 3. セキュリティ対策
- **パストラバーサル攻撃対策**: アップロードディレクトリ配下のファイルのみアクセス許可
- **ファイル形式検証**: 画像ファイルのみ受け入れ
- **ファイルサイズ制限**: 大容量ファイル防止

### 4. エラーハンドリング
- **ファイル不存在**: 適切なエラーメッセージとフォールバック
- **画像解析失敗**: Gemini APIエラー時の代替処理
- **ネットワークエラー**: 再試行機能付きエラーハンドリング

## 🧪 テスト方法

### 1. 単体テスト
```python
# テストファイル例
async def test_image_analysis_tool():
    tool = ImageAnalysisTool()
    
    # ローカルファイルパステスト
    result = await tool.analyze_child_image(
        image_path="/path/to/test/image.jpg",
        child_id="test_child"
    )
    
    assert result["success"] == True
    assert "detected_items" in result
```

### 2. 統合テスト
```bash
# テストスクリプト実行
cd backend
python test_direct_image_analysis.py
```

### 3. フロントエンド テスト
```bash
# 開発サーバー起動後、手動テスト
cd frontend && npm run dev
# http://localhost:3000/chat で画像アップロードテスト
```

## 🚀 運用時の考慮事項

### 1. パフォーマンス
- **画像サイズ最適化**: アップロード前のリサイズ検討
- **キャッシュ戦略**: 同一画像の再分析防止
- **非同期処理**: 大きな画像の処理時間対策

### 2. スケーラビリティ
- **ファイルストレージ**: ローカルディスクからクラウドストレージへの移行検討
- **負荷分散**: 複数インスタンス間でのファイル共有
- **データベース連携**: 分析結果の永続化

### 3. セキュリティ
- **アクセス制御**: ユーザー毎のファイルアクセス制限
- **暗号化**: 機密性の高い画像データの暗号化保存
- **監査ログ**: ファイルアクセス履歴の記録

## 📚 関連ドキュメント

- [ADKベストプラクティス](./adk-best-practices.md)
- [FastAPI DI統合](./fastapi-di-integration.md)
- [新エージェント作成ガイド](../guides/new-agent-creation.md)
- [新ツール開発ガイド](../guides/new-tool-development.md)

---

**最終更新**: 2025-06-28  
**バージョン**: 1.0.0  
**作成者**: Claude Code AI Assistant