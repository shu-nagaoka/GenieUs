import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // キャッシュ時間を30分に設定（CSRアプリケーションとして最適）
      staleTime: 30 * 60 * 1000, // 30 minutes
      // リフレッシュタイムを1時間に設定
      gcTime: 60 * 60 * 1000, // 1 hour (formerly cacheTime)
      // ネットワークエラーに対する再試行設定
      retry: (failureCount, error) => {
        // 4xx系エラーは再試行しない（認証エラーなど）
        if (error instanceof Error && 'status' in error) {
          const status = (error as unknown as { status: number }).status
          if (status >= 400 && status < 500) {
            return false
          }
        }
        // 最大3回まで再試行
        return failureCount < 3
      },
      // フォーカス時の自動更新を無効化（チャットアプリには不要）
      refetchOnWindowFocus: false,
      // マウント時の自動更新を最小限に
      refetchOnMount: 'always',
      // 接続復旧時の自動更新
      refetchOnReconnect: 'always',
    },
    mutations: {
      // 変更時の再試行設定
      retry: 1,
    },
  },
})