# UseCase層設計ルール完全ガイド

## 📋 概要

GenieUsアーキテクチャにおけるUseCase層の設計ルール、戻り値仕様、命名規約を完全整理したドキュメント。
Clean Architectureパターンに基づき、ビジネスロジックの一貫性と保守性を確保。

## 🎯 UseCase層の役割と責務

### ✅ UseCase層が行うこと

1. **ビジネスロジックの実装**: ドメイン知識の中核となる処理
2. **データ変換**: Infrastructure層の技術データ → ビジネス概念への変換
3. **エラーハンドリング**: ビジネス観点でのエラー処理とメッセージ生成
4. **依存関係統合**: Repository、外部サービスアダプター等の組み合わせ
5. **レスポンス統一**: 統一された戻り値形式での結果返却

### ❌ UseCase層が行わないこと

1. **UI関連処理**: プレゼンテーション層固有のフォーマット
2. **技術実装詳細**: データベースアクセス、API呼び出し等の実装
3. **状態保持**: リクエスト間でのデータ保持
4. **外部システム直接操作**: Repository/Adapterを通さない外部アクセス

## 📊 統一戻り値仕様

### 基本形式（必須フィールド）

全てのUseCaseメソッドは以下の統一形式で戻り値を返します：

```python
# ✅ 成功時の基本形式
{
    "success": True,          # bool - 処理成功フラグ（必須）
    "data": {...},           # Any - 成功時のビジネスデータ（任意）
    "message": "...",        # str - 処理結果メッセージ（任意）
    "id": "record_123"       # str - 作成・更新時の対象ID（任意）
}

# ❌ 失敗時の基本形式
{
    "success": False,        # bool - 処理失敗フラグ（必須）
    "error": "...",         # str - エラーメッセージ（失敗時必須）
    "message": "..."        # str - ユーザー向けメッセージ（任意）
}
```

### フィールド詳細仕様

| フィールド | 型 | 必須 | 説明 | 使用場面 |
|-----------|---|------|------|---------|
| `success` | `bool` | ✅ | 処理成功フラグ | 全メソッド |
| `data` | `Any` | ❌ | ビジネスデータ | 取得・作成・更新成功時 |
| `message` | `str` | ❌ | 処理結果メッセージ | ユーザー向け説明 |
| `error` | `str` | ❌ | エラーメッセージ | 失敗時のエラー内容 |
| `id` | `str` | ❌ | 操作対象ID | 作成・更新・削除時 |

## 🏗️ UseCase設計パターン

### パターン1: 単一エンティティ操作

```python
class GrowthRecordUseCase:
    """成長記録管理UseCase - 単一エンティティ操作パターン"""
    
    def __init__(self, growth_record_repository, family_repository, logger: logging.Logger):
        self.growth_record_repository = growth_record_repository  # メインリポジトリ
        self.family_repository = family_repository              # 関連リポジトリ
        self.logger = logger                                   # DI注入ロガー
    
    async def create_growth_record(self, user_id: str, record_data: dict) -> Dict[str, Any]:
        """メインメソッド: CRUD操作 + ビジネスロジック"""
        try:
            # 1. ビジネスロジック（月齢計算等）
            calculated_age = await self._calculate_age_at_record_date(...)
            
            # 2. エンティティ作成
            growth_record = GrowthRecord.from_dict(user_id, record_data)
            
            # 3. リポジトリ保存
            result = await self.growth_record_repository.save_growth_record(growth_record)
            
            # 4. 統一レスポンス返却
            return {"success": True, "id": result.get("record_id"), "data": growth_record.to_dict()}
        
        except Exception as e:
            # 5. エラーハンドリング
            return {"success": False, "message": f"成長記録の作成に失敗しました: {str(e)}"}
    
    async def _calculate_age_at_record_date(self, ...) -> Optional[int]:
        """プライベートメソッド: ビジネスロジック補助"""
        # 内部計算ロジック
        pass
```

### パターン2: 外部サービス統合

```python
class ImageAnalysisUseCase:
    """画像解析UseCase - 外部サービス統合パターン"""
    
    def __init__(self, image_analyzer: ImageAnalyzerProtocol, logger: logging.Logger):
        self.image_analyzer = image_analyzer  # 外部サービスアダプター
        self.logger = logger                 # DI注入ロガー
    
    async def analyze_child_image(self, image_path: str, child_id: str, analysis_context: dict = None) -> dict[str, Any]:
        """メインメソッド: 外部サービス + ビジネス変換"""
        try:
            # 1. ビジネスロジック（子育て用プロンプト構築）
            prompt = self._build_childcare_analysis_prompt(child_id, analysis_context)
            
            # 2. 外部サービス呼び出し
            raw_result = await self.image_analyzer.analyze_image_with_prompt(image_path, prompt)
            
            # 3. ビジネス概念への変換
            result = self._transform_to_childcare_analysis(raw_result, child_id)
            
            # 4. 結果検証・正規化
            validated_result = self._validate_analysis_result(result)
            
            return validated_result
        
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _build_childcare_analysis_prompt(self, child_id: str, context: dict) -> str:
        """プライベートメソッド: ビジネス知識（子育て用プロンプト）"""
        pass
    
    def _transform_to_childcare_analysis(self, raw_result: dict, child_id: str) -> dict:
        """プライベートメソッド: 技術レスポンス → ビジネス概念変換"""
        pass
```

### パターン3: 複数サービス統合

```python
class FamilyManagementUseCase:
    """家族管理UseCase - シンプルCRUDパターン"""
    
    def __init__(self, family_repository, logger: logging.Logger):
        self.family_repository = family_repository  # 単一リポジトリ
        self.logger = logger                       # DI注入ロガー
    
    async def register_family_info(self, user_id: str, family_data: dict) -> dict:
        """シンプルなCRUD操作"""
        try:
            # 1. エンティティ作成
            family_info = FamilyInfo.from_dict(user_id, family_data)
            
            # 2. リポジトリ保存
            result = await self.family_repository.save_family_info(family_info)
            
            # 3. 統一レスポンス
            return {"success": True, "message": "家族情報を登録しました", "family_id": result.get("family_id")}
        
        except Exception as e:
            return {"success": False, "error": f"家族情報の登録に失敗しました: {str(e)}"}
```

## 📝 命名規約・設計ルール

### クラス命名規約

```python
# ✅ 推奨パターン
class GrowthRecordUseCase:         # {ドメイン概念}UseCase
class ImageAnalysisUseCase:        # {機能名}UseCase  
class FamilyManagementUseCase:     # {管理対象}ManagementUseCase
class VoiceAnalysisUseCase:        # {分析対象}AnalysisUseCase

# ❌ 避けるべきパターン
class GrowthRecordService:         # Service suffix は使わない
class ImageAnalysisHandler:        # Handler suffix は使わない
class GrowthRecordManager:         # Manager suffix は使わない
```

### メソッド命名規約

```python
class SampleUseCase:
    # ✅ パブリックメソッド（Tool層から呼び出し）
    async def create_growth_record(self, ...):     # create_{エンティティ}
    async def get_growth_records(self, ...):       # get_{エンティティ複数形}
    async def get_growth_record(self, ...):        # get_{エンティティ単数}
    async def update_growth_record(self, ...):     # update_{エンティティ}
    async def delete_growth_record(self, ...):     # delete_{エンティティ}
    async def analyze_child_image(self, ...):      # {動詞}_{対象}
    
    # ✅ プライベートメソッド（内部ビジネスロジック）
    def _build_childcare_analysis_prompt(self, ...):     # _build_{対象}
    def _transform_to_childcare_analysis(self, ...):     # _transform_{変換内容}
    def _validate_analysis_result(self, ...):            # _validate_{対象}
    def _calculate_age_at_record_date(self, ...):        # _calculate_{計算対象}
    def _create_error_response(self, ...):               # _create_{作成対象}
    def _get_default_value(self, ...):                   # _get_{取得対象}
```

### コンストラクター設計ルール

```python
class StandardUseCase:
    """標準的なUseCaseコンストラクターパターン"""
    
    def __init__(
        self,
        primary_repository: PrimaryRepositoryProtocol,      # メインリポジトリ
        secondary_repository: SecondaryRepositoryProtocol,  # 関連リポジトリ
        external_service: ExternalServiceProtocol,          # 外部サービス
        logger: logging.Logger                              # DI注入ロガー（必須最後）
    ):
        # ✅ 推奨: 型ヒント付きで依存関係を明示
        self.primary_repository = primary_repository
        self.secondary_repository = secondary_repository  
        self.external_service = external_service
        self.logger = logger  # DIコンテナから注入、個別初期化禁止
```

## 🔄 Tool層とAPI層の戻り値関係

### UseCase → Tool層（薄いアダプター）

```python
# UseCase戻り値
usecase_result = {
    "success": True,
    "data": {...},
    "message": "成功しました"
}

# Tool層変換（パススルー + 軽微な整形）
async def _create_growth_record(self, args):
    result = await self.growth_record_usecase.create_growth_record(...)
    
    if result.get("success"):
        return {
            **result,  # UseCase戻り値をそのまま展開
            "message": f"✅ {args['child_name']}さんの成長記録を保存しました！"  # AI向けメッセージ追加
        }
    return result  # エラー時はそのまま返却
```

### UseCase → API層（Pydanticモデル変換）

```python
# UseCase戻り値
usecase_result = {
    "success": True,
    "data": {...},
    "family_id": "family_123"
}

# API層変換（HTTPレスポンス形式 + Pydantic）
@router.post("/register")
async def register_family_info(request: FamilyRegistrationRequest, ...):
    result = await family_usecase.register_family_info(...)
    
    if result.get("success"):
        return JSONResponse(
            status_code=201,
            content={
                "message": result.get("message"),
                "family_id": result.get("family_id"),
                "data": result.get("data")
            }
        )
    else:
        raise HTTPException(status_code=400, detail=result.get("error"))
```

## ⚠️ 設計原則・注意事項

### ✅ 必須遵守事項

1. **統一戻り値形式**: 全メソッドで`{"success": bool, ...}`形式
2. **DI注入ロガー**: `setup_logger(__name__)`禁止、DIコンテナから注入
3. **型アノテーション**: 全パラメータ・戻り値に型ヒント必須
4. **エラーハンドリング**: try-catch + 統一エラーレスポンス必須
5. **ビジネスロジック集約**: ドメイン知識はUseCase層に集約

### ❌ 絶対禁止事項

1. **Infrastructure層直接呼び出し**: Repository/Protocolを経由せずの外部アクセス
2. **UI関連処理**: フロントエンド固有のフォーマット処理
3. **グローバル状態**: クラス変数、モジュール変数での状態保持
4. **個別ロガー初期化**: `logging.getLogger(__name__)`等の個別初期化
5. **レイヤー跨ぎ**: Tool層・API層のロジック混在

### 🎯 ベストプラクティス

```python
class ExampleUseCase:
    """UseCase設計のベストプラクティス例"""
    
    def __init__(self, repository: RepositoryProtocol, logger: logging.Logger):
        self.repository = repository
        self.logger = logger
    
    async def main_business_method(self, user_id: str, data: dict) -> Dict[str, Any]:
        """メインビジネスメソッド"""
        try:
            self.logger.info(f"処理開始: user_id={user_id}")
            
            # 1. 入力検証・ビジネスルール適用
            validated_data = self._validate_business_rules(data)
            
            # 2. エンティティ作成
            entity = BusinessEntity.from_dict(user_id, validated_data)
            
            # 3. Repository操作
            result = await self.repository.save_entity(entity)
            
            # 4. 成功レスポンス
            self.logger.info(f"処理完了: user_id={user_id}")
            return {
                "success": True,
                "id": result.get("entity_id"),
                "data": entity.to_dict(),
                "message": "処理が完了しました"
            }
            
        except BusinessValidationError as e:
            # ビジネスルール違反
            self.logger.warning(f"ビジネスルール違反: {e}")
            return {"success": False, "error": f"入力エラー: {str(e)}"}
            
        except Exception as e:
            # システムエラー
            self.logger.error(f"システムエラー: {e}")
            return {"success": False, "error": "システムエラーが発生しました"}
    
    def _validate_business_rules(self, data: dict) -> dict:
        """プライベートメソッド: ビジネスルール検証"""
        # ビジネス固有の検証ロジック
        if not data.get("required_field"):
            raise BusinessValidationError("必須フィールドが不足しています")
        return data
```

## 📚 既存UseCaseの実装パターン分析

### 1. ImageAnalysisUseCase（外部サービス統合型）

**特徴**:
- 外部AI分析サービス統合
- ビジネスプロンプト構築
- 技術レスポンス→ビジネス概念変換

**戻り値例**:
```python
{
    "child_id": "child_123",
    "detected_items": ["お子さんの笑顔", "健康的な表情"],
    "confidence": 0.85,
    "emotion_detected": "happy",
    "activity_type": "playing",
    "suggestions": ["引き続き遊びを見守りましょう"],
    "timestamp": "2024-01-26T10:30:00"
}
```

### 2. GrowthRecordUseCase（CRUD + ビジネスロジック型）

**特徴**:
- 基本CRUD操作
- 月齢自動計算
- 家族情報との関連処理

**戻り値例**:
```python
{
    "success": True,
    "id": "growth_record_123",
    "data": {
        "child_name": "太郎",
        "title": "初歩き",
        "age_in_months": 12,
        "date": "2024-01-15"
    }
}
```

### 3. FamilyManagementUseCase（シンプルCRUD型）

**特徴**:
- 基本的なCRUD操作
- 最小限のビジネスロジック
- エンティティ中心の設計

**戻り値例**:
```python
{
    "success": True,
    "message": "家族情報を登録しました",
    "family_id": "family_456"
}
```

## 🎯 まとめ

### UseCase層設計の核心原則

1. **統一戦略**: 全UseCaseで統一された戻り値形式・設計パターン
2. **責務分離**: ビジネスロジックのみに集中、技術詳細は依存先に委譲
3. **依存注入**: DIコンテナによる完全な依存関係管理
4. **型安全性**: TypeScript/Python型ヒントによる堅牢性確保
5. **保守性**: 明確な命名規約・設計パターンによる可読性

### レイヤー間データフロー

```
Infrastructure → UseCase → Tool/API
    技術データ   ビジネス概念   UI/AI適応形式
```

UseCase層は技術とビジネスの境界で、**一貫したビジネス概念による戻り値**を提供し、Tool層とAPI層がそれぞれの目的に応じて軽微な変換を行う設計です。

---

**更新日**: 2024-01-26  
**対象バージョン**: GenieUs v0.1.0-mvp  
**関連ドキュメント**: [レイヤー別戻り値仕様書](layer-return-values.md), [FunctionDeclaration完全ガイド](function-declaration-guide.md)