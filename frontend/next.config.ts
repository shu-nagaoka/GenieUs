import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // パフォーマンス最適化を有効化
  reactStrictMode: true,

  // Cloud Run用standalone出力設定
  output: 'standalone',

  // 画像最適化
  images: {
    domains: ['localhost'],
    formats: ['image/avif', 'image/webp'],
  },

  // 実験的最適化機能
  experimental: {
    optimizePackageImports: [
      'react-icons',
      '@radix-ui/react-alert-dialog',
      '@radix-ui/react-button',
      '@radix-ui/react-card',
      '@radix-ui/react-dialog',
      '@radix-ui/react-dropdown-menu',
      '@radix-ui/react-label',
      '@radix-ui/react-separator',
      '@radix-ui/react-sheet',
      '@radix-ui/react-slot',
      '@radix-ui/react-toast',
      'lucide-react',
    ],
  },

  // API プロキシ設定は削除（直接バックエンド呼び出し）

  // Cloud Run環境変数対応
  env: {
    BACKEND_API_URL: process.env.BACKEND_API_URL || 'http://localhost:8000',
  },

  // 開発時のみエラーを無視（本番では有効）
  ...(process.env.NODE_ENV === 'development' && {
    eslint: { ignoreDuringBuilds: true },
    typescript: { ignoreBuildErrors: true },
  }),
}

export default nextConfig
