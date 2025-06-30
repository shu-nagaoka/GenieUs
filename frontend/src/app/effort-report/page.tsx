'use client'

import { useState, useMemo } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { AuthCheck } from '@/components/features/auth/auth-check'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Heart,
  Calendar,
  TrendingUp,
  Award,
  Sparkles,
  Clock,
  BarChart3,
  Star,
  CheckCircle,
  Target,
  Eye,
  FileText,
  X,
  Archive,
  Activity,
  LayoutGrid,
  List,
  Trash2,
} from 'lucide-react'
import { MdChildCare, MdFamilyRestroom } from 'react-icons/md'
import { FaHeart, FaStar, FaTrophy } from 'react-icons/fa'
import Link from 'next/link'
import { useEffortRecords, useEffortStats, useGenerateEffortReport, useDeleteEffortRecord } from '@/hooks/useEffortReports'
import type { EffortRecord as ApiEffortRecord } from '@/libs/api/effort-records'

interface HistoricalReport {
  id: string
  date: string
  period: string
  effortCount: number
  highlights: string[]
  score: number
  categories: {
    feeding: number
    sleep: number
    play: number
    care: number
  }
  summary: string
  achievements: string[]
}

type ViewMode = 'card' | 'table'

export default function EffortReportPage() {
  return (
    <AuthCheck>
      <EffortReportPageContent />
    </AuthCheck>
  )
}

function EffortReportPageContent() {
  const [selectedPeriod, setSelectedPeriod] = useState<number>(7)
  const [selectedReport, setSelectedReport] = useState<HistoricalReport | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('card')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [reportToDelete, setReportToDelete] = useState<HistoricalReport | null>(null)
  const [showSuccessNotification, setShowSuccessNotification] = useState(false)
  const [newReportId, setNewReportId] = useState<string | null>(null)
  const [showCreateConfirm, setShowCreateConfirm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  
  // React Query hooks
  const {
    data: effortRecordsData = [],
    isLoading: recordsLoading,
    refetch: refetchRecords,
  } = useEffortRecords('frontend_user')
  
  const {
    data: stats = {
      total_efforts: 27,
      streak_days: 21,
      average_score: 8.7,
      total_reports: 12,
    },
    isLoading: statsLoading,
  } = useEffortStats('frontend_user', selectedPeriod)

  // レポート生成Mutation
  const generateReportMutation = useGenerateEffortReport({
    onSuccess: (data) => {
      if (data.success && data.id) {
        setNewReportId(data.id)
        setShowSuccessNotification(true)
        // 5秒後に通知を自動で閉じる
        setTimeout(() => {
          setShowSuccessNotification(false)
          setNewReportId(null)
        }, 5000)
      }
    },
  })
  
  // 削除Mutation
  const deleteReportMutation = useDeleteEffortRecord()

  // APIデータをUIフォーマットに変換（メモ化）
  const historicalReports = useMemo(() => {
    return effortRecordsData.map((apiRecord: ApiEffortRecord) => ({
      id: apiRecord.id,
      date: apiRecord.date,
      period: apiRecord.period,
      effortCount: apiRecord.effort_count,
      highlights: apiRecord.highlights,
      score: apiRecord.score,
      categories: apiRecord.categories,
      summary: apiRecord.summary,
      achievements: apiRecord.achievements,
    }))
  }, [effortRecordsData])

  const loading = recordsLoading || statsLoading

  const handlePeriodChange = (value: string) => {
    setSelectedPeriod(parseInt(value))
  }

  const handleGenerateReport = () => {
    setShowCreateConfirm(true)
  }

  const handleCreateConfirm = async () => {
    setIsCreating(true)
    
    try {
      const result = await generateReportMutation.mutateAsync({
        userId: 'frontend_user',
        periodDays: selectedPeriod,
      })
      
      if (result.success) {
        console.log('✅ レポートが正常に生成されました:', result.data?.id)
        setShowCreateConfirm(false)
        setIsCreating(false)
      } else {
        console.error('❌ レポート生成に失敗:', result.message)
        setIsCreating(false)
      }
    } catch (error) {
      console.error('❌ レポート生成エラー:', error)
      setIsCreating(false)
    }
  }

  const handleCreateCancel = () => {
    setShowCreateConfirm(false)
    setIsCreating(false)
  }

  const openReportModal = (report: HistoricalReport) => {
    setSelectedReport(report)
    setShowModal(true)
  }

  const closeModal = () => {
    setSelectedReport(null)
    setShowModal(false)
  }

  const handleDeleteClick = (report: HistoricalReport, e: React.MouseEvent) => {
    e.stopPropagation()
    setReportToDelete(report)
    setShowDeleteConfirm(true)
  }

  const handleDeleteConfirm = async () => {
    if (!reportToDelete) return
    
    try {
      const result = await deleteReportMutation.mutateAsync({
        recordId: reportToDelete.id,
        userId: 'frontend_user',
      })
      
      if (result.success) {
        console.log('✅ レポートが削除されました:', reportToDelete.id)
        setShowDeleteConfirm(false)
        setReportToDelete(null)
        // モーダルが開いていて削除されたレポートと同じなら閉じる
        if (showModal && selectedReport?.id === reportToDelete.id) {
          setShowModal(false)
          setSelectedReport(null)
        }
      } else {
        console.error('❌ レポート削除に失敗:', result.message)
      }
    } catch (error) {
      console.error('❌ レポート削除エラー:', error)
    }
  }

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false)
    setReportToDelete(null)
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-emerald-50 via-teal-50 to-slate-50">
          <div className="inline-flex items-center gap-2">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent"></div>
            <span className="text-gray-600">努力記録を読み込み中...</span>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-slate-50">
        {/* ページヘッダー */}
        <div className="border-b border-emerald-100 bg-white/80 backdrop-blur-sm">
          <div className="mx-auto max-w-6xl px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg">
                  <FaTrophy className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">がんばったことレポート</h1>
                  <p className="text-gray-600">あなたの愛情と努力を記録・実感します</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <Button
                  onClick={handleGenerateReport}
                  disabled={generateReportMutation.isPending}
                  className="bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg hover:from-yellow-600 hover:to-amber-600"
                >
                  {generateReportMutation.isPending ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                      生成中...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="mr-2 h-4 w-4" />
                      今すぐ作成
                    </>
                  )}
                </Button>
                <Link href="/chat">
                  <Button className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg hover:from-lime-600 hover:to-green-600">
                    <Sparkles className="mr-2 h-4 w-4" />
                    Genieに相談
                  </Button>
                </Link>
                <div className="hidden items-center gap-2 rounded-lg border border-emerald-200 bg-white/60 px-3 py-1.5 backdrop-blur-sm md:flex">
                  <Sparkles className="h-4 w-4 text-emerald-600" />
                  <span className="text-sm font-medium text-emerald-700">毎日自動作成</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-6xl space-y-8 p-6">
          {/* 努力サマリーカード */}
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <Card className="border-0 bg-gradient-to-br from-emerald-600 to-emerald-700 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-emerald-100">今週頑張ったこと</p>
                    <p className="mt-1 text-2xl font-bold">{stats.total_efforts}回</p>
                    <p className="text-xs text-emerald-200">Genieが記録</p>
                  </div>
                  <Heart className="h-8 w-8 text-emerald-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-gradient-to-br from-teal-500 to-teal-600 text-white shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-teal-100">平均スコア</p>
                    <p className="mt-1 text-2xl font-bold">{stats.average_score}</p>
                    <p className="text-xs text-teal-200">総合評価</p>
                  </div>
                  <Star className="h-8 w-8 text-teal-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 簡単な設定ボタン */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-2xl font-bold text-gray-800">
                現在の表示期間: 過去{selectedPeriod}日間
              </h2>
            </div>
            <Button
              variant="outline"
              className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
              onClick={() => setShowSettingsModal(true)}
            >
              <Target className="mr-2 h-4 w-4" />
              設定
            </Button>
          </div>

          {/* 過去のレポート一覧 */}
          <Card className="border-0 bg-white/80 shadow-xl backdrop-blur-sm">
            <CardHeader className="rounded-t-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-3">
                    <Archive className="h-6 w-6" />
                    過去のレポート
                  </CardTitle>
                  <CardDescription className="text-emerald-100">
                    これまでのあなたの努力の記録を振り返る
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2 rounded-lg bg-white/20 p-1">
                  <Button
                    size="sm"
                    variant={viewMode === 'card' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('card')}
                    className={`h-8 px-3 ${viewMode === 'card' ? 'bg-white text-emerald-600' : 'text-white hover:bg-white/20'}`}
                  >
                    <LayoutGrid className="mr-1 h-4 w-4" />
                    カード
                  </Button>
                  <Button
                    size="sm"
                    variant={viewMode === 'table' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('table')}
                    className={`h-8 px-3 ${viewMode === 'table' ? 'bg-white text-emerald-600' : 'text-white hover:bg-white/20'}`}
                  >
                    <List className="mr-1 h-4 w-4" />
                    テーブル
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {viewMode === 'card' ? (
                // カード表示
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {historicalReports.map(report => (
                    <Card
                      key={report.id}
                      className="cursor-pointer border-0 bg-gradient-to-br from-white to-emerald-50 shadow-md transition-all duration-200 hover:from-emerald-50 hover:to-teal-50 hover:shadow-lg"
                      onClick={() => openReportModal(report)}
                    >
                      <CardContent className="p-5">
                        <div className="mb-3 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600">
                              <FileText className="h-4 w-4 text-white" />
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-gray-800">{report.period}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(report.date).toLocaleDateString('ja-JP')}
                              </p>
                            </div>
                          </div>
                          <Badge className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
                            {report.score}/100
                          </Badge>
                        </div>

                        <div className="space-y-3">
                          <div>
                            <p className="mb-1 text-sm font-medium text-gray-700">努力回数</p>
                            <div className="flex items-center gap-2">
                              <div className="h-2 flex-1 rounded-full bg-gray-200">
                                <div
                                  className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600"
                                  style={{
                                    width: `${Math.min((report.effortCount / 30) * 100, 100)}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-sm font-bold text-emerald-700">
                                {report.effortCount}回
                              </span>
                            </div>
                          </div>

                          <div>
                            <p className="mb-2 text-sm font-medium text-gray-700">ハイライト</p>
                            <div className="space-y-1">
                              {report.highlights.slice(0, 2).map((highlight, index) => (
                                <div key={index} className="flex items-center gap-2">
                                  <Star className="h-3 w-3 flex-shrink-0 text-emerald-600" />
                                  <p className="line-clamp-1 text-xs text-gray-600">{highlight}</p>
                                </div>
                              ))}
                              {report.highlights.length > 2 && (
                                <p className="pl-5 text-xs text-gray-500">
                                  +{report.highlights.length - 2}件のハイライト
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                              onClick={e => {
                                e.stopPropagation()
                                openReportModal(report)
                              }}
                            >
                              <Eye className="mr-2 h-3 w-3" />
                              詳細を見る
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                // テーブル表示
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-emerald-200">
                        <th className="px-4 py-3 text-left font-medium text-emerald-700">期間</th>
                        <th className="px-4 py-3 text-left font-medium text-emerald-700">日付</th>
                        <th className="px-4 py-3 text-center font-medium text-emerald-700">
                          努力回数
                        </th>
                        <th className="px-4 py-3 text-center font-medium text-emerald-700">
                          スコア
                        </th>
                        <th className="px-4 py-3 text-left font-medium text-emerald-700">
                          主なハイライト
                        </th>
                        <th className="px-4 py-3 text-center font-medium text-emerald-700">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      {historicalReports.map(report => (
                        <tr
                          key={report.id}
                          className="cursor-pointer border-b border-gray-100 transition-colors hover:bg-emerald-50/50"
                          onClick={() => openReportModal(report)}
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600">
                                <FileText className="h-3 w-3 text-white" />
                              </div>
                              <span className="text-sm font-medium text-gray-800">
                                {report.period}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">
                            {new Date(report.date).toLocaleDateString('ja-JP')}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Badge
                              variant="outline"
                              className="border-emerald-300 text-emerald-700"
                            >
                              {report.effortCount}回
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Badge className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
                              {report.score}/100
                            </Badge>
                          </td>
                          <td className="px-4 py-3">
                            <div className="space-y-1">
                              {report.highlights.slice(0, 2).map((highlight, index) => (
                                <div key={index} className="flex items-center gap-2">
                                  <Star className="h-3 w-3 flex-shrink-0 text-emerald-600" />
                                  <p className="truncate text-xs text-gray-600">{highlight}</p>
                                </div>
                              ))}
                              {report.highlights.length > 2 && (
                                <p className="text-xs text-gray-500">
                                  +{report.highlights.length - 2}件
                                </p>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <Button
                              variant="outline"
                              size="sm"
                              className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                              onClick={e => {
                                e.stopPropagation()
                                openReportModal(report)
                              }}
                            >
                              <Eye className="mr-1 h-3 w-3" />
                              詳細を見る
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>


          {/* AIチャット連携カード */}
          <Card className="border-0 bg-gradient-to-br from-lime-50 to-green-50 shadow-xl">
            <CardHeader className="rounded-t-lg bg-gradient-to-r from-emerald-500 to-teal-600 text-white">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとの連携
              </CardTitle>
              <CardDescription className="text-emerald-100">
                このレポートはGenieとの会話で活用され、あなたの努力を認めたよりよいアドバイスを提供します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="rounded-lg border border-emerald-200 bg-white/60 p-4">
                <div className="mb-4 flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg">
                    <FaTrophy className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="mb-2 text-sm font-medium text-emerald-800">
                      💡 Genieは、あなたの努力レポートを理解して：
                    </p>
                    <ul className="space-y-1 text-sm text-emerald-700">
                      <li>• 「今日も頑張りましたね」と具体的に認めてくれます</li>
                      <li>• あなたの努力の傾向を考慮したアドバイスをします</li>
                      <li>• 成長を実感できる振り返りを一緒にしてくれます</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg hover:from-lime-600 hover:to-green-600">
                      <Sparkles className="mr-2 h-4 w-4" />
                      Genieに努力を報告・相談
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>


          {/* 自動作成の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/60 px-4 py-2 backdrop-blur-sm">
              <Clock className="h-4 w-4 text-emerald-600" />
              <span className="text-sm font-medium text-emerald-700">
                毎日21:00に自動作成されます
              </span>
            </div>
          </div>
        </div>

        {/* レポート詳細モーダル */}
        {showModal && selectedReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-2xl">
              {/* モーダルヘッダー */}
              <div className="sticky top-0 rounded-t-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold">努力レポート</h2>
                    <p className="text-emerald-100">
                      {selectedReport.period} -{' '}
                      {new Date(selectedReport.date).toLocaleDateString('ja-JP')}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={closeModal}
                    className="text-white hover:bg-white/20"
                  >
                    <X className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              {/* モーダルコンテンツ */}
              <div className="space-y-6 p-6">
                {/* サマリー */}
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <Card className="border-0 bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-emerald-100">努力回数</p>
                      <p className="text-2xl font-bold">{selectedReport.effortCount}回</p>
                    </CardContent>
                  </Card>

                  <Card className="border-0 bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-blue-100">総合スコア</p>
                      <p className="text-2xl font-bold">{selectedReport.score}/100</p>
                    </CardContent>
                  </Card>

                  <Card className="border-0 bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-purple-100">ハイライト</p>
                      <p className="text-2xl font-bold">{selectedReport.highlights.length}件</p>
                    </CardContent>
                  </Card>
                </div>

                {/* サマリーテキスト */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-emerald-600" />
                      期間サマリー
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="leading-relaxed text-gray-700">{selectedReport.summary}</p>
                  </CardContent>
                </Card>

                {/* カテゴリ別スコア */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-emerald-600" />
                      カテゴリ別スコア
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          key: 'feeding',
                          label: '食事・授乳',
                          color: 'from-orange-500 to-red-600',
                        },
                        { key: 'sleep', label: '睡眠', color: 'from-blue-500 to-indigo-600' },
                        {
                          key: 'play',
                          label: '遊び・学び',
                          color: 'from-green-500 to-emerald-600',
                        },
                        { key: 'care', label: 'ケア・世話', color: 'from-purple-500 to-pink-600' },
                      ].map(({ key, label, color }) => (
                        <div key={key}>
                          <div className="mb-2 flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-700">{label}</span>
                            <span className="text-sm font-bold text-gray-800">
                              {
                                selectedReport.categories[
                                  key as keyof typeof selectedReport.categories
                                ]
                              }
                              %
                            </span>
                          </div>
                          <div className="h-3 rounded-full bg-gray-200">
                            <div
                              className={`h-3 bg-gradient-to-r ${color} rounded-full transition-all duration-500`}
                              style={{
                                width: `${selectedReport.categories[key as keyof typeof selectedReport.categories]}%`,
                              }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* ハイライト */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Star className="h-5 w-5 text-emerald-600" />
                      今週のハイライト
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {selectedReport.highlights.map((highlight, index) => (
                        <div
                          key={index}
                          className="flex items-start gap-3 rounded-lg border border-emerald-200 bg-gradient-to-r from-lime-50 to-green-50 p-3"
                        >
                          <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600">
                            <Star className="h-3 w-3 text-white" />
                          </div>
                          <p className="text-sm text-gray-700">{highlight}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 達成事項 */}
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Award className="h-5 w-5 text-emerald-600" />
                      達成事項
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.achievements.map((achievement, index) => (
                        <Badge
                          key={index}
                          className="bg-gradient-to-r from-emerald-500 to-teal-600 px-3 py-1 text-white"
                        >
                          <Award className="mr-1 h-3 w-3" />
                          {achievement}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* あなたの努力レポート */}
                <Card className="border-0 bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 shadow-lg">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-3 text-amber-800">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-orange-400">
                        <Heart className="h-4 w-4 text-white" />
                      </div>
                      あなたの努力レポート
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* AI生成されたハイライト */}
                    {selectedReport.highlights.length > 0 && (
                      <div className="space-y-3">
                        {selectedReport.highlights.map((highlight, index) => (
                          <div
                            key={index}
                            className="flex items-start gap-3 rounded-lg border border-amber-200 bg-gradient-to-r from-amber-100 to-orange-100 p-4"
                          >
                            <Sparkles className="mt-1 h-5 w-5 flex-shrink-0 text-amber-600" />
                            <p className="leading-relaxed text-amber-800">{highlight}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* AI生成されたサマリー */}
                    {selectedReport.summary && (
                      <div className="rounded-lg border border-amber-200 bg-gradient-to-r from-amber-100 to-orange-100 p-4">
                        <div className="flex items-start gap-3">
                          <Heart className="mt-1 h-6 w-6 flex-shrink-0 text-amber-600" />
                          <div>
                            <h4 className="mb-2 font-medium text-amber-900">Genieからのメッセージ</h4>
                            <p className="leading-relaxed text-amber-800">{selectedReport.summary}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* AI生成された達成項目 */}
                    {selectedReport.achievements.length > 0 && (
                      <div>
                        <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-amber-700">
                          <CheckCircle className="h-4 w-4 text-amber-600" />
                          今週の頑張りポイント
                        </h4>
                        <div className="space-y-2">
                          {selectedReport.achievements.map((achievement, index) => (
                            <div
                              key={index}
                              className="flex items-start gap-3 rounded-lg border border-amber-100 bg-white/60 p-3"
                            >
                              <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
                              <span className="text-sm text-amber-800">{achievement}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* 削除セクション - モーダル下部 */}
                <Card className="border-0 bg-gradient-to-br from-red-50 to-orange-50 shadow-lg">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-3 text-red-800">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-red-400 to-orange-400">
                        <Trash2 className="h-4 w-4 text-white" />
                      </div>
                      レポートの削除
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-lg border border-red-200 bg-red-50/50 p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-red-500 text-white">
                          ⚠️
                        </div>
                        <div>
                          <h4 className="font-medium text-red-900">削除の注意事項</h4>
                          <p className="mt-1 text-sm text-red-800">
                            このレポートを削除すると、データは完全に失われ、復元することはできません。
                            削除は慎重に行ってください。
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <Button
                        onClick={e => {
                          if (selectedReport) {
                            handleDeleteClick(selectedReport, e)
                          }
                        }}
                        variant="outline"
                        className="border-red-300 text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        このレポートを削除する
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* 削除確認ダイアログ */}
        {showDeleteConfirm && reportToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="w-full max-w-md rounded-xl bg-white shadow-2xl">
              {/* ダイアログヘッダー */}
              <div className="rounded-t-xl bg-gradient-to-r from-red-500 to-red-600 p-4 text-white">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                    <Trash2 className="h-4 w-4" />
                  </div>
                  <h2 className="text-lg font-bold">レポートを削除</h2>
                </div>
              </div>

              {/* ダイアログコンテンツ */}
              <div className="space-y-4 p-6">
                <div className="text-center">
                  <p className="mb-2 text-lg font-medium text-gray-800">
                    このレポートを削除しますか？
                  </p>
                  <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                    <p className="text-sm font-medium text-gray-700">{reportToDelete.period}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(reportToDelete.date).toLocaleDateString('ja-JP')}
                    </p>
                  </div>
                  <p className="mt-3 text-sm text-red-600">
                    ⚠️ この操作は取り消せません
                  </p>
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                    onClick={handleDeleteCancel}
                  >
                    キャンセル
                  </Button>
                  <Button
                    onClick={handleDeleteConfirm}
                    disabled={deleteReportMutation.isPending}
                    className="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700"
                  >
                    {deleteReportMutation.isPending ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                        削除中...
                      </>
                    ) : (
                      <>
                        <Trash2 className="mr-2 h-4 w-4" />
                        削除する
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* レポート作成確認ダイアログ */}
        {showCreateConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="w-full max-w-md rounded-xl bg-white shadow-2xl">
              {/* ダイアログヘッダー */}
              <div className="rounded-t-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-4 text-white">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <h2 className="text-lg font-bold">努力レポート作成</h2>
                </div>
              </div>

              {/* ダイアログコンテンツ */}
              <div className="space-y-4 p-6">
                {!isCreating ? (
                  <>
                    <div className="text-center">
                      <p className="mb-2 text-lg font-medium text-gray-800">
                        過去{selectedPeriod}日間の努力レポートを作成しますか？
                      </p>
                      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                        <p className="text-sm font-medium text-emerald-700">作成期間</p>
                        <p className="text-xs text-emerald-600">
                          {new Date(Date.now() - selectedPeriod * 24 * 60 * 60 * 1000).toLocaleDateString('ja-JP')} 〜 {new Date().toLocaleDateString('ja-JP')}
                        </p>
                      </div>
                      <p className="mt-3 text-sm text-gray-600">
                        ✨ AIがあなたの子育ての努力を分析して、素敵なレポートを作成します
                      </p>
                    </div>

                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50"
                        onClick={handleCreateCancel}
                      >
                        キャンセル
                      </Button>
                      <Button
                        onClick={handleCreateConfirm}
                        className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700"
                      >
                        <Sparkles className="mr-2 h-4 w-4" />
                        作成する
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="text-center space-y-4">
                    <div className="flex justify-center">
                      <div className="h-12 w-12 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-600"></div>
                    </div>
                    <div>
                      <p className="text-lg font-medium text-gray-800">レポートを作成中...</p>
                      <p className="mt-1 text-sm text-gray-600">
                        AIがあなたの子育ての記録を分析しています
                      </p>
                    </div>
                    <div className="space-y-2">
                      <div className="h-2 w-full rounded-full bg-gray-200">
                        <div className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600 animate-pulse" style={{width: '70%'}}></div>
                      </div>
                      <p className="text-xs text-gray-500">分析中... しばらくお待ちください</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* レポート作成成功通知 */}
        {showSuccessNotification && (
          <div className="fixed bottom-6 right-6 z-50 max-w-sm rounded-xl bg-white shadow-2xl border border-emerald-200">
            <div className="rounded-t-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-4 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                    <CheckCircle className="h-4 w-4" />
                  </div>
                  <h3 className="font-bold">レポート作成完了!</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowSuccessNotification(false)
                    setNewReportId(null)
                  }}
                  className="text-white hover:bg-white/20 h-6 w-6 p-0"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            </div>
            <div className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100">
                  <Sparkles className="h-3 w-3 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    新しい努力レポートが作成されました
                  </p>
                  <p className="mt-1 text-xs text-gray-600">
                    上の一覧に新しいカードが追加されています
                  </p>
                </div>
              </div>
              
              {newReportId && (
                <div className="mt-3 flex gap-2">
                  <Button
                    size="sm"
                    className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700"
                    onClick={() => {
                      // 新しく作成されたレポートを開く
                      const newReport = historicalReports.find(r => r.id === newReportId)
                      if (newReport) {
                        openReportModal(newReport)
                        setShowSuccessNotification(false)
                        setNewReportId(null)
                      }
                    }}
                  >
                    <Eye className="mr-1 h-3 w-3" />
                    今すぐ確認
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setShowSuccessNotification(false)
                      setNewReportId(null)
                    }}
                    className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                  >
                    閉じる
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 設定モーダル */}
        {showSettingsModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="w-full max-w-md rounded-xl bg-white shadow-2xl">
              {/* モーダルヘッダー */}
              <div className="rounded-t-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-4 text-white">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold">レポート設定</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowSettingsModal(false)}
                    className="text-white hover:bg-white/20"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* モーダルコンテンツ */}
              <div className="space-y-4 p-6">
                <div>
                  <Label className="mb-2 block text-sm font-medium text-gray-700">期間設定</Label>
                  <Select value={selectedPeriod.toString()} onValueChange={handlePeriodChange}>
                    <SelectTrigger className="border-emerald-200 focus:border-emerald-400">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">過去3日間</SelectItem>
                      <SelectItem value="7">過去1週間</SelectItem>
                      <SelectItem value="14">過去2週間</SelectItem>
                      <SelectItem value="30">過去1ヶ月</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="rounded-lg border border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 p-4">
                  <div className="text-center">
                    <p className="mb-1 text-sm font-medium text-gray-700">自動作成</p>
                    <p className="text-lg font-bold text-green-600">毎日 21:00</p>
                    <p className="text-xs text-green-700">自動生成</p>
                  </div>
                </div>

                <div className="rounded-lg border border-purple-200 bg-gradient-to-r from-purple-50 to-violet-50 p-4">
                  <div className="text-center">
                    <p className="mb-1 text-sm font-medium text-gray-700">総レポート数</p>
                    <p className="text-lg font-bold text-purple-600">{stats.total_reports}件</p>
                    <p className="text-xs text-purple-700">生成済み</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={handleGenerateReport}
                    disabled={generateReportMutation.isPending}
                    className="flex-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-yellow-600 hover:to-amber-600"
                  >
                    {generateReportMutation.isPending ? (
                      <>
                        <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                        生成中...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="mr-2 h-4 w-4" />
                        今すぐ作成
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1 border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                    onClick={() => setShowSettingsModal(false)}
                  >
                    設定完了
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
