# Frontend

このディレクトリには、Linx アプリケーションのフロントエンド関連のコードが含まれています。

## ディレクトリ構造

```
frontend/
├── .husky/                       # Git hooks (pre-commit等)
├── .next/                        # Next.js のビルド成果物
├── coverage/                     # テストカバレッジレポート
├── node_modules/                 # プロジェクトの依存関係
├── public/                       # 静的アセット (画像、フォントなど)
│   └── img/                      # 画像ファイル
├── src/                          # ソースコード
│   ├── __tests__/                # テストファイル
│   │   ├── components/           # コンポーネントテスト
│   │   │   ├── ui/               # UIコンポーネントテスト
│   │   │   └── features/         # 機能別コンポーネントテスト
│   │   └── hooks/                # カスタムフックテスト
│   ├── app/                      # Next.js App Router 関連
│   │   ├── api/                  # API ルートハンドラ
│   │   ├── develop/              # 開発者向けページ
│   │   ├── examples/             # UIコンポーネントのサンプルページ
│   │   ├── knowledge/            # ナレッジベースページ
│   │   ├── login/                # ログインページ
│   │   ├── rag/                  # RAG関連ページ
│   │   ├── register/             # 登録ページ
│   │   ├── globals.css           # グローバルスタイル
│   │   ├── layout.tsx            # ルートレイアウト
│   │   └── page.tsx              # ルートページ
│   ├── components/               # Feature-based コンポーネント構造
│   │   ├── features/             # 機能別コンポーネント
│   │   │   ├── auth/             # 認証関連
│   │   │   ├── rag/              # RAG機能
│   │   │   └── knowledge/        # ナレッジ機能
│   │   ├── layout/               # レイアウトコンポーネント
│   │   ├── ui/                   # 基本UIコンポーネント (shadcn/ui)
│   │   ├── molecules/            # 中間レベルコンポーネント
│   │   ├── organisms/            # 複合コンポーネント
│   │   ├── templates/            # テンプレートコンポーネント
│   │   └── providers/            # Context プロバイダー
│   ├── data/                     # 静的データ・モックデータ
│   ├── hooks/                    # カスタムフック
│   ├── libs/                     # ユーティリティ関数・ライブラリ設定
│   └── types/                    # TypeScript型定義
├── .gitignore                    # Git無視ファイル
├── .prettierrc                   # Prettier設定
├── .prettierignore               # Prettier除外ファイル
├── components.json               # shadcn/ui設定
├── eslint.config.mjs             # ESLint設定
├── jest.config.js                # Jest設定
├── jest.setup.js                 # Jestセットアップファイル
├── middleware.ts                 # Next.jsミドルウェア
├── next-env.d.ts                 # Next.js型定義
├── next.config.ts                # Next.js設定
├── package.json                  # 依存関係・スクリプト
├── playwright.config.ts          # Playwright E2Eテスト設定
├── postcss.config.mjs            # PostCSS設定
├── README.md                     # このファイル
├── tailwind.config.ts            # Tailwind CSS設定
└── tsconfig.json                 # TypeScript設定
```

## 主要技術スタック

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Prisma (クライアントライブラリとして)
- NextAuth.js

## セットアップと実行

1.  **依存関係のインストール:**

    ```bash
    npm install
    ```

2.  **Prisma関連の準備 (初回またはスキーマ変更時):**

    ```bash
    npx prisma generate
    npx prisma migrate deploy # (または npx prisma db push 開発時)
    ```

3.  **開発サーバーの起動:**

    ```bash
    npm run dev
    ```

    アプリケーションは `http://localhost:3000` で起動します。

## ビルド

```bash
npm run build
```

このコマンドは、Prismaのマイグレーションとクライアント生成も実行します。

## 開発ツール

### 🔍 **Lint と Format**

```bash
# ESLint チェック
npm run lint

# ESLint 自動修正
npm run lint:fix

# Prettier フォーマット
npm run format

# Prettier チェック（修正せずに確認のみ）
npm run format:check
```

### 🛡️ **品質管理**

このプロジェクトでは **pre-commit hooks** により、コミット時に自動で品質チェックが実行されます：

- **ESLint** - コード品質チェック
- **Prettier** - コードフォーマット
- **TypeScript** - 型チェック

```bash
# pre-commit hooks を手動実行
npx lint-staged
```

## テスト

### 🧪 **テスト環境**

このプロジェクトでは以下のテストツールを使用しています：

- **Jest** - ユニットテスト・統合テストフレームワーク
- **React Testing Library** - Reactコンポーネントテスト
- **Playwright** - E2Eテスト（ブラウザテスト）
- **@testing-library/user-event** - ユーザーインタラクションシミュレーション

### 📁 **テストファイル構造**

```
src/
├── __tests__/                    # テストファイル
│   ├── components/
│   │   ├── ui/                   # UIコンポーネントテスト
│   │   │   ├── button.test.tsx
│   │   │   ├── card.test.tsx
│   │   │   └── input.test.tsx
│   │   └── features/             # 機能別コンポーネントテスト
│   └── hooks/                    # カスタムフックテスト
├── components/                   # 実際のコンポーネント
└── jest.setup.js                # Jest設定ファイル
```

### 🚀 **テスト実行コマンド**

#### **基本的なテスト実行**

```bash
# 全テスト実行
npm test

# テスト監視モード（ファイル変更時に自動実行）
npm run test:watch

# テストカバレッジ取得
npm run test:coverage
```

#### **E2Eテスト（Playwright）**

```bash
# E2Eテスト実行
npm run test:e2e

# E2Eテストレポート表示
npm run test:e2e:report
```

### 📝 **テストファイルの書き方**

#### **基本的なコンポーネントテスト例**

```typescript
// src/__tests__/components/ui/button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Test Button</Button>)
    expect(screen.getByRole('button', { name: 'Test Button' })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = jest.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>Click me</Button>)

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

#### **新しいテストファイル作成時の命名規則**

- コンポーネントテスト: `ComponentName.test.tsx`
- フックテスト: `useHookName.test.tsx`
- ユーティリティテスト: `utilityName.test.ts`

### 🛠️ **テスト設定**

#### **jest.setup.js の内容**

- `@testing-library/jest-dom` の自動インポート
- `ResizeObserver`, `IntersectionObserver` のモック
- `window.matchMedia` のモック
- Next.js router のモック

#### **テスト対象パス**

- `src/components/**/*.{ts,tsx}`
- `src/hooks/**/*.{ts,tsx}`
- `src/libs/**/*.{ts,tsx}`

### 🎯 **テストのベストプラクティス**

#### **1. AAA パターンを使用**

```typescript
it('should update state when button is clicked', async () => {
  // Arrange (準備)
  const user = userEvent.setup()
  render(<Counter />)

  // Act (実行)
  await user.click(screen.getByRole('button', { name: 'Increment' }))

  // Assert (検証)
  expect(screen.getByText('Count: 1')).toBeInTheDocument()
})
```

#### **2. ユーザーの視点でテスト**

```typescript
// ❌ 実装詳細に依存
expect(component.state.isVisible).toBe(true)

// ✅ ユーザーの視点
expect(screen.getByText('Modal Content')).toBeVisible()
```

#### **3. アクセシブルな要素を使用**

```typescript
// role, label, text で要素を特定
screen.getByRole('button', { name: 'Submit' })
screen.getByLabelText('Email address')
screen.getByText('Welcome message')
```

### 📊 **テストカバレッジ**

テストカバレッジレポートは `coverage/` ディレクトリに出力されます：

```bash
npm run test:coverage
open coverage/lcov-report/index.html  # ブラウザでレポート表示
```

**カバレッジ目標:**

- Statements: 80%+
- Branches: 70%+
- Functions: 80%+
- Lines: 80%+

### 🐛 **トラブルシューティング**

#### **よくある問題と解決法**

**0. package.json が見つからないエラー**

```bash
# エラー: Could not read package.json
# 解決法: frontendディレクトリに移動してから実行
cd frontend
npm test
```

**1. Window/DOM API エラー**

```typescript
// jest.setup.js で適切なモックを追加
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))
```

**2. Next.js router エラー**

```typescript
// jest.setup.js で router をモック
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
  usePathname: () => '/',
}))
```

**3. CSS/スタイル関連エラー**

- Tailwind CSS クラスのテスト時は `className` や `toBeVisible()` を使用
- 具体的なスタイル値ではなく、機能をテスト

### 🔄 **継続的インテグレーション**

プロジェクトには **pre-commit hooks** が設定されており、コミット前に自動で以下が実行されます：

- ESLint チェック
- Prettier フォーマット
- 型チェック

```bash
# 手動で pre-commit チェックを実行
npx lint-staged
```

## 🚀 **クイックスタート**

### **新規開発者向け**

```bash
# 1. 依存関係インストール
npm install

# 2. 開発サーバー起動
npm run dev

# 3. テスト実行確認
npm test

# 4. ブラウザで確認
open http://localhost:3000
```

### **日常的な開発フロー**

```bash
# 1. 機能開発
npm run dev                    # 開発サーバー起動

# 2. テスト駆動開発
npm run test:watch            # テスト監視モード

# 3. コード品質チェック
npm run lint:fix              # リント自動修正
npm run format                # フォーマット

# 4. 最終チェック
npm run test:coverage         # カバレッジ確認
npm run build                 # ビルド確認
```

### **新しいコンポーネント作成時**

```bash
# 1. コンポーネント作成
# src/components/ui/new-component.tsx

# 2. テストファイル作成
# src/__tests__/components/ui/new-component.test.tsx

# 3. テスト実行
npm test new-component.test.tsx

# 4. 統合確認
npm run test:coverage
```

## その他

- 詳細なルーティングや各コンポーネントの役割については、`src` ディレクトリ内の各ファイルを参照してください。
- API のエンドポイントは `src/app/api` 以下に定義されています。
- 認証は NextAuth.js を使用しています。設定は `src/app/api/auth/[...nextauth]/` 配下や関連する環境変数で管理されます。

## 非推奨パッケージの対処法

`npm install` 実行時に以下のような非推奨（deprecated）パッケージの警告が表示される場合があります：

```
npm warn deprecated @types/long@5.0.0: This is a stub types definition. long provides its own type definitions, so you do not need this installed.
npm warn deprecated inflight@1.0.6: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
```

### 対処手順

1. **依存関係の確認**

   どのパッケージが非推奨のパッケージに依存しているかを確認します：

   ```bash
   npm ls <非推奨パッケージ名>
   ```

   例：

   ```bash
   npm ls @types/long
   npm ls inflight
   ```

2. **対処方法の選択**

   **a) 直接的な依存関係の場合（`package.json`に直接記載されている場合）**

   - パッケージのドキュメントやnpmページで代替パッケージや新バージョンを確認
   - 新しいパッケージに更新：
     ```bash
     npm install <新しいパッケージ名またはバージョン>
     ```
   - 不要な場合は削除：
     ```bash
     npm uninstall <非推奨パッケージ名>
     ```

   **b) 間接的な依存関係の場合（他のパッケージが依存している場合）**

   - 親パッケージを最新バージョンに更新：
     ```bash
     npm update <親パッケージ名>
     ```
   - プロジェクト全体の更新を試行：
     ```bash
     npm update
     ```

3. **具体的な対処例**

   **`@types/long` の場合：**

   - `long` パッケージ自体が型定義を提供するため、`@types/long` は不要
   - 対処：
     ```bash
     npm uninstall @types/long
     npm update long
     ```

   **`inflight` の場合：**

   - 通常は他のパッケージの依存関係として含まれる
   - 親パッケージの更新で解決することが多い：
     ```bash
     npm update
     ```

4. **セキュリティ脆弱性がある場合**

   `npm audit` でセキュリティ脆弱性もチェックできます：

   ```bash
   npm audit
   npm audit fix  # 自動修正を試行
   npm audit fix --force  # 破壊的変更を含む修正（要注意）
   ```

### 注意事項

- `npm audit fix --force` は破壊的な変更を伴う可能性があるため、実行前にコードをバックアップしてください
- パッケージ更新後は、アプリケーションが正常に動作することを確認してください
- 大きなバージョンアップが含まれる場合は、BREAKING CHANGESを確認してください
