'use client'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Sparkles, 
  Heart, 
  Star, 
  TrendingUp, 
  Award, 
  Calendar,
  Clock,
  Baby,
  Utensils,
  Moon,
  Activity,
  Download,
  Share2,
  ExternalLink,
  Wand2,
  FileText,
  BarChart3,
  PieChart
} from 'lucide-react'

interface MagicReport {
  id: string
  title: string
  type: 'daily' | 'weekly' | 'monthly' | 'milestone'
  date: string
  summary: string
  highlights: string[]
  stats: {
    label: string
    value: string | number
    icon: string
    trend?: 'up' | 'down' | 'stable'
  }[]
  achievements: {
    title: string
    description: string
    icon: string
  }[]
  recommendations: string[]
  shareUrl?: string
}

export function MagicReportGenerator() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [reports, setReports] = useState<MagicReport[]>([])
  const [selectedReport, setSelectedReport] = useState<MagicReport | null>(null)
  const [showFullReport, setShowFullReport] = useState(false)

  // サンプルレポートデータ
  useEffect(() => {
    const sampleReports: MagicReport[] = [
      {
        id: '1',
        title: '今日のがんばりレポート',
        type: 'daily',
        date: new Date().toISOString().split('T')[0],
        summary: '今日もお疲れさまでした！あなたの愛情がたくさんの成果を生みました。',
        highlights: [
          '夜泣きを3回優しく対応しました',
          '離乳食を完食してもらえました',
          '新しい言葉「まんま」を覚えました'
        ],
        stats: [
          { label: '授乳回数', value: 6, icon: '🍼', trend: 'stable' },
          { label: '睡眠時間', value: '12時間', icon: '😴', trend: 'up' },
          { label: '機嫌の良さ', value: '85%', icon: '😊', trend: 'up' },
          { label: '食事完食率', value: '90%', icon: '🍽️', trend: 'up' }
        ],
        achievements: [
          {
            title: '夜泣き対応マスター',
            description: '今日は夜泣きに落ち着いて対応できました',
            icon: '🌙'
          },
          {
            title: '離乳食完食達成',
            description: '新しいメニューを完食してくれました',
            icon: '🎉'
          }
        ],
        recommendations: [
          '明日は少し疲れそうです。早めのお昼寝をおすすめします',
          '新しいおもちゃに興味を示しています。音の出るものがよさそうです'
        ],
        shareUrl: 'https://GenieUs.app/reports/share/1'
      }
    ]
    setReports(sampleReports)
  }, [])

  // 魔法のレポート生成
  const generateMagicReport = async (type: 'daily' | 'weekly' | 'monthly') => {
    setIsGenerating(true)
    
    // アニメーション効果
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 新しいレポートを生成（実際にはAPIコール）
    const newReport: MagicReport = {
      id: Date.now().toString(),
      title: type === 'daily' ? '今日のがんばりレポート' : 
             type === 'weekly' ? '今週の成長レポート' : '今月の振り返りレポート',
      type,
      date: new Date().toISOString().split('T')[0],
      summary: '✨ ジーニーが魔法でレポートを作成しました',
      highlights: ['新しいレポートが生成されました'],
      stats: [],
      achievements: [],
      recommendations: [],
      shareUrl: `https://GenieUs.app/reports/share/${Date.now()}`
    }
    
    setReports(prev => [newReport, ...prev])
    setSelectedReport(newReport)
    setIsGenerating(false)
  }

  // レポートを共有
  const shareReport = async (report: MagicReport) => {
    if (navigator.share && report.shareUrl) {
      try {
        await navigator.share({
          title: report.title,
          text: report.summary,
          url: report.shareUrl,
        })
      } catch (err) {
        // Web Share API未対応の場合はクリップボードにコピー
        navigator.clipboard.writeText(report.shareUrl)
        alert('レポートリンクをクリップボードにコピーしました')
      }
    } else if (report.shareUrl) {
      navigator.clipboard.writeText(report.shareUrl)
      alert('レポートリンクをクリップボードにコピーしました')
    }
  }

  return (
    <div className="space-y-6">
      
      {/* 魔法のレポート生成器 */}
      <Card className="bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center">
              <Wand2 className="h-5 w-5 text-white" />
            </div>
            魔法のレポート生成器
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-6">
            🧞‍♂️ ジーニーがあなたの頑張りを魔法でレポートにまとめます
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* 今日のレポート */}
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={() => generateMagicReport('daily')}
                disabled={isGenerating}
                className="w-full h-auto p-4 bg-gradient-to-r from-amber-400 to-orange-400 hover:from-amber-500 hover:to-orange-500 flex flex-col items-center gap-2"
              >
                <Calendar className="h-6 w-6" />
                <span className="font-medium">今日のがんばり</span>
                <span className="text-xs opacity-90">デイリーレポート</span>
              </Button>
            </motion.div>

            {/* 今週のレポート */}
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={() => generateMagicReport('weekly')}
                disabled={isGenerating}
                className="w-full h-auto p-4 bg-gradient-to-r from-green-400 to-teal-400 hover:from-green-500 hover:to-teal-500 flex flex-col items-center gap-2"
              >
                <BarChart3 className="h-6 w-6" />
                <span className="font-medium">今週の成長</span>
                <span className="text-xs opacity-90">ウィークリーレポート</span>
              </Button>
            </motion.div>

            {/* 今月のレポート */}
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={() => generateMagicReport('monthly')}
                disabled={isGenerating}
                className="w-full h-auto p-4 bg-gradient-to-r from-purple-400 to-pink-400 hover:from-purple-500 hover:to-pink-500 flex flex-col items-center gap-2"
              >
                <PieChart className="h-6 w-6" />
                <span className="font-medium">今月の振り返り</span>
                <span className="text-xs opacity-90">マンスリーレポート</span>
              </Button>
            </motion.div>
          </div>

          {/* レポート生成中のアニメーション */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                className="mt-6 p-6 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg border border-purple-200"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <div className="text-center">
                  <motion.div
                    className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <Sparkles className="h-8 w-8 text-white" />
                  </motion.div>
                  <h3 className="text-lg font-bold text-purple-800 mb-2">
                    🧞‍♂️ 魔法でレポートを作成中...
                  </h3>
                  <p className="text-purple-600">
                    あなたの愛情の記録を分析して、素敵なレポートを作っています
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>

      {/* レポート一覧 */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <FileText className="h-6 w-6" />
          魔法のレポート履歴
        </h2>
        
        <div className="grid grid-cols-1 gap-4">
          {reports.map((report, index) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="bg-white/80 backdrop-blur-sm hover:shadow-lg transition-all duration-300 hover:scale-[1.02]">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                        report.type === 'daily' ? 'bg-gradient-to-br from-amber-400 to-orange-400' :
                        report.type === 'weekly' ? 'bg-gradient-to-br from-green-400 to-teal-400' :
                        'bg-gradient-to-br from-purple-400 to-pink-400'
                      }`}>
                        {report.type === 'daily' ? <Calendar className="h-6 w-6 text-white" /> :
                         report.type === 'weekly' ? <BarChart3 className="h-6 w-6 text-white" /> :
                         <PieChart className="h-6 w-6 text-white" />}
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-800">{report.title}</h3>
                        <p className="text-sm text-gray-500">{report.date}</p>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => shareReport(report)}
                      >
                        <Share2 className="h-4 w-4 mr-1" />
                        共有
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedReport(report)
                          setShowFullReport(true)
                        }}
                        className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600"
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        詳細
                      </Button>
                    </div>
                  </div>

                  <p className="text-gray-600 mb-4">{report.summary}</p>

                  {/* ハイライト */}
                  {report.highlights.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-800 mb-2 flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-500" />
                        今日のハイライト
                      </h4>
                      <div className="space-y-1">
                        {report.highlights.slice(0, 3).map((highlight, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                            <span className="w-1.5 h-1.5 bg-purple-400 rounded-full"></span>
                            {highlight}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 統計サマリー */}
                  {report.stats.length > 0 && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {report.stats.slice(0, 4).map((stat, idx) => (
                        <div key={idx} className="text-center p-3 bg-gray-50 rounded-lg">
                          <div className="text-lg mb-1">{stat.icon}</div>
                          <div className="text-sm font-bold text-gray-800">{stat.value}</div>
                          <div className="text-xs text-gray-600">{stat.label}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 詳細レポートモーダル */}
      <AnimatePresence>
        {showFullReport && selectedReport && (
          <motion.div
            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowFullReport(false)}
          >
            <motion.div
              className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              initial={{ opacity: 0, scale: 0.9, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 50 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                {/* ヘッダー */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      selectedReport.type === 'daily' ? 'bg-gradient-to-br from-amber-400 to-orange-400' :
                      selectedReport.type === 'weekly' ? 'bg-gradient-to-br from-green-400 to-teal-400' :
                      'bg-gradient-to-br from-purple-400 to-pink-400'
                    }`}>
                      {selectedReport.type === 'daily' ? <Calendar className="h-6 w-6 text-white" /> :
                       selectedReport.type === 'weekly' ? <BarChart3 className="h-6 w-6 text-white" /> :
                       <PieChart className="h-6 w-6 text-white" />}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800">{selectedReport.title}</h2>
                      <p className="text-gray-600">{selectedReport.date}</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => shareReport(selectedReport)}
                    >
                      <Share2 className="h-4 w-4 mr-1" />
                      共有
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowFullReport(false)}
                    >
                      閉じる
                    </Button>
                  </div>
                </div>

                {/* サマリー */}
                <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                  <h3 className="font-bold text-purple-800 mb-2 flex items-center gap-2">
                    <Heart className="h-5 w-5" />
                    ジーニーからのメッセージ
                  </h3>
                  <p className="text-purple-700">{selectedReport.summary}</p>
                </div>

                {/* ハイライト */}
                {selectedReport.highlights.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <Star className="h-5 w-5 text-yellow-500" />
                      今日のハイライト
                    </h3>
                    <div className="space-y-2">
                      {selectedReport.highlights.map((highlight, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                          <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                          <span className="text-gray-700">{highlight}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 達成バッジ */}
                {selectedReport.achievements.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <Award className="h-5 w-5 text-amber-500" />
                      今日の達成バッジ
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {selectedReport.achievements.map((achievement, idx) => (
                        <div key={idx} className="flex items-center gap-3 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-200">
                          <div className="text-2xl">{achievement.icon}</div>
                          <div>
                            <h4 className="font-medium text-gray-800">{achievement.title}</h4>
                            <p className="text-sm text-gray-600">{achievement.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 統計 */}
                {selectedReport.stats.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-500" />
                      今日の数字
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {selectedReport.stats.map((stat, idx) => (
                        <div key={idx} className="text-center p-4 bg-white border border-gray-200 rounded-lg">
                          <div className="text-3xl mb-2">{stat.icon}</div>
                          <div className="text-2xl font-bold text-gray-800 mb-1">{stat.value}</div>
                          <div className="text-sm text-gray-600">{stat.label}</div>
                          {stat.trend && (
                            <div className={`text-xs mt-1 ${
                              stat.trend === 'up' ? 'text-green-600' :
                              stat.trend === 'down' ? 'text-red-600' :
                              'text-gray-600'
                            }`}>
                              {stat.trend === 'up' ? '↗ 改善' :
                               stat.trend === 'down' ? '↘ 注意' :
                               '→ 安定'}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* おすすめアクション */}
                {selectedReport.recommendations.length > 0 && (
                  <div>
                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-purple-500" />
                      明日へのおすすめ
                    </h3>
                    <div className="space-y-2">
                      {selectedReport.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-xs text-white font-bold">{idx + 1}</span>
                          </div>
                          <span className="text-blue-800">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}