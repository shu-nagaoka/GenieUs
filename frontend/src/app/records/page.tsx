'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
// import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { 
  BookOpen,
  Plus,
  Heart,
  Smile,
  Star,
  Trash2,
  Image,
  Search,
  Video,
  Upload,
  X
} from 'lucide-react'

interface Record {
  id: string
  title: string
  content: string
  date: Date
  category: 'milestone' | 'daily' | 'memory' | 'growth'
  photos?: string[]
  videos?: string[]
  mood?: 'happy' | 'sad' | 'excited' | 'calm' | 'funny'
}

export default function RecordsPage() {
  const [records, setRecords] = useState<Record[]>([
    {
      id: '1',
      title: '初めて笑った！',
      content: '今日、初めてニコっと笑ってくれました。本当に可愛くて感動しました。',
      date: new Date('2024-06-20'),
      category: 'milestone',
      mood: 'happy'
    },
    {
      id: '2',
      title: '公園でお散歩',
      content: 'お天気が良かったので近所の公園へ。桜がきれいで、ベビーカーでゆっくりお散歩しました。',
      date: new Date('2024-06-19'),
      category: 'daily',
      mood: 'calm'
    },
    {
      id: '3',
      title: 'おじいちゃんおばあちゃんとの初対面',
      content: '両親に初めて会わせました。みんなメロメロで、たくさん写真を撮りました。',
      date: new Date('2024-06-18'),
      category: 'memory',
      mood: 'excited'
    }
  ])

  const [isAddingRecord, setIsAddingRecord] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [newRecord, setNewRecord] = useState({
    title: '',
    content: '',
    category: 'daily' as Record['category'],
    mood: 'happy' as Record['mood']
  })

  const categoryLabels = {
    milestone: 'マイルストーン',
    daily: '日常',
    memory: '思い出',
    growth: '成長'
  }

  const moodIcons = {
    happy: { icon: Smile, color: 'text-yellow-500' },
    excited: { icon: Star, color: 'text-orange-500' },
    calm: { icon: Heart, color: 'text-blue-500' },
    sad: { icon: Heart, color: 'text-gray-500' },
    funny: { icon: Smile, color: 'text-green-500' }
  }

  const getCategoryColor = (category: Record['category']) => {
    switch (category) {
      case 'milestone': return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'daily': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'memory': return 'bg-pink-100 text-pink-800 border-pink-200'
      case 'growth': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const handleAddRecord = () => {
    if (newRecord.title && newRecord.content) {
      const record: Record = {
        id: Date.now().toString(),
        title: newRecord.title,
        content: newRecord.content,
        category: newRecord.category,
        mood: newRecord.mood,
        date: new Date()
      }
      setRecords(prev => [record, ...prev])
      setNewRecord({ title: '', content: '', category: 'daily', mood: 'happy' })
      setIsAddingRecord(false)
    }
  }

  const deleteRecord = (id: string) => {
    setRecords(prev => prev.filter(r => r.id !== id))
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const filteredRecords = (category?: Record['category']) => {
    let filtered = records
    
    // 検索フィルター
    if (searchQuery) {
      filtered = filtered.filter(r => 
        r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    
    // カテゴリフィルター
    if (category) {
      filtered = filtered.filter(r => r.category === category)
    }
    
    return filtered
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      setSelectedFiles(prev => [...prev, ...files])
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const getHighlightStats = () => {
    const total = records.length
    const thisWeek = records.filter(r => {
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      return r.date >= weekAgo
    }).length
    const milestones = records.filter(r => r.category === 'milestone').length
    return { total, thisWeek, milestones }
  }

  return (
    <AppLayout>
      {/* ページヘッダー */}
      <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
        <div className="px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center">
                <BookOpen className="h-4 w-4 text-white" />
              </div>
              <h1 className="text-2xl font-heading font-semibold text-gray-800">子育て記録</h1>
            </div>
            <Button onClick={() => setIsAddingRecord(true)} className="bg-indigo-500 hover:bg-indigo-600">
              <Plus className="h-4 w-4 mr-2" />
              記録を追加
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        {/* ハイライト統計 */}
        <div className="mb-8">
          <h2 className="text-2xl font-heading font-semibold text-gray-800 mb-4">記録の概要</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100">
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{getHighlightStats().total}</div>
                <p className="text-sm text-blue-700">総記録数</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-r from-green-50 to-green-100">
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{getHighlightStats().thisWeek}</div>
                <p className="text-sm text-green-700">今週の記録</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-r from-purple-50 to-purple-100">
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">{getHighlightStats().milestones}</div>
                <p className="text-sm text-purple-700">マイルストーン</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 検索バー */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="記録を検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* 新しい記録の追加フォーム */}
        {isAddingRecord && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>新しい記録</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Input
                  placeholder="タイトル"
                  value={newRecord.title}
                  onChange={(e) => setNewRecord(prev => ({ ...prev, title: e.target.value }))}
                />
              </div>
              <div>
                <textarea
                  placeholder="記録の内容を書いてください..."
                  value={newRecord.content}
                  onChange={(e) => setNewRecord(prev => ({ ...prev, content: e.target.value }))}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">カテゴリ</label>
                  <select
                    value={newRecord.category}
                    onChange={(e) => setNewRecord(prev => ({ ...prev, category: e.target.value as Record['category'] }))}
                    className="px-3 py-2 border border-gray-300 rounded-md"
                  >
                    {Object.entries(categoryLabels).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">気分</label>
                  <select
                    value={newRecord.mood}
                    onChange={(e) => setNewRecord(prev => ({ ...prev, mood: e.target.value as Record['mood'] }))}
                    className="px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="happy">嬉しい</option>
                    <option value="excited">ワクワク</option>
                    <option value="calm">穏やか</option>
                    <option value="funny">面白い</option>
                    <option value="sad">寂しい</option>
                  </select>
                </div>
              </div>
              
              {/* ファイルアップロード */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">写真・動画</label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <input
                    type="file"
                    multiple
                    accept="image/*,video/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm text-gray-600">写真や動画をアップロード</p>
                    <p className="text-xs text-gray-500 mt-1">クリックしてファイルを選択</p>
                  </label>
                </div>
                
                {/* 選択されたファイル一覧 */}
                {selectedFiles.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                        {file.type.startsWith('image/') ? (
                          <Image className="h-4 w-4 text-blue-500" />
                        ) : (
                          <Video className="h-4 w-4 text-green-500" />
                        )}
                        <span className="text-sm flex-1">{file.name}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                          className="h-6 w-6 p-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddRecord} className="bg-indigo-500 hover:bg-indigo-600">
                  保存
                </Button>
                <Button variant="outline" onClick={() => setIsAddingRecord(false)}>
                  キャンセル
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* タブ */}
        <Tabs defaultValue="all" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">すべて</TabsTrigger>
            <TabsTrigger value="milestone">マイルストーン</TabsTrigger>
            <TabsTrigger value="daily">日常</TabsTrigger>
            <TabsTrigger value="memory">思い出</TabsTrigger>
            <TabsTrigger value="growth">成長</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4">
            {records.map((record) => (
              <Card key={record.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-medium text-gray-800">{record.title}</h3>
                      <Badge className={getCategoryColor(record.category)}>
                        {categoryLabels[record.category]}
                      </Badge>
                      {record.mood && (
                        <div className={`${moodIcons[record.mood].color}`}>
                          {React.createElement(moodIcons[record.mood].icon, { className: 'h-4 w-4' })}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">{formatDate(record.date)}</span>
                      <Button variant="ghost" size="sm" onClick={() => deleteRecord(record.id)}>
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                  <p className="text-gray-600 leading-relaxed">{record.content}</p>
                  {record.photos && record.photos.length > 0 && (
                    <div className="mt-4 flex gap-2">
                      {record.photos.map((photo, index) => (
                        <div key={index} className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center">
                          <Image className="h-8 w-8 text-gray-400" />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {(['milestone', 'daily', 'memory', 'growth'] as Record['category'][]).map((category) => (
            <TabsContent key={category} value={category} className="space-y-4">
              {filteredRecords(category).map((record) => (
                <Card key={record.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-medium text-gray-800">{record.title}</h3>
                        {record.mood && (
                          <div className={`${moodIcons[record.mood].color}`}>
                            {React.createElement(moodIcons[record.mood].icon, { className: 'h-4 w-4' })}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">{formatDate(record.date)}</span>
                        <Button variant="ghost" size="sm" onClick={() => deleteRecord(record.id)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-gray-600 leading-relaxed">{record.content}</p>
                  </CardContent>
                </Card>
              ))}
              {filteredRecords(category).length === 0 && (
                <Card>
                  <CardContent className="p-8 text-center">
                    <BookOpen className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-600">まだ{categoryLabels[category]}の記録がありません</p>
                    <p className="text-sm text-gray-500 mt-2">新しい記録を追加してみましょう</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </AppLayout>
  )
}