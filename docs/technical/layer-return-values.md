# レイヤー別戻り値仕様書

## 📋 概要

GenieUs アーキテクチャにおける各レイヤーの戻り値形式を整理したドキュメント。
Clean Architecture パターンに基づき、UseCase 層と Tool 層の責務と戻り値を明確化。

## 🏗️ アーキテクチャ層構成

```
Tool Layer        ← 薄いアダプター（AI向けインターフェース）
    ↓
UseCase Layer     ← ビジネスロジック（核心処理）
    ↓
Infrastructure    ← 外部システム統合
```

## 📊 UseCase 層 戻り値仕様

### 基本形式

すべての UseCase メソッドは以下の統一形式で戻り値を返します：

| フィールド | 型     | 必須 | 説明                                           |
| ---------- | ------ | ---- | ---------------------------------------------- |
| `success`  | `bool` | ✅   | 処理成功フラグ                                 |
| `data`     | `Any`  | ❌   | 成功時のデータ（リスト・辞書・オブジェクト等） |
| `message`  | `str`  | ❌   | 処理結果メッセージ                             |
| `error`    | `str`  | ❌   | 失敗時のエラーメッセージ                       |
| `id`       | `str`  | ❌   | 作成・更新時の対象 ID                          |

### UseCase 別戻り値詳細

#### 🖼️ ImageAnalysisUseCase

```python
# analyze_child_image(image_path, child_id, analysis_context)
{
    "success": True,
    "detected_items": ["お子さんの笑顔", "健康的な表情"],
    "emotion_detected": "happy",
    "activity_type": "playing",
    "confidence": 0.85,
    "suggestions": ["引き続き遊びを見守りましょう"],
    "safety_concerns": []
}
```

#### 📈 GrowthRecordUseCase

```python
# create_growth_record(user_id, record_data)
{
    "success": True,
    "id": "growth_record_123",
    "data": {
        "child_name": "太郎",
        "title": "初歩き",
        "description": "10歩歩けました",
        "date": "2024-01-15",
        "type": "milestone"
    },
    "message": "成長記録を作成しました"
}

# get_growth_records(user_id, filters)
{
    "success": True,
    "data": [
        {
            "id": "growth_record_123",
            "child_name": "太郎",
            "title": "初歩き",
            "date": "2024-01-15"
        }
    ]
}
```

#### 🍽️ MealPlanManagementUseCase

```python
# create_meal_plan(request)
{
    "success": True,
    "plan_id": "meal_plan_456",
    "meal_plan": {
        "user_id": "user123",
        "title": "1週間の離乳食プラン",
        "week_start": "2024-01-15",
        "meals": {...},
        "nutrition_goals": {...}
    }
}

# get_user_meal_plans(user_id)
{
    "success": True,
    "meal_plans": [
        {
            "id": "meal_plan_456",
            "title": "1週間の離乳食プラン",
            "week_start": "2024-01-15"
        }
    ],
    "total_count": 1
}
```

#### 📅 ScheduleEventUseCase

```python
# create_schedule_event(user_id, event_data)
{
    "success": True,
    "id": "schedule_789",
    "data": {
        "title": "小児科検診",
        "date": "2024-01-20",
        "time": "14:00",
        "location": "ABC病院"
    }
}

# get_schedule_events(user_id, filters)
{
    "success": True,
    "data": [
        {
            "id": "schedule_789",
            "title": "小児科検診",
            "date": "2024-01-20",
            "time": "14:00"
        }
    ]
}
```

#### 🎤 VoiceAnalysisUseCase

```python
# analyze_child_voice(voice_path, child_id, analysis_context)
{
    "success": True,
    "transcription": "ママ、おなかすいた",
    "emotion_detected": "neutral",
    "language_analysis": {
        "vocabulary_level": "age_appropriate",
        "grammar_complexity": "simple"
    },
    "suggestions": ["語彙が豊富です"]
}
```

#### 📁 FileManagementUseCase

```python
# upload_file(file_data, metadata)
{
    "success": True,
    "file_id": "file_abc123",
    "url": "https://storage.googleapis.com/bucket/file_abc123.jpg",
    "metadata": {
        "filename": "photo.jpg",
        "size": 1024000,
        "mime_type": "image/jpeg"
    }
}
```

### ❌ エラー時の戻り値

```python
{
    "success": False,
    "error": "ファイルが見つかりません",
    "message": "指定されたIDのデータは存在しません"
}
```

## 🔧 Tool 層 戻り値仕様

Tool 層は**UseCase 層の戻り値を基にした薄いアダプター**として機能します。

### 基本変換パターン

#### パターン 1: 直接パススルー（推奨）

```python
# UseCase戻り値をそのまま返す
async def _create_growth_record(self, args):
    result = await self.growth_record_usecase.create_growth_record(...)
    return result  # UseCaseの戻り値をそのまま
```

#### パターン 2: 軽微な整形・メッセージ追加

```python
async def _analyze_child_image(self, args):
    result = await self.image_analysis_usecase.analyze_child_image(...)

    if result.get("success"):
        return {
            **result,  # UseCase戻り値を展開
            "message": self._format_analysis_summary(result)  # AI向けメッセージ追加
        }
    return result
```

#### パターン 3: エラーハンドリング統一

```python
async def execute_function(self, function_name, arguments):
    try:
        # UseCase呼び出し
        return await self._internal_method(arguments)
    except Exception as e:
        # Tool層での統一エラー形式
        return {
            "success": False,
            "error": f"ツールエラー ({function_name}): {e}",
            "details": str(e)
        }
```

### Tool 形式別戻り値

#### 旧式 (Google ADK FunctionTool)

```python
# 関数の戻り値がそのままAIエージェントに渡される
async def analyze_child_image(...):
    result = await usecase.analyze_child_image(...)
    return result  # dict形式でAIに送信
```

#### 新式 (FunctionDeclaration)

```python
# execute_function経由でAIエージェントに渡される
async def execute_function(self, function_name, arguments):
    if function_name == "analyze_child_image":
        result = await self.usecase.analyze_child_image(...)
        return result  # dict形式でAIに送信
```

## 📋 戻り値設計原則

### ✅ 推奨パターン

1. **UseCase 戻り値の直接利用**: Tool 層は UseCase の戻り値をなるべくそのまま返す
2. **統一エラー形式**: `{"success": False, "error": "...", "details": "..."}`
3. **AI 向けメッセージ追加**: 必要に応じて`message`フィールドで分析結果要約
4. **型安全性**: TypeScript/Python 型ヒントで戻り値形式を明確化

### ❌ 避けるべきパターン

1. **Tool 層での重複ロジック**: ビジネスロジックを Tool で再実装
2. **戻り値形式の大幅変更**: UseCase の戻り値を根本的に変える
3. **レイヤー跨ぎ**: Tool から Infrastructure 層への直接アクセス
4. **状態保持**: Tool 層でのデータ保持・キャッシュ

## 🔄 データフロー例

```
1. AIエージェント → Tool層呼び出し
   引数: {"user_id": "123", "title": "初歩き", ...}

2. Tool層 → UseCase層呼び出し
   引数: {"user_id": "123", "record_data": {...}}

3. UseCase層 → Infrastructure層呼び出し
   Repository.create(...)

4. Infrastructure層 → UseCase層戻り値
   戻り値: {"success": True, "id": "record_456", "data": {...}}

5. UseCase層 → Tool層戻り値
   戻り値: {"success": True, "id": "record_456", "data": {...}}

6. Tool層 → AIエージェント戻り値
   戻り値: {"success": True, "id": "record_456", "data": {...}, "message": "✅ 成長記録を作成しました"}
```

## 🎯 まとめ

- **UseCase 層**: ビジネスロジックの核心処理、統一された戻り値形式
- **Tool 層**: UseCase の薄いラッパー、AI 向けの軽微な整形のみ
- **戻り値の本質**: Tool 層は UseCase の戻り値をほぼそのまま返す設計
- **責務分離**: 各層が明確な役割を持ち、戻り値も一貫性を保つ

---

**更新日**: 2024-01-26  
**対象バージョン**: GenieUs v0.1.0-mvp
