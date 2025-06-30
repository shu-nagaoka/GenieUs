# Stripe技術実装計画

**文書ID**: TECH-STRIPE-001  
**作成日**: 2024-12-29  
**対象**: GenieUs Stripe統合  
**前提**: [Stripe マネタイズ戦略](../plan/stripe-monetization-strategy.md)準拠

## 🏗️ システムアーキテクチャ設計

### 全体構成
```
Frontend (Next.js)
├── Stripe Elements (決済UI)
├── Customer Portal (管理画面)
└── Subscription Management

Backend (FastAPI)
├── Subscription API
├── Webhook Handler
├── User Management
└── Feature Gate Controller

Stripe Services
├── Products & Prices
├── Subscriptions
├── Customer Portal
└── Webhooks
```

## 📦 必要パッケージ

### バックエンド
```bash
# 新規追加
uv add stripe
uv add python-jose[cryptography]  # JWT処理
uv add passlib[bcrypt]           # パスワードハッシュ

# 既存確認
fastapi>=0.104.0
sqlalchemy>=2.0.0
```

### フロントエンド
```bash
# 新規追加
npm install @stripe/stripe-js @stripe/react-stripe-js
npm install @types/stripe        # TypeScript型定義

# 既存確認
next>=15.0.0
react>=18.0.0
typescript>=5.0.0
```

## 🗄️ データベース設計

### 新規テーブル設計
```sql
-- ユーザー拡張（既存usersテーブルに追加）
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255);
ALTER TABLE users ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'free';
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free';

-- サブスクリプション管理
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stripe_subscription_id VARCHAR(255) NOT NULL UNIQUE,
    stripe_customer_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- active, canceled, past_due, etc.
    tier VARCHAR(50) NOT NULL,    -- free, basic, premium, family
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 課金イベント履歴
CREATE TABLE billing_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    stripe_event_id VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,  -- subscription.created, invoice.paid, etc.
    amount INTEGER,  -- 金額（円、小数点なし）
    currency VARCHAR(3) DEFAULT 'jpy',
    status VARCHAR(50),
    metadata TEXT,  -- JSON形式で追加情報
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 機能使用制限
CREATE TABLE feature_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_type VARCHAR(100) NOT NULL,  -- ai_consultation, image_analysis, etc.
    usage_count INTEGER DEFAULT 0,
    period_start DATE,
    period_end DATE,
    reset_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🔧 バックエンド実装

### 1. Stripe設定とDI統合
```python
# src/infrastructure/config/stripe_config.py
from typing import Optional
import stripe
from src.infrastructure.config.settings import get_settings

class StripeConfig:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        stripe.api_key = self.api_key
    
    @property
    def client(self) -> stripe:
        return stripe
```

### 2. サブスクリプション管理UseCase
```python
# src/application/usecases/subscription_usecase.py
from typing import Optional
import stripe
from src.application.interface.protocols.subscription_repository import SubscriptionRepository
from src.domain.entities import User, Subscription
from src.infrastructure.config.stripe_config import StripeConfig

class SubscriptionUseCase:
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        stripe_config: StripeConfig,
        logger
    ):
        self.subscription_repo = subscription_repo
        self.stripe = stripe_config.client
        self.logger = logger
    
    async def create_subscription(
        self, 
        user_id: int, 
        price_id: str
    ) -> dict:
        """サブスクリプション作成"""
        try:
            user = await self.subscription_repo.get_user(user_id)
            
            # Stripeカスタマー作成または取得
            customer = await self._get_or_create_customer(user)
            
            # サブスクリプション作成
            subscription = self.stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                metadata={'user_id': str(user_id)}
            )
            
            # データベース保存
            await self.subscription_repo.save_subscription(
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer.id,
                status=subscription.status,
                tier=self._get_tier_from_price(price_id)
            )
            
            return {
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except Exception as e:
            self.logger.error(f"Subscription creation failed: {e}")
            raise
    
    async def _get_or_create_customer(self, user: User) -> stripe.Customer:
        """Stripeカスタマー取得または作成"""
        if user.stripe_customer_id:
            return self.stripe.Customer.retrieve(user.stripe_customer_id)
        
        customer = self.stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={'user_id': str(user.id)}
        )
        
        await self.subscription_repo.update_user_stripe_customer(
            user.id, customer.id
        )
        
        return customer
```

### 3. Webhook処理
```python
# src/presentation/api/routes/stripe_webhooks.py
from fastapi import APIRouter, Request, HTTPException, Depends
import stripe
from src.di_provider.composition_root import CompositionRoot

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    composition_root: CompositionRoot = Depends()
):
    """Stripeウェブフック処理"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, composition_root.stripe_config.webhook_secret
        )
        
        webhook_handler = composition_root.get_webhook_handler()
        await webhook_handler.handle_event(event)
        
        return {"status": "success"}
        
    except ValueError as e:
        composition_root.logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        composition_root.logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
```

### 4. 機能制限ゲート
```python
# src/application/services/feature_gate_service.py
from enum import Enum
from typing import Dict, Optional
from src.domain.entities import User, SubscriptionTier

class FeatureType(Enum):
    AI_CONSULTATION = "ai_consultation"
    IMAGE_ANALYSIS = "image_analysis"
    GROWTH_RECORD = "growth_record"
    FAMILY_SHARING = "family_sharing"

class FeatureGateService:
    LIMITS: Dict[SubscriptionTier, Dict[FeatureType, Optional[int]]] = {
        SubscriptionTier.FREE: {
            FeatureType.AI_CONSULTATION: 5,
            FeatureType.IMAGE_ANALYSIS: 3,
            FeatureType.GROWTH_RECORD: 10,
            FeatureType.FAMILY_SHARING: 0,
        },
        SubscriptionTier.BASIC: {
            FeatureType.AI_CONSULTATION: None,  # Unlimited
            FeatureType.IMAGE_ANALYSIS: None,
            FeatureType.GROWTH_RECORD: None,
            FeatureType.FAMILY_SHARING: 2,
        },
        # ... 他のティア
    }
    
    async def can_use_feature(
        self, 
        user: User, 
        feature_type: FeatureType
    ) -> tuple[bool, Optional[str]]:
        """機能使用可否判定"""
        limit = self.LIMITS[user.subscription_tier][feature_type]
        
        if limit is None:  # Unlimited
            return True, None
            
        if limit == 0:  # Not allowed
            return False, f"{feature_type.value} is not available in your plan"
            
        current_usage = await self._get_current_usage(user.id, feature_type)
        
        if current_usage >= limit:
            return False, f"Monthly limit reached for {feature_type.value}"
            
        return True, None
```

## 🎨 フロントエンド実装

### 1. Stripe Elements統合
```typescript
// src/components/billing/checkout.tsx
'use client';

import { loadStripe } from '@stripe/stripe-js';
import {
    Elements,
    CardElement,
    useStripe,
    useElements
} from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export function CheckoutForm({ priceId }: { priceId: string }) {
    const stripe = useStripe();
    const elements = useElements();
    
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        
        if (!stripe || !elements) return;
        
        const response = await fetch('/api/subscription/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ price_id: priceId }),
        });
        
        const { client_secret } = await response.json();
        
        const result = await stripe.confirmCardPayment(client_secret, {
            payment_method: {
                card: elements.getElement(CardElement)!,
            }
        });
        
        if (result.error) {
            console.error(result.error.message);
        } else {
            // 成功処理
            window.location.href = '/dashboard?success=true';
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <CardElement />
            <button type="submit" disabled={!stripe}>
                Subscribe
            </button>
        </form>
    );
}
```

### 2. プラン選択コンポーネント
```typescript
// src/components/billing/pricing-plans.tsx
import { CheckoutForm } from './checkout';

interface PricingPlan {
    id: string;
    name: string;
    price: number;
    features: string[];
    stripePrice: string;
    popular?: boolean;
}

const PLANS: PricingPlan[] = [
    {
        id: 'free',
        name: 'フリー',
        price: 0,
        features: ['AI相談 月5回', '成長記録 3枚/月'],
        stripePrice: '',
    },
    {
        id: 'basic',
        name: 'ベーシック',
        price: 980,
        features: ['AI相談 無制限', '成長記録 無制限'],
        stripePrice: 'price_basic_monthly',
        popular: true,
    },
    // ...
];

export function PricingPlans() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
                <PlanCard key={plan.id} plan={plan} />
            ))}
        </div>
    );
}
```

## 🔗 API設計

### RESTエンドポイント
```python
# 主要API
POST   /api/subscription/create           # サブスクリプション作成
GET    /api/subscription/status           # 現在の状態取得
POST   /api/subscription/modify           # プラン変更
POST   /api/subscription/cancel           # キャンセル
GET    /api/subscription/portal           # Customer Portal URL
POST   /webhooks/stripe                   # Stripeイベント受信
GET    /api/billing/history               # 請求履歴
GET    /api/features/usage                # 機能使用状況
```

## 🧪 テスト戦略

### 1. バックエンドテスト
```python
# tests/test_subscription_usecase.py
import pytest
from unittest.mock import Mock, patch
from src.application.usecases.subscription_usecase import SubscriptionUseCase

@pytest.fixture
async def subscription_usecase():
    mock_repo = Mock()
    mock_stripe = Mock()
    mock_logger = Mock()
    return SubscriptionUseCase(mock_repo, mock_stripe, mock_logger)

@patch('stripe.Subscription.create')
async def test_create_subscription_success(mock_create, subscription_usecase):
    # テスト実装
    pass
```

### 2. フロントエンドテスト
```typescript
// __tests__/checkout.test.tsx
import { render, screen } from '@testing-library/react';
import { CheckoutForm } from '../src/components/billing/checkout';

jest.mock('@stripe/stripe-js');
jest.mock('@stripe/react-stripe-js');

test('renders checkout form', () => {
    render(<CheckoutForm priceId="price_test" />);
    expect(screen.getByRole('button', { name: /subscribe/i })).toBeInTheDocument();
});
```

## 🚀 デプロイメント設定

### 環境変数
```bash
# .env.production
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Next.js
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### Webhook設定
- **URL**: `https://your-domain.com/webhooks/stripe`
- **イベント**: 
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`

## 📊 監視・分析

### メトリクス収集
```python
# src/infrastructure/monitoring/subscription_metrics.py
class SubscriptionMetrics:
    async def track_conversion(self, user_id: int, from_tier: str, to_tier: str):
        """コンバージョン追跡"""
        pass
    
    async def track_churn(self, user_id: int, reason: str):
        """チャーン分析"""
        pass
```

## 🔄 次のステップ

1. **環境変数設定**とStripeアカウント設定
2. **データベースマイグレーション**実行
3. **段階的実装**（MVP→フル機能）
4. **テスト環境**でのStripe Testモード確認
5. **本番デプロイ**とWebhook設定

---

**注意**: 本番環境では必ずStripe Liveモードを使用し、適切なエラーハンドリングとログ監視を実装してください。