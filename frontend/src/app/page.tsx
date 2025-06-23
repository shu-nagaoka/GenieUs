import { redirect } from 'next/navigation'

export default function RootPage() {
  // ルートアクセス時は自動的にダッシュボードにリダイレクト
  redirect('/dashboard')
}