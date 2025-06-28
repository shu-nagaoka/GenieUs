'use client'

import { useState, useMemo } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { AuthCheck } from '@/components/features/auth/auth-check'
import { EffortReportCard } from '@/components/v2/effort-affirmation/EffortReportCard'
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
} from 'lucide-react'
import { MdChildCare, MdFamilyRestroom } from 'react-icons/md'
import { FaHeart, FaStar, FaTrophy } from 'react-icons/fa'
import Link from 'next/link'
import { useEffortRecords, useEffortStats } from '@/hooks/useEffortReports'
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
  const [reportKey, setReportKey] = useState<number>(0)
  const [selectedReport, setSelectedReport] = useState<HistoricalReport | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('card')
  
  // React Query hooks
  const {
    data: effortRecordsData = [],
    isLoading: recordsLoading,
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
    setReportKey(prev => prev + 1) // Force re-render of EffortReportCard
  }

  const regenerateReport = () => {
    setReportKey(prev => prev + 1)
  }

  const openReportModal = (report: HistoricalReport) => {
    setSelectedReport(report)
    setShowModal(true)
  }

  const closeModal = () => {
    setSelectedReport(null)
    setShowModal(false)
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
                            {report.score}/10
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
                        <th className="px-4 py-3 text-center font-medium text-emerald-700">詳細</th>
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
                              {report.score}/10
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
                              詳細
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

          {/* メインレポート */}
          <div className="mb-8">
            <EffortReportCard key={reportKey} periodDays={selectedPeriod} className="w-full" />
          </div>

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
                  <Button
                    onClick={regenerateReport}
                    variant="outline"
                    className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                  >
                    <TrendingUp className="mr-2 h-4 w-4" />
                    レポート更新
                  </Button>
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
                      <p className="text-2xl font-bold">{selectedReport.score}/10</p>
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
              </div>
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

                <Button
                  className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:from-lime-600 hover:to-green-600"
                  onClick={() => setShowSettingsModal(false)}
                >
                  設定完了
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
