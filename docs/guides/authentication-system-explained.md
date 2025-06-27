# 認証システム実装ガイド - GenieUs

**「Google OAuth + JWT統合認証システム」の完全理解ガイド**

GenieUsの認証システムは、Google OAuthとJWTを組み合わせた二段階認証システムです。このドキュメントでは、認証の仕組みをステップバイステップで詳しく解説します。

## 🎯 認証システムの全体像

### 認証フロー概要
```
1. ユーザー  →  フロントエンド  →  Google OAuth
2. Google OAuth  →  フロントエンド  →  バックエンド
3. バックエンド  →  JWT生成  →  フロントエンド保存
4. 以降のAPI呼び出し  →  JWTトークン認証
```

### アーキテクチャ構成
```
Frontend (Next.js + NextAuth.js)
    ↓
Google OAuth Provider
    ↓
Backend Authentication System
    ├── Auth Middleware (JWT検証)
    ├── User Management UseCase
    ├── User Repository (SQLite)
    └── JWT Authenticator
```

## 📋 認証の流れ - ステップバイステップ

### Step 1: Google OAuth認証（フロントエンド）

**実装場所:** `frontend/src/app/api/auth/[...nextauth]/route.ts`

```typescript
// NextAuth.js + Google Provider設定
import GoogleProvider from "next-auth/providers/google"

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    })
  ],
  session: { strategy: "jwt" }
}
```

**何が起こるか:**
1. ユーザーが「Googleでログイン」ボタンをクリック
2. Google OAuth認証画面に遷移
3. ユーザーがGoogle認証を完了
4. Google OAuth情報がNextAuthに返される：
   ```json
   {
     "sub": "Google User ID",
     "email": "user@example.com",
     "name": "ユーザー名",
     "picture": "https://lh3.googleusercontent.com/...",
     "email_verified": true
   }
   ```

### Step 2: バックエンド認証（Google情報の送信）

**実装場所:** `frontend/src/hooks/useAuth.ts`

```typescript
// Google OAuth情報をバックエンドに送信
const loginWithGoogle = async (googleUserInfo: any) => {
  const response = await fetch('/api/auth/login/google', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ google_user_info: googleUserInfo })
  })
}
```

**何が起こるか:**
1. フロントエンドがGoogle OAuth情報をバックエンドに送信
2. バックエンドの`/api/auth/login/google`エンドポイントが受信

### Step 3: バックエンドでのユーザー処理

**実装場所:** `backend/src/presentation/api/routes/auth.py`

```python
@router.post("/login/google", response_model=LoginResponse)
async def google_login(
    request: GoogleLoginRequest,
    user_management_usecase: UserManagementUseCase = Depends(get_user_management_usecase)
):
    result = await user_management_usecase.login_with_google_oauth(
        request.google_user_info
    )
```

**何が起こるか:**
1. Google OAuth情報を受信
2. `UserManagementUseCase`に処理を委譲

### Step 4: ユーザー作成/更新処理

**実装場所:** `backend/src/application/usecases/user_management_usecase.py`

```python
async def login_with_google_oauth(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Google OAuth情報からUserエンティティ作成
    user = User.from_google_oauth(google_user_info)
    
    # 2. ユーザー作成または更新（upsert）
    stored_user = await self.user_repository.create_or_update_user(user)
    
    # 3. 最終ログイン時刻を更新
    await self.user_repository.update_last_login(stored_user.google_id)
    
    # 4. JWTトークン生成
    access_token = self.jwt_authenticator.create_access_token(stored_user)
    
    return {
        "success": True,
        "user": stored_user.to_dict(),
        "access_token": access_token,
        "token_type": "bearer"
    }
```

**何が起こるか:**
1. **ユーザーエンティティ作成** - Google OAuth情報を`User`エンティティに変換
2. **Upsert処理** - ユーザーが存在すれば更新、なければ新規作成
3. **ログイン時刻更新** - 最終ログイン時刻を現在時刻に更新
4. **JWTトークン生成** - ユーザー情報からJWTアクセストークンを生成

### Step 5: Userエンティティの作成

**実装場所:** `backend/src/domain/entities.py`

```python
class User:
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
            google_id=oauth_user_info.get("sub", ""),      # Google User ID
            email=oauth_user_info.get("email", ""),
            name=oauth_user_info.get("name", ""),
            picture_url=oauth_user_info.get("picture"),
            locale=oauth_user_info.get("locale"),
            verified_email=oauth_user_info.get("email_verified", False),
        )
```

**何が起こるか:**
- Google OAuth情報（`sub`, `email`, `name`など）をUserエンティティの属性にマッピング
- `google_id`をプライマリキーとして使用
- 作成・更新・最終ログイン時刻を自動設定

### Step 6: データベース保存

**実装場所:** `backend/src/infrastructure/adapters/persistence/user_repository.py`

```python
async def create_or_update_user(self, user: User) -> User:
    """ユーザー作成または更新（upsert）"""
    existing_user = await self.get_user_by_google_id(user.google_id)
    
    if existing_user:
        # 既存ユーザーの更新
        user.created_at = existing_user.created_at  # 作成日時を保持
        return await self.update_user(user)
    else:
        # 新規ユーザー作成
        return await self.create_user(user)
```

**何が起こるか:**
1. **ユーザー存在確認** - `google_id`でユーザーを検索
2. **既存ユーザーの場合** - プロフィール情報を更新（作成日時は保持）
3. **新規ユーザーの場合** - 新しいレコードをデータベースに挿入

### Step 7: JWTトークン生成

**実装場所:** `backend/src/presentation/api/middleware/auth_middleware.py`

```python
def create_access_token(self, user: User) -> str:
    """アクセストークン生成"""
    payload = {
        "sub": user.google_id,              # Subject（ユーザーID）
        "email": user.email,
        "name": user.name,
        "iat": datetime.utcnow(),           # Issued At（発行時刻）
        "exp": datetime.utcnow() + timedelta(minutes=self.settings.JWT_EXPIRE_MINUTES)  # Expiration（有効期限）
    }
    
    token = jwt.encode(
        payload, 
        self.settings.JWT_SECRET,           # 秘密鍵
        algorithm="HS256"                   # 署名アルゴリズム
    )
    
    return token
```

**何が起こるか:**
1. **ペイロード作成** - ユーザー情報をJWTペイロードに設定
2. **有効期限設定** - デフォルト24時間（1440分）
3. **トークン署名** - HS256アルゴリズムで署名
4. **トークン返却** - エンコードされたJWTトークンを返却

### Step 8: トークンの保存（フロントエンド）

**実装場所:** `frontend/src/libs/api.ts`

```typescript
class TokenManager {
  private static readonly TOKEN_KEY = 'backend_token'
  
  setToken(token: string): void {
    localStorage.setItem(TokenManager.TOKEN_KEY, token)
  }
  
  getToken(): string | null {
    return localStorage.getItem(TokenManager.TOKEN_KEY)
  }
}
```

**何が起こるか:**
1. **ローカルストレージ保存** - JWTトークンをlocalStorageに保存
2. **トークン管理** - シングルトンパターンでトークンを管理
3. **認証状態更新** - `backendAuthenticated`フラグをtrueに設定

## 🔐 API認証の仕組み

### Step 9: API呼び出し時の認証

**実装場所:** `backend/src/presentation/api/dependencies.py`

```python
async def get_current_user_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """必須認証 - 認証が必要なエンドポイント用"""
    auth_middleware = get_auth_middleware(request)
    return await auth_middleware.require_authentication(credentials)
```

**何が起こるか:**
1. **Authorizationヘッダー取得** - `Bearer <token>`形式でトークンを取得
2. **認証ミドルウェア呼び出し** - トークン検証処理を実行

### Step 10: トークン検証処理

**実装場所:** `backend/src/presentation/api/middleware/auth_middleware.py`

```python
async def authenticate_request(
    self, 
    authorization: Optional[HTTPAuthorizationCredentials]
) -> Optional[Dict[str, Any]]:
    """
    リクエスト認証
    
    1. JWTトークン検証 (優先)
    2. Google OAuth Token検証 (フォールバック)
    """
    if not authorization:
        return None
    
    token = authorization.credentials
    
    try:
        # 1. JWTトークン検証を試行
        payload = self.jwt_authenticator.verify_token(token)
        
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
            "name": payload["name"],
            "auth_type": "jwt"
        }
        
    except AuthError:
        # 2. Google OAuth Token検証にフォールバック
        google_user_info = await self.google_verifier.verify_google_token(token)
        
        if google_user_info:
            return {
                "user_id": google_user_info["sub"],
                "email": google_user_info["email"],
                "name": google_user_info.get("name", ""),
                "auth_type": "google_oauth"
            }
    
    return None
```

**何が起こるか:**
1. **JWT検証優先** - まずJWTトークンの検証を試行
2. **Google OAuth フォールバック** - JWT検証に失敗した場合、Google OAuth Tokenの検証を試行
3. **ユーザーコンテキスト返却** - 成功時はユーザー情報を返却、失敗時はNoneを返却

### Step 11: JWT詳細検証

**実装場所:** `backend/src/presentation/api/middleware/auth_middleware.py`

```python
def verify_token(self, token: str) -> Dict[str, Any]:
    """JWTトークン検証"""
    try:
        payload = jwt.decode(
            token,
            self.settings.JWT_SECRET,       # 秘密鍵で署名検証
            algorithms=["HS256"]            # HS256アルゴリズムで検証
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthError("トークンの有効期限が切れています")
    except PyJWTError as e:
        raise AuthError("無効なトークンです")
```

**何が起こるか:**
1. **署名検証** - JWT_SECRETでトークンの署名を検証
2. **有効期限チェック** - トークンの有効期限をチェック
3. **ペイロード返却** - 検証成功時はペイロード（ユーザー情報）を返却
4. **エラー処理** - 期限切れや無効なトークンの場合、適切なエラーを投げる

## 🔄 認証の種類とエンドポイント

### 必須認証エンドポイント
```python
# 例: プロフィール取得
@router.get("/profile")
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    # current_userが自動的に注入される
    return {"user_id": current_user["user_id"]}
```

### オプション認証エンドポイント
```python
# 例: パブリックコンテンツ（認証任意）
@router.get("/public-content")
async def get_public_content(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    if current_user:
        # 認証済みユーザー向けの追加情報
        return {"content": "認証済みコンテンツ"}
    else:
        # 未認証ユーザー向けの基本情報
        return {"content": "パブリックコンテンツ"}
```

## 🛡️ セキュリティ機能

### 1. 段階的認証（フォールバック）
```
1次認証: JWTトークン検証（高速）
    ↓（失敗時）
2次認証: Google OAuth Token検証（確実）
    ↓（失敗時）
認証エラー
```

### 2. トークン期限管理
- **JWT有効期限**: 24時間（設定可能）
- **自動期限チェック**: 各API呼び出し時に自動チェック
- **リフレッシュ機能**: `/api/auth/refresh`エンドポイントで新しいトークン取得

### 3. 暗号化・署名
- **JWT署名**: HS256アルゴリズム
- **秘密鍵**: 環境変数`JWT_SECRET`で管理
- **ペイロード暗号化**: 重要情報は暗号化された状態で保存

## 📊 認証状態の管理

### フロントエンド認証状態
```typescript
interface AuthState {
  // NextAuth状態
  session: any
  sessionStatus: 'loading' | 'authenticated' | 'unauthenticated'
  
  // バックエンド認証状態
  backendToken: string | null
  backendUser: any
  backendAuthenticated: boolean
  
  // 統合状態
  fullyAuthenticated: boolean    // 両方とも認証済み
  isLoading: boolean
  error: string | null
}
```

### 認証レベル
1. **未認証** - どちらも未認証
2. **フロントエンドのみ認証** - NextAuthのみ認証済み
3. **完全認証** - NextAuth + バックエンドJWT両方認証済み

## 🔧 設定と環境変数

### バックエンド設定 (.env.dev)
```bash
# Google OAuth設定
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT設定
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRE_MINUTES=1440  # 24時間

# データベース設定
DATABASE_URL=sqlite:///./data/genieus.db
```

### フロントエンド設定 (.env.local)
```bash
# NextAuth設定
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## 🚨 エラーハンドリング

### 認証エラーの種類と対処
1. **401 Unauthorized** - トークンなし/無効
   - 対処: ログイン画面に遷移
2. **403 Forbidden** - 権限不足
   - 対処: 権限エラー画面表示
3. **トークン期限切れ** - JWT有効期限切れ
   - 対処: リフレッシュトークンで再取得

### ログ監視ポイント
```python
# 認証成功ログ
self.logger.info("認証成功", extra={
    "user_id": user_context["user_id"],
    "auth_type": user_context["auth_type"]
})

# 認証失敗ログ
self.logger.warning("認証失敗: 無効なトークン")
```

## 📈 パフォーマンス最適化

### 1. トークン検証の最適化
- **JWTファースト**: 高速なJWT検証を優先
- **フォールバック**: Google API呼び出しは最後の手段

### 2. キャッシュ戦略
- **ユーザー情報キャッシュ**: 同一リクエスト内でのユーザー情報再利用
- **トークン検証結果キャッシュ**: 短期間のトークン検証結果キャッシュ

## 🎯 まとめ

GenieUsの認証システムは以下の特徴を持っています：

1. **二段階認証**: Google OAuth（入口） + JWT（継続認証）
2. **段階的フォールバック**: JWT → Google OAuth Token の順で認証試行
3. **完全な分離**: フロントエンド認証（NextAuth）とバックエンド認証（JWT）の独立性
4. **堅牢なセキュリティ**: 署名検証、期限チェック、エラーハンドリング
5. **開発者フレンドリー**: Dependsパターンでの簡単な認証注入

この認証システムにより、セキュアで使いやすい認証機能を実現しています。