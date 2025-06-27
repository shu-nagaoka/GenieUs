# ユーザー認証・パーソナライズ機能実装ガイド

Google OAuth + JWT認証によるユーザー固有データ管理システムの完全実装ガイド

## 🎯 概要

GenieUsアプリケーションにGoogle OAuth認証とJWT統合によるパーソナライズ機能を実装し、ユーザーごとに独立したデータ環境を提供します。

### 実装の核心
- **Google OAuth + JWT段階的認証**: フロントエンド→バックエンド認証統合
- **SQLiteベース個人データ管理**: JSONファイルからデータベースへ移行
- **Composition Root統合**: 既存アーキテクチャとの完全統合
- **段階的互換性**: 既存機能を壊さない段階的実装

## 🏗️ アーキテクチャ概要

### 認証フロー設計
```
フロントエンド (NextAuth.js)
    ↓ Google OAuth
Google Authentication Server
    ↓ OAuth Token
バックエンド認証ミドルウェア
    ├─ JWT検証 (プライマリ)
    └─ Google Token検証 (フォールバック)
    ↓ user_id抽出
個人化されたAPI処理
    ↓ ユーザー固有データアクセス
SQLiteデータベース (user_id別分離)
```

### データベース設計
```sql
-- ユーザーテーブル (認証統合)
users (google_id PK, email, name, picture_url, locale, verified_email, created_at, last_login)

-- 既存エンティティにuser_id外部キー追加
family_info (family_id PK, user_id FK → users.google_id, ...)
child_records (id PK, user_id FK → users.google_id, child_id, ...)
growth_records (id PK, user_id FK → users.google_id, child_id, ...)
-- ... 他すべてのエンティティも同様
```

## 📋 実装手順

### Phase 1: 環境設定とデータベース準備

#### 1.1 環境変数設定

**backend/.env.example** (開発環境):
```bash
# ********** NextAuth.js (フロントエンド認証) ********** #
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
NEXTAUTH_SECRET=your_nextauth_secret_key
NEXTAUTH_URL=http://localhost:3000

# ********** データベース設定 ********** #
DATABASE_URL=sqlite:///./data/genieus.db
DATABASE_TYPE=sqlite

# ********** セキュリティ設定 ********** #
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRE_MINUTES=1440  # 24時間
```

#### 1.2 SQLiteデータベース自動初期化

**重要**: アプリケーション起動時に自動でデータベースが初期化されます。

```python
# src/infrastructure/database/sqlite_manager.py で自動実行
# - users テーブル作成
# - 既存エンティティテーブルにuser_id外部キー追加
# - マイグレーション履歴管理
```

### Phase 2: 認証ミドルウェア実装

#### 2.1 段階的認証システム

**src/presentation/api/middleware/auth_middleware.py**:
```python
class AuthMiddleware:
    async def authenticate_request(self, authorization):
        """段階的認証: JWT → Google OAuth → None"""
        try:
            # 1. JWTトークン検証 (プライマリ)
            payload = self.jwt_authenticator.verify_token(token)
            return {"user_id": payload["sub"], "auth_type": "jwt"}
        except AuthError:
            # 2. Google OAuth検証 (フォールバック)
            google_info = await self.google_verifier.verify_google_token(token)
            if google_info:
                return {"user_id": google_info["sub"], "auth_type": "google_oauth"}
        
        return None  # 認証失敗
```

#### 2.2 FastAPI依存関係統合

**src/presentation/api/dependencies.py**:
```python
async def get_current_user_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """必須認証 - 認証が必要なエンドポイント用"""
    auth_middleware = get_auth_middleware(request)
    return await auth_middleware.require_authentication(credentials)

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """オプション認証 - 認証が任意のエンドポイント用"""
    auth_middleware = get_auth_middleware(request)
    return await auth_middleware.optional_authentication(credentials)
```

### Phase 3: ユーザー管理システム

#### 3.1 Userエンティティ

**src/domain/entities.py**:
```python
@dataclass
class User:
    """ユーザーエンティティ（Google OAuth統合）"""
    
    google_id: str = ""  # Google OAuth User ID (プライマリキー)
    email: str = ""
    name: str = ""
    picture_url: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_google_oauth(cls, oauth_user_info: dict) -> "User":
        """Google OAuth情報からユーザーエンティティを作成"""
        return cls(
            google_id=oauth_user_info.get("sub", ""),
            email=oauth_user_info.get("email", ""),
            name=oauth_user_info.get("name", ""),
            # ... その他フィールド
        )
```

#### 3.2 UserRepository (SQLite実装)

**src/infrastructure/adapters/persistence/user_repository.py**:
```python
class UserRepository:
    """ユーザーデータ永続化Repository（SQLite版）"""
    
    async def create_or_update_user(self, user: User) -> User:
        """ユーザー作成または更新（upsert）"""
        existing_user = await self.get_user_by_google_id(user.google_id)
        
        if existing_user:
            user.created_at = existing_user.created_at  # 作成日時保持
            return await self.update_user(user)
        else:
            return await self.create_user(user)
```

#### 3.3 UserManagementUseCase

**src/application/usecases/user_management_usecase.py**:
```python
class UserManagementUseCase:
    """ユーザー管理ビジネスロジック"""
    
    async def login_with_google_oauth(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Google OAuth情報でログイン処理"""
        # 1. Google OAuth → Userエンティティ
        user = User.from_google_oauth(google_user_info)
        
        # 2. ユーザー作成/更新
        stored_user = await self.user_repository.create_or_update_user(user)
        
        # 3. JWTトークン生成
        access_token = self.jwt_authenticator.create_access_token(stored_user)
        
        return {
            "success": True,
            "user": stored_user.to_dict(),
            "access_token": access_token,
            "token_type": "bearer"
        }
```

### Phase 4: API統合

#### 4.1 認証APIエンドポイント

**src/presentation/api/routes/auth.py**:
```python
@router.post("/login/google", response_model=LoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    user_management_usecase: UserManagementUseCase = Depends(...)
):
    """Google OAuthでログイン"""
    result = await user_management_usecase.login_with_google_oauth(
        request.google_user_info
    )
    # JWTトークンとユーザー情報を返却

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    user_management_usecase: UserManagementUseCase = Depends(...)
):
    """ユーザープロフィール取得"""
    # 認証済みユーザーのプロフィール情報を返却
```

#### 4.2 既存API認証統合

**src/presentation/api/routes/family.py** (例):
```python
@router.post("/register")
async def register_family_info(
    request: FamilyRegistrationRequest,
    user_id: str = Depends(get_user_id_optional),  # 認証統合（オプション）
    family_usecase: FamilyManagementUseCase = Depends(get_family_management_usecase),
):
    """家族情報を登録"""
    # 認証ユーザーIDまたはデフォルトを使用
    effective_user_id = user_id or "frontend_user"
    
    # 既存ロジックはそのまま、user_idのみ認証ユーザーに変更
    result = await family_usecase.register_family_info(
        user_id=effective_user_id, 
        family_data=request.dict()
    )
```

### Phase 5: データ移行システム

#### 5.1 JSONからSQLiteへの自動移行

**src/infrastructure/database/data_migrator.py**:
```python
class DataMigrator:
    """既存JSONデータのSQLite移行管理"""
    
    async def migrate_all_data(self) -> Dict[str, Any]:
        """全データの移行実行"""
        # 1. 家族情報 (*_family.json)
        family_results = await self._migrate_family_data()
        
        # 2. 成長記録 (growth_records.json)
        growth_results = await self._migrate_growth_records()
        
        # 3. 努力レポート (effort_reports.json)
        effort_results = await self._migrate_effort_reports()
        
        return migration_summary
    
    async def _migrate_family_data(self):
        """JSONファイルパターン: frontend_user_family.json → SQLite"""
        family_files = list(self.data_dir.glob("*_family.json"))
        
        for family_file in family_files:
            # ファイル名からuser_id抽出
            user_id = family_file.stem.replace("_family", "")
            
            # JSONデータ読み込み → SQLite挿入
            with open(family_file, 'r') as f:
                family_data = json.load(f)
            
            await self._insert_family_data(user_id, family_data)
```

#### 5.2 管理者API

**src/presentation/api/routes/admin.py**:
```python
@router.get("/migration/status")
async def get_migration_status(request: Request):
    """データ移行状況確認"""
    data_migrator = request.app.composition_root.get_data_migrator()
    status = await data_migrator.get_migration_status()
    return {
        "sqlite_records": {"users": 5, "family_info": 3, ...},
        "json_files_count": 8,
        "json_files": ["frontend_user_family.json", "growth_records.json", ...]
    }

@router.post("/migration/execute")
async def execute_data_migration(request: Request):
    """データ移行実行"""
    # JSON → SQLite 完全移行
    result = await data_migrator.migrate_all_data()
    return migration_results
```

## 🔧 Composition Root統合

### 依存関係組み立て

**src/di_provider/composition_root.py**:
```python
class CompositionRoot:
    def _build_infrastructure_layer(self):
        """Infrastructure層組み立て"""
        # ... 既存コンポーネント

        # Authentication components
        google_verifier = GoogleTokenVerifier(logger=self.logger)
        jwt_authenticator = JWTAuthenticator(settings=self.settings, logger=self.logger)
        auth_middleware = AuthMiddleware(
            settings=self.settings,
            logger=self.logger,
            google_verifier=google_verifier,
            jwt_authenticator=jwt_authenticator
        )
        
        # Database components
        if self.settings.DATABASE_TYPE == "sqlite":
            sqlite_manager = SQLiteManager(settings=self.settings, logger=self.logger)
            database_migrator = DatabaseMigrator(sqlite_manager=sqlite_manager, logger=self.logger)
            
            # データベース初期化（必要に応じて）
            if not database_migrator.is_database_initialized():
                database_migrator.initialize_database()
            
            # User Repository + Data Migrator
            user_repository = UserRepository(sqlite_manager=sqlite_manager, logger=self.logger)
            data_migrator = DataMigrator(settings=self.settings, sqlite_manager=sqlite_manager, logger=self.logger)
            
            self._infrastructure.register("user_repository", user_repository)
            self._infrastructure.register("data_migrator", data_migrator)

    def _build_application_layer(self):
        """Application層組み立て"""
        # ... 既存UseCases

        # User Management UseCase
        if self.settings.DATABASE_TYPE == "sqlite":
            user_repository = self._infrastructure.get("user_repository")
            jwt_authenticator = self._infrastructure.get("jwt_authenticator")
            user_management_usecase = UserManagementUseCase(
                user_repository=user_repository,
                jwt_authenticator=jwt_authenticator,
                logger=self.logger,
            )
            self._usecases.register("user_management", user_management_usecase)
```

## 🌐 API仕様

### 認証エンドポイント

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| POST | `/api/v1/auth/login/google` | Google OAuth ログイン | ❌ |
| GET | `/api/v1/auth/profile` | プロフィール取得 | ✅ 必須 |
| PUT | `/api/v1/auth/profile` | プロフィール更新 | ✅ 必須 |
| POST | `/api/v1/auth/verify` | トークン検証 | ⚠️ オプション |
| POST | `/api/v1/auth/refresh` | トークンリフレッシュ | ✅ 必須 |
| DELETE | `/api/v1/auth/account` | アカウント削除 | ✅ 必須 |

### 管理者エンドポイント

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/admin/migration/status` | 移行状況確認 |
| POST | `/api/v1/admin/migration/backup` | JSONバックアップ |
| POST | `/api/v1/admin/migration/execute` | データ移行実行 |
| GET | `/api/v1/admin/database/info` | データベース情報 |
| GET | `/api/v1/admin/system/health` | システムヘルスチェック |

### 既存API認証統合

**既存エンドポイントは後方互換性を維持**:
- 認証トークンがある場合: 認証ユーザーのデータにアクセス
- 認証トークンがない場合: デフォルトユーザー(`"frontend_user"`)のデータにアクセス

## 📖 使用例

### 1. Google OAuthログイン

**リクエスト**:
```http
POST /api/v1/auth/login/google
Content-Type: application/json

{
  "google_user_info": {
    "sub": "google_user_12345",
    "email": "user@example.com",
    "name": "田中太郎",
    "picture": "https://...",
    "email_verified": true
  }
}
```

**レスポンス**:
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "google_id": "google_user_12345",
    "email": "user@example.com",
    "name": "田中太郎",
    "picture_url": "https://...",
    "created_at": "2024-12-26T10:00:00",
    "last_login": "2024-12-26T10:00:00"
  }
}
```

### 2. 認証付き家族情報登録

**リクエスト**:
```http
POST /api/v1/family/register
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "parent_name": "田中太郎",
  "family_structure": "核家族",
  "concerns": "夜泣きが心配です",
  "living_area": "東京都",
  "children": [
    {"name": "田中花子", "birth_date": "2024-06-01", "gender": "female"}
  ]
}
```

**動作**:
- JWTトークンから`user_id="google_user_12345"`を抽出
- `google_user_12345`用の家族情報として保存
- 他のユーザーからはアクセス不可

### 3. データ移行実行

**リクエスト**:
```http
POST /api/v1/admin/migration/execute
```

**レスポンス**:
```json
{
  "success": true,
  "summary": {
    "family": {"migrated_count": 3, "errors": []},
    "growth_records": {"migrated_count": 15, "errors": []},
    "effort_reports": {"migrated_count": 8, "errors": []}
  }
}
```

## 🚨 重要な設計決定

### 1. 段階的認証の理由

**JWT → Google OAuth → フォールバック** の順序:
- **パフォーマンス**: JWTはローカル検証で高速
- **信頼性**: Google OAuth APIが一時的に利用できない場合の対応
- **移行期間対応**: 既存フロントエンドとの互換性

### 2. オプション認証の採用

既存APIは認証を**必須にせず**、段階的移行を可能にする:
```python
user_id: str = Depends(get_user_id_optional)  # 認証統合（オプション）
effective_user_id = user_id or "frontend_user"  # フォールバック
```

**メリット**:
- 既存機能の即座の破綻を防ぐ
- フロントエンド認証実装の段階的対応
- 開発・テスト時の利便性

### 3. SQLite採用の理由

**開発・デプロイ段階でのSQLite使用**:
- **設定不要**: 追加のデータベースサーバー不要
- **移行準備**: PostgreSQL移行時もRepository Patternで容易
- **開発効率**: ローカル開発での簡単性

## 🔄 移行戦略

### 段階的移行計画

1. **Phase 1 (現在)**: 
   - 認証システム実装
   - SQLiteデータベース構築
   - 既存API認証統合（オプション）

2. **Phase 2 (次期)**:
   - フロントエンド認証実装
   - 既存データの完全移行
   - 認証を必須に切り替え

3. **Phase 3 (将来)**:
   - PostgreSQL移行検討
   - 高度なパーソナライズ機能
   - マルチテナント対応

### データ整合性の確保

```sql
-- 外部キー制約によるデータ整合性
FOREIGN KEY (user_id) REFERENCES users(google_id) ON DELETE CASCADE
```

**効果**:
- ユーザー削除時に関連データも自動削除
- データの孤立防止
- GDPR等のプライバシー要件対応

## 🧪 テスト戦略

### 認証テスト

```python
class TestUserAuthentication:
    async def test_google_oauth_login(self):
        """Google OAuthログインテスト"""
        google_user_info = {
            "sub": "test_google_id",
            "email": "test@example.com",
            "name": "テストユーザー"
        }
        
        result = await user_management_usecase.login_with_google_oauth(google_user_info)
        
        assert result["success"] is True
        assert "access_token" in result
        assert result["user"]["google_id"] == "test_google_id"
    
    async def test_jwt_token_verification(self):
        """JWTトークン検証テスト"""
        # ... JWTトークン検証ロジックテスト
```

### データ分離テスト

```python
class TestUserDataIsolation:
    async def test_family_data_isolation(self):
        """ユーザー間データ分離テスト"""
        # ユーザーAの家族情報作成
        await family_usecase.register_family_info("user_a", family_data_a)
        
        # ユーザーBの家族情報作成
        await family_usecase.register_family_info("user_b", family_data_b)
        
        # ユーザーAは自分のデータのみアクセス可能
        family_a = await family_usecase.get_family_info("user_a")
        assert family_a is not None
        
        # ユーザーBのデータにはアクセス不可
        family_b_from_a = await family_usecase.get_family_info("user_b")
        assert family_b_from_a is None  # user_a視点では見えない
```

## 🔧 実装完了項目

| **項目** | **ステータス** | **実装ファイル** |
|---------|---------------|-----------------|
| **👤 Userエンティティ** | ✅ 完了 | `src/domain/entities.py` |
| **🔐 認証ミドルウェア** | ✅ 完了 | `src/presentation/api/middleware/auth_middleware.py` |
| **🏪 UserRepository** | ✅ 完了 | `src/infrastructure/adapters/persistence/user_repository.py` |
| **📋 UserManagementUseCase** | ✅ 完了 | `src/application/usecases/user_management_usecase.py` |
| **🗃️ SQLiteManager** | ✅ 完了 | `src/infrastructure/database/sqlite_manager.py` |
| **📦 DataMigrator** | ✅ 完了 | `src/infrastructure/database/data_migrator.py` |
| **🌐 認証API** | ✅ 完了 | `src/presentation/api/routes/auth.py` |
| **🛠️ 管理者API** | ✅ 完了 | `src/presentation/api/routes/admin.py` |
| **⚡ 認証Dependencies** | ✅ 完了 | `src/presentation/api/dependencies.py` |
| **🏗️ Composition Root統合** | ✅ 完了 | `src/di_provider/composition_root.py` |
| **🌊 既存API認証統合** | ✅ 完了 | `src/presentation/api/routes/family.py` (例) |

## 📚 関連ドキュメント

### アーキテクチャ
- [アーキテクチャ概要](../architecture/overview.md) - 全体設計理解
- [Composition Root設計](../architecture/composition-root-design.md) - DI統合詳細

### 技術詳細
- [FastAPI DI統合](../technical/fastapi-di-integration.md) - Depends統合パターン
- [エラーハンドリング戦略](../technical/error-handling.md) - 段階的フォールバック
- [コーディング規約](../development/coding-standards.md) - 実装規約

### 開発ガイド
- [新UseCase実装](./new-usecase-impl.md) - ビジネスロジック実装
- [DI統合マイグレーション](./di-migration-guide.md) - DI統合手順

---

この実装により、GenieUsは**完全なユーザー認証・パーソナライズ機能**を獲得し、Google アカウントでログインしたユーザーごとに**独立したデータ環境**を提供する現代的なSaaSアプリケーションとしての基盤が整いました。