'use client'

import { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Calendar,
  Clock,
  Sparkles,
  MapPin,
  Stethoscope,
  Heart,
  Baby,
  Users,
  Target,
  CheckCircle,
  Plus,
  Star,
  Grid3X3,
  LayoutList,
  ChevronLeft,
  ChevronRight,
  Edit
} from 'lucide-react'
import { MdEvent, MdVaccines, MdOutdoorGrill } from 'react-icons/md'
import { FaCalendarAlt, FaStar, FaHeart, FaMapMarkerAlt } from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'
import Link from 'next/link'
import { getScheduleEvents, ScheduleEvent as ApiScheduleEvent } from '@/lib/api/schedules'
import { CreateScheduleModal } from '@/components/features/schedule/create-schedule-modal'
import { EditScheduleModal } from '@/components/features/schedule/edit-schedule-modal'

// APIから取得したデータを表示用に変換するインターフェース
interface ScheduleEvent extends Omit<ApiScheduleEvent, 'user_id' | 'created_at' | 'updated_at' | 'created_by'> {
  subtype?: 'vaccination' | 'checkup' | 'event' | 'ceremony' | 'class'
  createdBy: 'genie' | 'user'
}

export default function SchedulePlanningPage() {
  const [selectedTab, setSelectedTab] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'cards' | 'calendar'>('cards')
  const [scheduleEvents, setScheduleEvents] = useState<ScheduleEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedEvent, setSelectedEvent] = useState<ApiScheduleEvent | null>(null)

  // APIからスケジュールデータを取得
  const loadScheduleEvents = async () => {
    try {
      setLoading(true)
      const result = await getScheduleEvents({ user_id: 'frontend_user' })
      
      if (result.success && result.data) {
        // APIデータを表示用に変換
        const convertedEvents: ScheduleEvent[] = result.data.map(apiEvent => ({
          id: apiEvent.id,
          title: apiEvent.title,
          date: apiEvent.date,
          time: apiEvent.time,
          type: apiEvent.type,
          location: apiEvent.location,
          description: apiEvent.description,
          status: apiEvent.status,
          createdBy: apiEvent.created_by,
          // 既存のフロントエンドロジック用にsubtypeを推定
          subtype: apiEvent.type === 'medical' ? 
            (apiEvent.title.includes('ワクチン') || apiEvent.title.includes('接種') ? 'vaccination' : 'checkup') :
            undefined
        }))
        setScheduleEvents(convertedEvents)
      } else {
        console.error('スケジュール取得に失敗しました:', result.message)
      }
    } catch (error) {
      console.error('スケジュール読み込みエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  // 初回ロード
  useEffect(() => {
    loadScheduleEvents()
  }, [])

  // サンプルデータ（バックアップ用）
  const sampleScheduleEvents: ScheduleEvent[] = [
    {
      id: '1',
      title: '1歳6ヶ月健診',
      date: '2025-07-03',
      time: '14:00',
      type: 'medical',
      subtype: 'checkup',
      location: 'みなと保健センター',
      description: '成長の確認と育児相談',
      status: 'upcoming',
      createdBy: 'genie'
    },
    {
      id: '2', 
      title: '水族館デビュー',
      date: '2025-07-07',
      time: '10:00',
      type: 'outing',
      location: 'すみだ水族館',
      description: '暑い夏にぴったりの涼しいお出かけをGenieが提案',
      status: 'upcoming',
      createdBy: 'genie'
    },
    {
      id: '3',
      title: 'MRワクチン接種',
      date: '2025-07-15',
      time: '16:30',
      type: 'medical',
      subtype: 'vaccination',
      location: 'かわい小児科',
      description: '麻疹・風疹の予防接種',
      status: 'upcoming',
      createdBy: 'genie'
    },
    {
      id: '4',
      title: '夏祭りお出かけ',
      date: '2025-07-20',
      time: '18:00',
      type: 'outing',
      location: '地域夏祭り会場',
      description: '親子で楽しむ夏の思い出作り',
      status: 'upcoming',
      createdBy: 'user'
    },
    {
      id: '5',
      title: 'BCGワクチン接種',
      date: '2025-06-25',
      time: '11:00',
      type: 'medical',
      subtype: 'vaccination',
      location: 'みなと小児科クリニック',
      description: 'Genieが推奨時期に自動登録',
      status: 'completed',
      createdBy: 'genie'
    },
    {
      id: '6',
      title: 'プール開き準備',
      date: '2025-07-25',
      time: '09:30',
      type: 'outing',
      location: '市民プール',
      description: '夏の水遊びデビュー',
      status: 'upcoming',
      createdBy: 'user'
    },
    {
      id: '7',
      title: '4種混合ワクチン',
      date: '2025-06-30',
      time: '15:00',
      type: 'medical',
      subtype: 'vaccination',
      location: 'ファミリークリニック',
      description: 'ジフテリア・破傷風・百日咳・ポリオの予防接種',
      status: 'completed',
      createdBy: 'genie'
    },
    {
      id: '8',
      title: '七夕イベント',
      date: '2025-07-07',
      time: '15:30',
      type: 'outing',
      location: '地域センター',
      description: '短冊に願いを込めて',
      status: 'upcoming',
      createdBy: 'genie'
    },
    {
      id: '9',
      title: '入園式',
      date: '2025-04-08',
      time: '10:00',
      type: 'school',
      subtype: 'ceremony',
      location: 'みらい保育園',
      description: '新しい生活のスタート。制服着用',
      status: 'completed',
      createdBy: 'user'
    },
    {
      id: '10',
      title: '運動会',
      date: '2025-10-15',
      time: '09:00',
      type: 'school',
      subtype: 'event',
      location: '保育園園庭',
      description: 'かけっこやダンスの発表会',
      status: 'upcoming',
      createdBy: 'user'
    },
    {
      id: '11',
      title: 'お芋掘り遠足',
      date: '2025-10-22',
      time: '09:30',
      type: 'school',
      subtype: 'event',
      location: 'みどり農園',
      description: '秋の収穫体験。汚れても良い服装で',
      status: 'upcoming',
      createdBy: 'user'
    },
    {
      id: '12',
      title: 'クリスマス発表会',
      date: '2025-12-20',
      time: '14:00',
      type: 'school',
      subtype: 'event',
      location: '保育園ホール',
      description: '歌とダンスの発表。家族みんなで参加',
      status: 'upcoming',
      createdBy: 'user'
    },
    {
      id: '13',
      title: '親子参観日',
      date: '2025-09-10',
      time: '10:30',
      type: 'school',
      subtype: 'class',
      location: 'みらい保育園',
      description: '日頃の保育の様子を見学',
      status: 'upcoming',
      createdBy: 'user'
    }
  ]

  const handleEditEvent = (event: ScheduleEvent) => {
    // ScheduleEvent を ApiScheduleEvent に変換
    const apiEvent: ApiScheduleEvent = {
      id: event.id,
      user_id: 'frontend_user',
      title: event.title,
      date: event.date,
      time: event.time,
      type: event.type,
      location: event.location,
      description: event.description,
      status: event.status,
      created_by: event.createdBy,
      created_at: '',
      updated_at: ''
    }
    setSelectedEvent(apiEvent)
    setShowEditModal(true)
  }

  const handleEventUpdated = () => {
    loadScheduleEvents()
  }

  const handleEventDeleted = () => {
    loadScheduleEvents()
  }

  const getEventsByType = (type: string) => {
    if (type === 'all') return scheduleEvents
    return scheduleEvents.filter(event => event.type === type)
  }

  const getUpcomingCount = () => scheduleEvents.filter(e => e.status === 'upcoming').length
  const getCompletedCount = () => scheduleEvents.filter(e => e.status === 'completed').length
  const getGenieCreatedCount = () => scheduleEvents.filter(e => e.createdBy === 'genie').length

  const getTypeIcon = (type: string, subtype?: string) => {
    switch (type) {
      case 'medical': 
        return subtype === 'vaccination' ? <MdVaccines className="h-5 w-5" /> : <Stethoscope className="h-5 w-5" />
      case 'outing': return <MapPin className="h-5 w-5" />
      case 'school': return <Users className="h-5 w-5" />
      default: return <Calendar className="h-5 w-5" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'medical': return 'bg-red-500'
      case 'outing': return 'bg-green-500'
      case 'school': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', { 
      month: 'short', 
      day: 'numeric',
      weekday: 'short'
    })
  }

  // カレンダービュー用の日付管理
  const [currentDate, setCurrentDate] = useState(new Date(2025, 6, 1)) // 2025年7月
  
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startDate = new Date(firstDay)
    startDate.setDate(startDate.getDate() - firstDay.getDay()) // 日曜日から開始
    
    const days = []
    for (let i = 0; i < 42; i++) { // 6週間分
      const currentDay = new Date(startDate)
      currentDay.setDate(startDate.getDate() + i)
      days.push(currentDay)
    }
    return days
  }

  const getEventsForDate = (date: Date) => {
    const dateString = date.toISOString().split('T')[0]
    return getEventsByType(selectedTab).filter(event => event.date === dateString)
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1))
    setCurrentDate(newDate)
  }

  const isToday = (date: Date) => {
    const today = new Date()
    return date.toDateString() === today.toDateString()
  }

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentDate.getMonth()
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-slate-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-cyan-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
                  <FaCalendarAlt className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">予定を立てたこと</h1>
                  <p className="text-gray-600">Genieと一緒に計画した大切なスケジュール</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  予定を追加
                </Button>
                <Link href="/chat">
                  <Button variant="outline" className="border-cyan-300 text-cyan-700 hover:bg-cyan-50">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Genieに相談
                  </Button>
                </Link>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-cyan-200">
                  <GiMagicLamp className="h-4 w-4 text-cyan-600" />
                  <span className="text-sm text-cyan-700 font-medium">AI自動提案</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {/* スケジュールサマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-cyan-600 to-cyan-700 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-cyan-100 text-sm font-medium">今後の予定</p>
                    <p className="text-2xl font-bold mt-1">{getUpcomingCount()}件</p>
                    <p className="text-cyan-200 text-xs">今月予定あり</p>
                  </div>
                  <Calendar className="h-8 w-8 text-cyan-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-cyan-500 to-cyan-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-cyan-100 text-sm font-medium">完了済み</p>
                    <p className="text-2xl font-bold mt-1">{getCompletedCount()}件</p>
                    <p className="text-cyan-200 text-xs">実行完了</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-cyan-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">Genie提案</p>
                    <p className="text-2xl font-bold mt-1">{getGenieCreatedCount()}件</p>
                    <p className="text-blue-200 text-xs">AI自動作成</p>
                  </div>
                  <GiMagicLamp className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-slate-500 to-slate-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-100 text-sm font-medium">効率スコア</p>
                    <p className="text-2xl font-bold mt-1">9.2</p>
                    <p className="text-slate-200 text-xs">予定管理評価</p>
                  </div>
                  <Star className="h-8 w-8 text-slate-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 予定タブ切り替え */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Target className="h-6 w-6" />
                予定カテゴリ
              </CardTitle>
              <CardDescription className="text-cyan-100">
                カテゴリ別に整理されたあなたの大切な予定
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              {/* ビューモード切り替えとタブ */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Tabs value={selectedTab} onValueChange={setSelectedTab} className="flex-1">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="all" className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        すべて
                      </TabsTrigger>
                      <TabsTrigger value="medical" className="flex items-center gap-2">
                        <Stethoscope className="h-4 w-4" />
                        医療・健康
                      </TabsTrigger>
                      <TabsTrigger value="outing" className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        お出かけ
                      </TabsTrigger>
                      <TabsTrigger value="school" className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        学校行事
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant={viewMode === 'cards' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('cards')}
                      className="flex items-center gap-2"
                    >
                      <LayoutList className="h-4 w-4" />
                      カード
                    </Button>
                    <Button
                      variant={viewMode === 'calendar' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('calendar')}
                      className="flex items-center gap-2"
                    >
                      <Grid3X3 className="h-4 w-4" />
                      カレンダー
                    </Button>
                  </div>
                </div>

                {/* カードビュー */}
                {viewMode === 'cards' && (
                  <div className="space-y-4">
                    {/* ローディング表示 */}
                    {loading && (
                      <div className="text-center py-12">
                        <div className="inline-flex items-center gap-2">
                          <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                          <span className="text-gray-600">予定を読み込み中...</span>
                        </div>
                      </div>
                    )}

                    {/* 予定が見つからない場合 */}
                    {!loading && getEventsByType(selectedTab).length === 0 && (
                      <div className="text-center py-12">
                        <div className="mb-4">
                          <Calendar className="h-16 w-16 mx-auto text-gray-300" />
                        </div>
                        <h3 className="text-lg font-medium text-gray-700 mb-2">
                          {scheduleEvents.length === 0 ? '予定がありません' : '予定が見つかりません'}
                        </h3>
                        <p className="text-gray-500 mb-4">
                          {scheduleEvents.length === 0 
                            ? '最初の予定を作成しましょう' 
                            : 'フィルター条件を変更するか、新しい予定を作成してください'
                          }
                        </p>
                        <div className="flex gap-3 justify-center">
                          <Button 
                            onClick={() => setShowCreateModal(true)}
                            className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            予定を作成
                          </Button>
                          <Link href="/chat">
                            <Button variant="outline" className="border-cyan-300 text-cyan-700 hover:bg-cyan-50">
                              <Sparkles className="h-4 w-4 mr-2" />
                              Genieに相談
                            </Button>
                          </Link>
                        </div>
                      </div>
                    )}

                    {!loading && getEventsByType(selectedTab).map((event) => (
                      <Card key={event.id} className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50 hover:shadow-xl transition-all duration-300">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-4 flex-1">
                              <div className={`h-12 w-12 rounded-full ${getTypeColor(event.type)} flex items-center justify-center text-white shadow-lg`}>
                                {getTypeIcon(event.type, event.subtype)}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h4 className="font-bold text-lg text-gray-800">{event.title}</h4>
                                  {event.subtype && (
                                    <Badge variant="outline" className="text-xs">
                                      {event.subtype === 'vaccination' ? '予防接種' :
                                       event.subtype === 'checkup' ? '健診' :
                                       event.subtype === 'ceremony' ? '式典' :
                                       event.subtype === 'event' ? 'イベント' :
                                       event.subtype === 'class' ? '授業' : event.subtype}
                                    </Badge>
                                  )}
                                  {event.createdBy === 'genie' && (
                                    <Badge className="bg-gradient-to-r from-purple-500 to-violet-600 text-white">
                                      <GiMagicLamp className="h-3 w-3 mr-1" />
                                      Genie提案
                                    </Badge>
                                  )}
                                  <Badge 
                                    className={`${
                                      event.status === 'completed' 
                                        ? 'bg-green-500' 
                                        : event.status === 'upcoming'
                                        ? 'bg-blue-500'
                                        : 'bg-gray-500'
                                    } text-white`}
                                  >
                                    {event.status === 'completed' ? '完了' : 
                                     event.status === 'upcoming' ? '予定' : 'キャンセル'}
                                  </Badge>
                                </div>
                                
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-cyan-600" />
                                    <span>{formatDate(event.date)}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-cyan-600" />
                                    <span>{event.time}</span>
                                  </div>
                                  {event.location && (
                                    <div className="flex items-center gap-2">
                                      <FaMapMarkerAlt className="h-4 w-4 text-cyan-600" />
                                      <span>{event.location}</span>
                                    </div>
                                  )}
                                </div>
                                
                                {event.description && (
                                  <div className="mt-3 p-3 bg-emerald-50 rounded-lg border border-cyan-200">
                                    <p className="text-sm text-cyan-700">{event.description}</p>
                                  </div>
                                )}
                                
                                {/* 編集ボタン */}
                                <div className="mt-4 flex gap-2">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleEditEvent(event)}
                                    className="border-cyan-300 text-cyan-700 hover:bg-cyan-50"
                                  >
                                    <Edit className="h-4 w-4 mr-1" />
                                    編集
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                {/* カレンダービュー */}
                {viewMode === 'calendar' && (
                  <div className="space-y-4">
                    {/* カレンダーヘッダー */}
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-cyan-200">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigateMonth('prev')}
                        className="text-cyan-700 hover:bg-emerald-100"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      
                      <h3 className="text-lg font-semibold text-cyan-800">
                        {currentDate.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long' })}
                      </h3>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigateMonth('next')}
                        className="text-cyan-700 hover:bg-emerald-100"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>

                    {/* カレンダーグリッド */}
                    <div className="bg-white rounded-lg border border-cyan-200 overflow-hidden">
                      {/* 曜日ヘッダー */}
                      <div className="grid grid-cols-7 bg-emerald-100">
                        {['日', '月', '火', '水', '木', '金', '土'].map((day, index) => (
                          <div key={day} className={`p-3 text-center font-medium text-cyan-800 ${
                            index === 0 ? 'text-red-600' : index === 6 ? 'text-blue-600' : ''
                          }`}>
                            {day}
                          </div>
                        ))}
                      </div>

                      {/* カレンダー日付 */}
                      <div className="grid grid-cols-7">
                        {getDaysInMonth(currentDate).map((date, index) => {
                          const dayEvents = getEventsForDate(date)
                          const isCurrentMonthDay = isCurrentMonth(date)
                          const isTodayDate = isToday(date)
                          
                          return (
                            <div 
                              key={index} 
                              className={`min-h-[120px] p-2 border-r border-b border-cyan-100 ${
                                !isCurrentMonthDay ? 'bg-gray-50 text-gray-400' : 'bg-white'
                              } ${isTodayDate ? 'bg-emerald-50 ring-2 ring-emerald-300' : ''}`}
                            >
                              <div className={`text-sm font-medium mb-2 ${
                                isTodayDate ? 'text-cyan-700' : 
                                !isCurrentMonthDay ? 'text-gray-400' : 'text-gray-700'
                              }`}>
                                {date.getDate()}
                              </div>
                              
                              <div className="space-y-1">
                                {dayEvents.slice(0, 3).map((event) => (
                                  <div 
                                    key={event.id} 
                                    className={`text-xs p-1 rounded text-white truncate cursor-pointer hover:opacity-80 transition-opacity ${
                                      getTypeColor(event.type).split(' ')[0]
                                    }`}
                                    title={`${event.title} - ${event.time}`}
                                  >
                                    <div className="flex items-center gap-1">
                                      {getTypeIcon(event.type)}
                                      <span className="truncate">{event.title}</span>
                                    </div>
                                    <div className="text-xs opacity-90">{event.time}</div>
                                  </div>
                                ))}
                                {dayEvents.length > 3 && (
                                  <div className="text-xs text-gray-500 text-center py-1">
                                    +{dayEvents.length - 3}件
                                  </div>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>

                    {/* カレンダー凡例 */}
                    <div className="flex items-center justify-center gap-6 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg border border-cyan-200">
                      <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-red-500"></div>
                        <span className="text-xs text-gray-600">予防接種</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-green-500"></div>
                        <span className="text-xs text-gray-600">お出かけ</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded bg-blue-500"></div>
                        <span className="text-xs text-gray-600">健診</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <GiMagicLamp className="h-3 w-3 text-purple-600" />
                        <span className="text-xs text-gray-600">Genie提案</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>


          {/* AIチャット連携カード */}
          <Card className="shadow-xl border-0 bg-gradient-to-br from-emerald-50 to-teal-50">
            <CardHeader className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとの予定作成連携
              </CardTitle>
              <CardDescription className="text-cyan-100">
                Genieがあなたのライフスタイルに合わせて最適な予定を提案・作成します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="bg-white/60 p-4 rounded-lg border border-cyan-200">
                <div className="flex items-start gap-3 mb-4">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
                    <GiMagicLamp className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-cyan-800 font-medium mb-2">
                      💡 Genieができること：
                    </p>
                    <ul className="text-sm text-cyan-700 space-y-1">
                      <li>• 子どもの年齢に応じた予防接種スケジュールを自動提案</li>
                      <li>• 発達に良いお出かけ先を季節や天気を考慮して推奨</li>
                      <li>• 健診や検診の適切なタイミングをリマインド</li>
                      <li>• 家族の予定を考慮した最適な時間帯を提案</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg">
                      <Sparkles className="h-4 w-4 mr-2" />
                      Genieに予定を相談
                    </Button>
                  </Link>
                  <Button 
                    variant="outline"
                    className="border-cyan-300 text-cyan-700 hover:bg-emerald-50"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    手動で追加
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 自動提案の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full border border-cyan-200">
              <GiMagicLamp className="h-4 w-4 text-cyan-600" />
              <span className="text-sm text-cyan-700 font-medium">Genieが24時間自動で最適な予定を提案します</span>
            </div>
          </div>
        </div>
      </div>

      {/* 予定作成モーダル */}
      <CreateScheduleModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        onEventCreated={loadScheduleEvents}
      />

      {/* 予定編集モーダル */}
      <EditScheduleModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        event={selectedEvent}
        onEventUpdated={handleEventUpdated}
        onEventDeleted={handleEventDeleted}
      />
    </AppLayout>
  )
}