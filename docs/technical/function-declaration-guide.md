# FunctionDeclaration 完全ガイド

## 📋 概要

Google AI Generative Language APIの`FunctionDeclaration`は、**AIエージェントがツールの使い方を理解するためのメタデータ定義**です。
実際の処理は行わず、「このツールは何ができるか」「どんな引数が必要か」をAIに教える役割を果たします。

## 🎯 FunctionDeclarationの本質

### 「デコレート」の意味

FunctionDeclarationは文字通り「**関数の宣言・説明書**」であり、実処理は含みません：

```python
# ❌ 誤解: FunctionDeclarationが処理を行う
# ✅ 正解: FunctionDeclarationはAIへの「取扱説明書」

FunctionDeclaration(
    name="analyze_child_image",
    description="お子さんの画像を分析します",  # ← AIに何ができるかを説明
    parameters=Schema(...)  # ← AIにどんな引数が必要かを説明
)
# ↑ これ自体は何も処理しない。ただの「説明書」
```

### 類似例：レストランのメニュー

```python
# メニュー（FunctionDeclaration）
"ハンバーガー - 牛肉のパティとレタス、トマトをバンズで挟んだ料理 - 価格: 500円"

# 実際の調理（execute_function）
def make_hamburger(ingredients):
    patty = cook_beef(ingredients.beef)
    return assemble(patty, ingredients.lettuce, ingredients.tomato)
```

**メニューは料理そのものではなく、何が作れるかの説明**。FunctionDeclarationも同じです。

## 🔄 処理フロー詳細

### 1. AI側の処理

```python
# AIエージェントの内部処理（概念的）
available_tools = [
    {
        "name": "analyze_child_image",
        "description": "お子さんの画像を分析します",
        "parameters": {
            "image_path": "必須 - 分析する画像のパス",
            "analysis_type": "オプション - 分析タイプ"
        }
    }
]

# ユーザーの質問: "この写真の子どもの表情を分析して"
# AI: "analyze_child_imageツールを使えば良さそうだ"
tool_call = {
    "function_name": "analyze_child_image",
    "arguments": {
        "image_path": "/path/to/image.jpg",
        "analysis_type": "emotion"
    }
}
```

### 2. GenieUs側の処理

```python
# Tool層で受信
async def execute_function(self, function_name: str, arguments: Dict[str, Any]):
    # FunctionDeclarationで宣言した関数名で分岐
    if function_name == "analyze_child_image":
        return await self._analyze_child_image(arguments)
    
# 実際の処理実行
async def _analyze_child_image(self, args):
    # UseCase層を呼び出し、実際の画像分析を実行
    result = await self.image_analysis_usecase.analyze_child_image(...)
    return result
```

## 📊 新式vs旧式の本質的違い

### 旧式 (Google ADK FunctionTool)

```python
# 関数定義 = ツール説明 + 実処理が一体化
async def analyze_child_image(image_path: str, analysis_type: str = "general"):
    """お子さんの画像を分析します"""  # ← AIへの説明
    # ↓ 実際の処理
    result = await usecase.analyze_child_image(image_path, analysis_type)
    return result

# ADKが自動的に関数シグネチャからFunctionDeclarationを生成
tool = FunctionTool(func=analyze_child_image)
```

**特徴**: 
- 説明と実処理が一つの関数に混在
- ADKが自動的にメタデータを抽出
- シンプルだが、柔軟性に欠ける

### 新式 (FunctionDeclaration)

```python
# 1. ツール説明（メタデータ）を明示的に定義
def get_function_declarations(self):
    return [
        FunctionDeclaration(
            name="analyze_child_image",
            description="お子さんの画像を分析してblahblah...",  # ← 詳細な説明
            parameters=Schema(
                type=Type.OBJECT,
                properties={
                    "image_path": Schema(type=Type.STRING, description="分析する画像のパス"),
                    "analysis_type": Schema(
                        type=Type.STRING,
                        description="分析タイプ",
                        enum=["general", "emotion", "safety"]  # ← 選択肢も指定可能
                    )
                }
            )
        )
    ]

# 2. 実処理を別途定義
async def execute_function(self, function_name: str, arguments: Dict[str, Any]):
    if function_name == "analyze_child_image":
        # 実際の処理
        result = await self.usecase.analyze_child_image(...)
        return result
```

**特徴**:
- 説明と実処理が完全に分離
- より詳細で構造化された説明が可能
- AIの理解精度が向上

## 🤖 AIエージェントの視点

### FunctionDeclarationがAIに与える情報

```python
FunctionDeclaration(
    name="create_growth_record",
    description="新しい成長記録を作成します。身長・体重から言葉の発達まで幅広く記録できます。",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "child_name": Schema(type=Type.STRING, description="お子さんの名前"),
            "title": Schema(type=Type.STRING, description="記録のタイトル"),
            "type": Schema(
                type=Type.STRING,
                description="成長記録のタイプ",
                enum=["body_growth", "language_growth", "milestone"]
            )
        },
        required=["child_name", "title", "type"]
    )
)
```

**AIが理解すること**:
1. 📝 **機能**: "成長記録を作成できる"
2. 🎯 **目的**: "身長・体重から言葉の発達まで記録"
3. 📋 **必須項目**: "child_name, title, type は必ず必要"
4. 🔤 **選択肢**: "type は body_growth, language_growth, milestone のいずれか"
5. 💡 **使用場面**: "ユーザーが子どもの成長について話したら使えそう"

### AIの判断プロセス

```
ユーザー: "うちの太郎、今日初めて立っちができたんです！"

AI思考プロセス:
1. "立っち" = milestone的な成長
2. create_growth_recordツールが使えそう
3. 必要な情報を整理:
   - child_name: "太郎" (ユーザーから取得済み)
   - title: "初立っち" (内容から推測)
   - type: "milestone" (立っちはマイルストーン)
4. ツール呼び出し実行

AI → GenieUs:
{
    "function_name": "create_growth_record",
    "arguments": {
        "child_name": "太郎",
        "title": "初立っち",
        "type": "milestone",
        "description": "今日初めて一人で立つことができました"
    }
}
```

## 📚 具体的な使用イメージ

### シナリオ1: 画像分析

```python
# 1. FunctionDeclarationでAIに説明
FunctionDeclaration(
    name="analyze_child_image", 
    description="写真からお子さんの表情や活動を分析し、成長の様子を確認します",
    parameters=Schema(...)
)

# 2. ユーザーがAIと会話
ユーザー: "この写真の娘の表情、どう思いますか？" + [画像添付]

# 3. AIがFunctionDeclarationを参考に判断
AI: "analyze_child_imageツールで分析できます"

# 4. AIがツール呼び出し
AI → execute_function("analyze_child_image", {"image_path": "...", "analysis_type": "emotion"})

# 5. 実処理実行
result = await image_analysis_usecase.analyze_child_image(...)

# 6. AIが結果を解釈してユーザーに回答
AI: "お嬢さんはとても楽しそうな表情をされていますね！..."
```

### シナリオ2: 食事プラン作成

```python
# 1. FunctionDeclarationでAIに説明
FunctionDeclaration(
    name="suggest_meal_plan",
    description="お子さんの月齢に応じた最適な食事プランを提案します",
    parameters=Schema(
        properties={
            "child_age_months": Schema(type=Type.NUMBER, description="お子さんの月齢"),
            "allergies": Schema(type=Type.ARRAY, description="アレルギー食材")
        }
    )
)

# 2. ユーザーとの会話
ユーザー: "8ヶ月の息子の離乳食メニューを考えてほしいです。卵アレルギーがあります。"

# 3. AIがFunctionDeclarationから必要情報を抽出
AI: "月齢8ヶ月、卵アレルギーありの情報でsuggest_meal_planを使用"

# 4. ツール呼び出し
AI → execute_function("suggest_meal_plan", {
    "child_age_months": 8,
    "allergies": ["卵"]
})

# 5. 実処理とレスポンス
result = {
    "success": True,
    "meal_suggestions": {
        "breakfast": "10倍粥、野菜ペースト",
        "lunch": "白身魚ペースト、にんじんペースト"
    },
    "avoid_foods": ["蜂蜜", "生もの", "卵"]
}

# 6. AIが結果を分かりやすく説明
AI: "8ヶ月のお子さんでしたら、以下のようなメニューがおすすめです..."
```

## 🔧 実装時のポイント

### ✅ 良いFunctionDeclaration

```python
FunctionDeclaration(
    name="create_schedule_event",
    description="お子さんの予定（検診、予防接種、習い事など）を登録します。リマインダー機能付きで忘れ防止をサポートします。",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "title": Schema(
                type=Type.STRING, 
                description="予定のタイトル（例：小児科検診、BCG接種、ピアノレッスン）"
            ),
            "date": Schema(
                type=Type.STRING, 
                description="予定日（YYYY-MM-DD形式）"
            ),
            "time": Schema(
                type=Type.STRING, 
                description="時刻（HH:MM形式、任意）"
            ),
            "location": Schema(
                type=Type.STRING, 
                description="場所（病院名、施設名など、任意）"
            ),
            "reminder_minutes": Schema(
                type=Type.NUMBER, 
                description="事前リマインダー（分前、デフォルト30分）"
            )
        },
        required=["title", "date"]
    )
)
```

**優れている点**:
- 具体的な使用例を含む説明
- パラメータの形式を明確に指定
- 必須・任意の区別が明確
- AIが判断しやすい詳細度

### ❌ 不十分なFunctionDeclaration

```python
FunctionDeclaration(
    name="save_data",  # ← 抽象的すぎる
    description="データを保存",  # ← 何のデータかわからない
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "data": Schema(type=Type.STRING)  # ← 形式が不明確
        }
    )
)
```

## 🎯 まとめ

### FunctionDeclarationの本質

1. **メタデータ定義**: 実処理は行わず、AIへの「取扱説明書」
2. **AI理解支援**: より正確で適切なツール使用を可能にする
3. **処理分離**: 説明と実装を分離し、保守性を向上
4. **柔軟性**: 詳細で構造化された説明により、複雑なツールも表現可能

### 設計指針

- **説明の詳細さ**: AIが迷わないレベルの具体的な説明
- **パラメータの明確化**: 型、形式、例を含む丁寧な説明
- **実処理との分離**: FunctionDeclarationは説明のみ、実処理は別途実装
- **ユーザー視点**: AIがユーザーの意図を正しく理解できる構成

---

**更新日**: 2024-01-26  
**対象バージョン**: GenieUs v0.1.0-mvp  
**関連ドキュメント**: [レイヤー別戻り値仕様書](layer-return-values.md)