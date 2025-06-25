'use client'

import React, { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { CreateMemoryModal } from '@/components/features/memories/create-memory-modal'
import { EditMemoryModal } from '@/components/features/memories/edit-memory-modal'
import { getMemories, toggleMemoryFavorite, MemoryRecord as ApiMemoryRecord } from '@/lib/api/memories'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Camera,
  Plus,
  Heart,
  Smile,
  Star,
  Image,
  Search,
  Video,
  Upload,
  X,
  Calendar,
  Clock,
  Play,
  Download,
  Share,
  Eye,
  Sparkles,
  Filter,
  Grid3X3,
  List,
  Archive,
  Edit,
  Trash2
} from 'lucide-react'
import { MdPhotoLibrary, MdVideoLibrary, MdFamilyRestroom } from 'react-icons/md'
import { FaCamera, FaVideo, FaHeart } from 'react-icons/fa'
import { GiMagicLamp } from 'react-icons/gi'
import Link from 'next/link'
import { getImageUrl } from '@/lib/api/file-upload'

// バックエンドAPIから取得したデータを表示用に変換するインターフェース
interface MemoryRecord extends Omit<ApiMemoryRecord, 'user_id' | 'created_at' | 'updated_at'> {
  mediaUrl?: string
  thumbnailUrl?: string
  duration?: string
  fileSize?: string
  genieAnalysis?: {
    detected: string[]
    emotions: string[]
    confidence: number
    description: string
  }
}

// EditMemoryModalが期待する形式
interface EditableMemoryRecord {
  id: string
  title: string
  description: string
  date: string
  type: 'photo' | 'video' | 'album'
  category: 'milestone' | 'daily' | 'family' | 'special'
  mediaUrl?: string
  thumbnailUrl?: string
  location?: string
  tags: string[]
  favorited: boolean
}

export default function CapturedMemoriesPage() {
  const [memories, setMemories] = useState<MemoryRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedMemory, setSelectedMemory] = useState<EditableMemoryRecord | null>(null)

  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)

  // APIからメモリーデータを取得
  const loadMemories = async () => {
    try {
      setLoading(true)
      const result = await getMemories({ user_id: 'frontend_user' })
      
      if (result.success && result.data) {
        // APIデータを表示用に変換
        const convertedMemories: MemoryRecord[] = result.data.map(apiMemory => ({
          id: apiMemory.id,
          title: apiMemory.title,
          description: apiMemory.description,
          date: apiMemory.date,
          type: apiMemory.type,
          category: apiMemory.category,
          mediaUrl: apiMemory.media_url,
          thumbnailUrl: apiMemory.thumbnail_url,
          location: apiMemory.location,
          tags: apiMemory.tags,
          favorited: apiMemory.favorited,
          // 仮のGenieAnalysisデータ（後で実装）
          genieAnalysis: undefined
        }))
        setMemories(convertedMemories)
      } else {
        console.error('メモリーの取得に失敗しました:', result.message)
      }
    } catch (error) {
      console.error('メモリー読み込みエラー:', error)
    } finally {
      setLoading(false)
    }
  }

  // 初回ロード
  useEffect(() => {
    loadMemories()
  }, [])

  const categoryLabels = {
    milestone: 'マイルストーン',
    daily: '日常',
    family: '家族',
    special: '特別'
  }

  const typeLabels = {
    photo: '写真',
    video: '動画',
    album: 'アルバム'
  }

  const typeIcons = {
    photo: Camera,
    video: Video,
    album: Archive
  }

  const getCategoryColor = (category: MemoryRecord['category']) => {
    switch (category) {
      case 'milestone': return 'from-purple-500 to-purple-600'
      case 'daily': return 'from-blue-500 to-blue-600'
      case 'family': return 'from-green-500 to-green-600'
      case 'special': return 'from-pink-500 to-pink-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  const getTypeColor = (type: MemoryRecord['type']) => {
    switch (type) {
      case 'photo': return 'bg-cyan-500'
      case 'video': return 'bg-indigo-500'
      case 'album': return 'bg-emerald-500'
      default: return 'bg-gray-500'
    }
  }

  const toggleFavorite = async (id: string) => {
    const memory = memories.find(m => m.id === id)
    if (!memory) return

    try {
      const result = await toggleMemoryFavorite(id, !memory.favorited)
      
      if (result.success) {
        setMemories(prev => prev.map(memory => 
          memory.id === id ? { ...memory, favorited: !memory.favorited } : memory
        ))
      } else {
        console.error('お気に入り切り替えに失敗しました:', result.message)
        alert('お気に入りの切り替えに失敗しました')
      }
    } catch (error) {
      console.error('お気に入り切り替えエラー:', error)
      alert('お気に入りの切り替え中にエラーが発生しました')
    }
  }

  const handleEditMemory = (memory: MemoryRecord) => {
    // Convert page MemoryRecord to EditableMemoryRecord format for the EditMemoryModal
    const editableMemoryRecord: EditableMemoryRecord = {
      id: memory.id,
      title: memory.title,
      description: memory.description,
      date: memory.date,
      type: memory.type,
      category: memory.category,
      mediaUrl: memory.mediaUrl,
      thumbnailUrl: memory.thumbnailUrl,
      location: memory.location || '',
      tags: memory.tags,
      favorited: memory.favorited
    }
    setSelectedMemory(editableMemoryRecord)
    setShowEditModal(true)
  }

  const handleMemoryUpdated = () => {
    loadMemories()
  }

  const handleMemoryDeleted = () => {
    loadMemories()
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getFilteredMemories = () => {
    let filtered = memories
    
    // 検索フィルター
    if (searchQuery) {
      filtered = filtered.filter(m => 
        m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }
    
    // カテゴリフィルター
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(m => m.category === selectedCategory)
    }
    
    // タイプフィルター
    if (selectedType !== 'all') {
      filtered = filtered.filter(m => m.type === selectedType)
    }
    
    // お気に入りフィルター
    if (showFavoritesOnly) {
      filtered = filtered.filter(m => m.favorited)
    }
    
    return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  const getStatsData = () => {
    return {
      totalMemories: memories.length,
      photosCount: memories.filter(m => m.type === 'photo').length,
      videosCount: memories.filter(m => m.type === 'video').length,
      favoritesCount: memories.filter(m => m.favorited).length,
      genieAnalyzed: memories.filter(m => m.genieAnalysis).length
    }
  }

  const statsData = getStatsData()

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-cyan-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
                  <MdPhotoLibrary className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">撮影したメモリー</h1>
                  <p className="text-gray-600">Genieが管理する大切な思い出のコレクション</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  メモリーを追加
                </Button>
                <Link href="/chat">
                  <Button variant="outline" className="border-cyan-300 text-cyan-700 hover:bg-cyan-50">
                    <Camera className="h-4 w-4 mr-2" />
                    Genieで撮影
                  </Button>
                </Link>
                <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-lg border border-cyan-200">
                  <GiMagicLamp className="h-4 w-4 text-cyan-600" />
                  <span className="text-sm text-cyan-700 font-medium">AI自動整理</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {/* メモリーサマリーカード */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-cyan-500 to-cyan-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-cyan-100 text-sm font-medium">総メモリー</p>
                    <p className="text-2xl font-bold mt-1">{statsData.totalMemories}件</p>
                    <p className="text-cyan-200 text-xs">保存済み</p>
                  </div>
                  <Archive className="h-8 w-8 text-cyan-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">写真</p>
                    <p className="text-2xl font-bold mt-1">{statsData.photosCount}枚</p>
                    <p className="text-blue-200 text-xs">撮影済み</p>
                  </div>
                  <Camera className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-indigo-500 to-indigo-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-indigo-100 text-sm font-medium">動画</p>
                    <p className="text-2xl font-bold mt-1">{statsData.videosCount}本</p>
                    <p className="text-indigo-200 text-xs">録画済み</p>
                  </div>
                  <Video className="h-8 w-8 text-indigo-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">お気に入り</p>
                    <p className="text-2xl font-bold mt-1">{statsData.favoritesCount}件</p>
                    <p className="text-purple-200 text-xs">特別保存</p>
                  </div>
                  <Heart className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-emerald-100 text-sm font-medium">AI解析</p>
                    <p className="text-2xl font-bold mt-1">{statsData.genieAnalyzed}件</p>
                    <p className="text-emerald-200 text-xs">分析完了</p>
                  </div>
                  <Sparkles className="h-8 w-8 text-emerald-200" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* フィルターとビューモード */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Filter className="h-6 w-6" />
                メモリーフィルター
              </CardTitle>
              <CardDescription className="text-cyan-100">
                お探しのメモリーを見つけやすくする検索・フィルター機能
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="space-y-4">
                {/* 検索バー */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="タイトル、説明、タグで検索..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 border-cyan-200 focus:border-cyan-400"
                  />
                </div>
                
                {/* フィルター設定 */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">カテゴリ</label>
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">すべて</SelectItem>
                        {Object.entries(categoryLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">メディアタイプ</label>
                    <Select value={selectedType} onValueChange={setSelectedType}>
                      <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">すべて</SelectItem>
                        {Object.entries(typeLabels).map(([key, label]) => (
                          <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-end">
                    <Button
                      variant={showFavoritesOnly ? 'default' : 'outline'}
                      onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
                      className="flex items-center gap-2"
                    >
                      <Heart className={`h-4 w-4 ${showFavoritesOnly ? 'fill-current' : ''}`} />
                      お気に入りのみ
                    </Button>
                  </div>
                  
                  <div className="flex items-end gap-2">
                    <Button
                      variant={viewMode === 'grid' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('grid')}
                    >
                      <Grid3X3 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewMode('list')}
                    >
                      <List className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* メモリーギャラリー */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <MdPhotoLibrary className="h-6 w-6" />
                メモリーギャラリー
              </CardTitle>
              <CardDescription className="text-blue-100">
                {getFilteredMemories().length}件のメモリーが見つかりました
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              {/* グリッドビュー */}
              {viewMode === 'grid' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {getFilteredMemories().map((memory) => {
                    const IconComponent = typeIcons[memory.type]
                    return (
                      <Card key={memory.id} className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50 hover:shadow-xl transition-all duration-300">
                        <CardContent className="p-0">
                          {/* メディアプレビュー */}
                          <div className="relative aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-t-lg overflow-hidden">
                            {memory.mediaUrl ? (
                              <img 
                                src={memory.mediaUrl.startsWith('/api/') ? `http://localhost:8000${memory.mediaUrl}` : memory.mediaUrl}
                                alt={memory.title}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                                <IconComponent className="h-12 w-12 text-gray-400" />
                              </div>
                            )}
                            
                            {/* タイプバッジ */}
                            <div className={`absolute top-3 left-3 ${getTypeColor(memory.type)} text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1`}>
                              <IconComponent className="h-3 w-3" />
                              {typeLabels[memory.type]}
                            </div>
                            
                            {/* お気に入りボタン */}
                            <button
                              onClick={() => toggleFavorite(memory.id)}
                              className="absolute top-3 right-3 p-2 bg-white/80 rounded-full hover:bg-white transition-colors"
                            >
                              <Heart className={`h-4 w-4 ${memory.favorited ? 'text-red-500 fill-current' : 'text-gray-400'}`} />
                            </button>
                            
                            {/* 動画時間 */}
                            {memory.duration && (
                              <div className="absolute bottom-3 right-3 bg-black/60 text-white px-2 py-1 rounded text-xs flex items-center gap-1">
                                <Play className="h-3 w-3" />
                                {memory.duration}
                              </div>
                            )}
                          </div>
                          
                          {/* メモリー情報 */}
                          <div className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-bold text-lg text-gray-800 line-clamp-1">{memory.title}</h4>
                              <Badge className={`bg-gradient-to-r ${getCategoryColor(memory.category)} text-white ml-2`}>
                                {categoryLabels[memory.category]}
                              </Badge>
                            </div>
                            
                            <p className="text-sm text-gray-600 mb-3 line-clamp-2">{memory.description}</p>
                            
                            <div className="space-y-2">
                              <div className="flex items-center gap-2 text-xs text-gray-500">
                                <Calendar className="h-3 w-3" />
                                <span>{formatDate(memory.date)}</span>
                                {memory.location && (
                                  <>
                                    <span>•</span>
                                    <span>{memory.location}</span>
                                  </>
                                )}
                              </div>
                              
                              {/* タグ */}
                              {memory.tags.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {memory.tags.slice(0, 3).map((tag, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {tag}
                                    </Badge>
                                  ))}
                                  {memory.tags.length > 3 && (
                                    <Badge variant="outline" className="text-xs">
                                      +{memory.tags.length - 3}
                                    </Badge>
                                  )}
                                </div>
                              )}
                              
                              {/* Genie解析結果 */}
                              {memory.genieAnalysis && (
                                <div className="mt-3 p-2 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200">
                                  <div className="flex items-center gap-2 mb-1">
                                    <GiMagicLamp className="h-3 w-3 text-purple-600" />
                                    <span className="text-xs font-medium text-purple-700">Genie解析</span>
                                    <Badge variant="outline" className="text-xs">
                                      {Math.round(memory.genieAnalysis.confidence * 100)}%
                                    </Badge>
                                  </div>
                                  <p className="text-xs text-purple-600">{memory.genieAnalysis.description}</p>
                                </div>
                              )}
                            </div>
                            
                            {/* アクションボタン */}
                            <div className="flex gap-2 mt-4">
                              <Button size="sm" variant="outline" className="flex-1">
                                <Eye className="h-3 w-3 mr-1" />
                                表示
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleEditMemory(memory)}
                                className="border-cyan-300 text-cyan-700 hover:bg-cyan-50"
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button size="sm" variant="outline">
                                <Share className="h-3 w-3" />
                              </Button>
                              <Button size="sm" variant="outline">
                                <Download className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
              
              {/* リストビュー */}
              {viewMode === 'list' && (
                <div className="space-y-4">
                  {getFilteredMemories().map((memory) => {
                    const IconComponent = typeIcons[memory.type]
                    return (
                      <Card key={memory.id} className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50">
                        <CardContent className="p-6">
                          <div className="flex items-start gap-4">
                            {/* サムネイル */}
                            <div className="flex-shrink-0">
                              <div className={`w-24 h-24 ${getTypeColor(memory.type)} rounded-lg flex items-center justify-center`}>
                                <IconComponent className="h-8 w-8 text-white" />
                              </div>
                            </div>
                            
                            {/* メモリー情報 */}
                            <div className="flex-1">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex items-center gap-3">
                                  <h4 className="font-bold text-lg text-gray-800">{memory.title}</h4>
                                  <Badge className={`bg-gradient-to-r ${getCategoryColor(memory.category)} text-white`}>
                                    {categoryLabels[memory.category]}
                                  </Badge>
                                  {memory.genieAnalysis && (
                                    <Badge variant="outline" className="text-xs">
                                      <GiMagicLamp className="h-3 w-3 mr-1" />
                                      AI解析済み
                                    </Badge>
                                  )}
                                </div>
                                <button
                                  onClick={() => toggleFavorite(memory.id)}
                                  className="p-1"
                                >
                                  <Heart className={`h-5 w-5 ${memory.favorited ? 'text-red-500 fill-current' : 'text-gray-400'}`} />
                                </button>
                              </div>
                              
                              <p className="text-gray-600 mb-3">{memory.description}</p>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-500 mb-3">
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4 text-cyan-600" />
                                  <span>{formatDate(memory.date)}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <IconComponent className="h-4 w-4 text-cyan-600" />
                                  <span>{typeLabels[memory.type]}</span>
                                </div>
                                {memory.location && (
                                  <div className="flex items-center gap-2">
                                    <span>📍</span>
                                    <span>{memory.location}</span>
                                  </div>
                                )}
                              </div>
                              
                              {/* タグ */}
                              {memory.tags.length > 0 && (
                                <div className="flex flex-wrap gap-2 mb-3">
                                  {memory.tags.map((tag, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {tag}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                              
                              {/* Genie解析結果 */}
                              {memory.genieAnalysis && (
                                <div className="p-3 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border border-purple-200 mb-3">
                                  <div className="flex items-center gap-2 mb-2">
                                    <GiMagicLamp className="h-4 w-4 text-purple-600" />
                                    <span className="text-sm font-medium text-purple-700">Genie AI解析結果</span>
                                    <Badge variant="outline" className="text-xs">
                                      信頼度 {Math.round(memory.genieAnalysis.confidence * 100)}%
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-purple-600 mb-2">{memory.genieAnalysis.description}</p>
                                  {memory.genieAnalysis.emotions.length > 0 && (
                                    <div className="flex flex-wrap gap-1">
                                      {memory.genieAnalysis.emotions.map((emotion, index) => (
                                        <Badge key={index} variant="outline" className="text-xs">
                                          {emotion}
                                        </Badge>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* アクションボタン */}
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline">
                                  <Eye className="h-4 w-4 mr-2" />
                                  詳細表示
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline"
                                  onClick={() => handleEditMemory(memory)}
                                  className="border-cyan-300 text-cyan-700 hover:bg-cyan-50"
                                >
                                  <Edit className="h-4 w-4 mr-2" />
                                  編集
                                </Button>
                                <Button size="sm" variant="outline">
                                  <Share className="h-4 w-4 mr-2" />
                                  共有
                                </Button>
                                <Button size="sm" variant="outline">
                                  <Download className="h-4 w-4 mr-2" />
                                  ダウンロード
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
              
              {/* ローディング表示 */}
              {loading && (
                <div className="text-center py-12">
                  <div className="inline-flex items-center gap-2">
                    <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-600">メモリーを読み込み中...</span>
                  </div>
                </div>
              )}

              {/* 結果が見つからない場合 */}
              {!loading && getFilteredMemories().length === 0 && (
                <div className="text-center py-12">
                  <div className="mb-4">
                    <Camera className="h-16 w-16 mx-auto text-gray-300" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">
                    {memories.length === 0 ? 'メモリーがありません' : 'メモリーが見つかりません'}
                  </h3>
                  <p className="text-gray-500 mb-4">
                    {memories.length === 0 
                      ? '最初のメモリーを作成しましょう' 
                      : '検索条件を変更するか、新しいメモリーを作成してください'
                    }
                  </p>
                  <div className="flex gap-3 justify-center">
                    <Button 
                      onClick={() => setShowCreateModal(true)}
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      メモリーを作成
                    </Button>
                    <Link href="/chat">
                      <Button variant="outline" className="border-cyan-300 text-cyan-700 hover:bg-cyan-50">
                        <Camera className="h-4 w-4 mr-2" />
                        Genieで撮影
                      </Button>
                    </Link>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AIチャット連携カード */}
          <Card className="shadow-xl border-0 bg-gradient-to-br from-cyan-50 to-blue-50">
            <CardHeader className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                Genieとのメモリー作成連携
              </CardTitle>
              <CardDescription className="text-cyan-100">
                写真や動画を送るだけで、Genieが自動で整理・分析してメモリーに保存します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="bg-white/60 p-4 rounded-lg border border-cyan-200">
                <div className="flex items-start gap-3 mb-4">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
                    <GiMagicLamp className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-cyan-800 font-medium mb-2">
                      📸 Genieができること：
                    </p>
                    <ul className="text-sm text-cyan-700 space-y-1">
                      <li>• 写真から表情や行動を自動解析してタグ付け</li>
                      <li>• 撮影日時や場所情報を自動で記録</li>
                      <li>• 似た写真を自動でグループ化してアルバム作成</li>
                      <li>• 成長の瞬間やマイルストーンを自動検出</li>
                      <li>• 感情分析で思い出の価値を数値化</li>
                    </ul>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Link href="/chat" className="flex-1">
                    <Button className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg">
                      <Camera className="h-4 w-4 mr-2" />
                      Genieに写真を送る
                    </Button>
                  </Link>
                  <Button 
                    variant="outline"
                    className="border-cyan-300 text-cyan-700 hover:bg-cyan-50"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    直接アップロード
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 自動整理の説明 */}
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full border border-cyan-200">
              <GiMagicLamp className="h-4 w-4 text-cyan-600" />
              <span className="text-sm text-cyan-700 font-medium">Genieが24時間、大切な瞬間を自動で整理・保存します</span>
            </div>
          </div>
        </div>
      </div>

      {/* メモリー作成モーダル */}
      <CreateMemoryModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        onMemoryCreated={loadMemories}
      />

      {/* メモリー編集モーダル */}
      <EditMemoryModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        memory={selectedMemory}
        onMemoryUpdated={handleMemoryUpdated}
        onMemoryDeleted={handleMemoryDeleted}
      />
    </AppLayout>
  )
}