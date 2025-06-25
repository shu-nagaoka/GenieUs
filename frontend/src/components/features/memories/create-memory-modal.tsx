'use client'

import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { 
  Camera, 
  Video, 
  Archive,
  Heart,
  Calendar,
  MapPin,
  Tag,
  X,
  Plus,
  Save,
  Loader2,
  Upload
} from 'lucide-react'
import { createMemory, MemoryRecordCreateRequest } from '@/libs/api/memories'
import { ImageUpload } from './image-upload'

interface CreateMemoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onMemoryCreated: () => void
}

export function CreateMemoryModal({ open, onOpenChange, onMemoryCreated }: CreateMemoryModalProps) {
  const [formData, setFormData] = useState<MemoryRecordCreateRequest>({
    title: '',
    description: '',
    date: new Date().toISOString().split('T')[0], // 今日の日付をデフォルト
    type: 'photo',
    category: 'daily',
    location: '',
    tags: [],
    favorited: false
  })
  
  const [newTag, setNewTag] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)

  const typeOptions = [
    { value: 'photo', label: '写真', icon: Camera },
    { value: 'video', label: '動画', icon: Video },
    { value: 'album', label: 'アルバム', icon: Archive }
  ]

  const categoryOptions = [
    { value: 'milestone', label: 'マイルストーン', color: 'from-purple-500 to-purple-600' },
    { value: 'daily', label: '日常', color: 'from-blue-500 to-blue-600' },
    { value: 'family', label: '家族', color: 'from-green-500 to-green-600' },
    { value: 'special', label: '特別', color: 'from-pink-500 to-pink-600' }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title.trim()) {
      alert('タイトルを入力してください')
      return
    }
    
    if (!formData.description.trim()) {
      alert('説明を入力してください')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      // アップロードされた画像URLをformDataに追加
      const memoryData = {
        ...formData,
        media_url: uploadedImageUrl,
        thumbnail_url: uploadedImageUrl // サムネイルも同じ画像を使用
      }
      
      const result = await createMemory(memoryData)
      
      if (result.success) {
        // フォームをリセット
        setFormData({
          title: '',
          description: '',
          date: new Date().toISOString().split('T')[0],
          type: 'photo',
          category: 'daily',
          location: '',
          tags: [],
          favorited: false
        })
        setNewTag('')
        setUploadedImageUrl(null)
        
        // モーダルを閉じて親コンポーネントに通知
        onOpenChange(false)
        onMemoryCreated()
        
        alert('メモリーが作成されました！')
      } else {
        alert(result.message || 'メモリーの作成に失敗しました')
      }
    } catch (error) {
      console.error('メモリー作成エラー:', error)
      alert('メモリーの作成中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }))
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleInputChange = (field: keyof MemoryRecordCreateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleImageUploaded = (fileUrl: string) => {
    setUploadedImageUrl(fileUrl)
  }

  const handleImageRemove = () => {
    setUploadedImageUrl(null)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <Camera className="h-6 w-6 text-cyan-600" />
            新しいメモリーを作成
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            大切な瞬間を記録して、家族の思い出として保存しましょう
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          {/* タイトル */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium text-gray-700">
              タイトル *
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="例: 初めての笑顔、つかまり立ち成功"
              className="border-cyan-200 focus:border-cyan-400"
              required
            />
          </div>

          {/* 説明 */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium text-gray-700">
              説明 *
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="この瞬間について詳しく説明してください..."
              rows={3}
              className="border-cyan-200 focus:border-cyan-400"
              required
            />
          </div>

          {/* 日付とお気に入り */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                日付
              </Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => handleInputChange('date', e.target.value)}
                className="border-cyan-200 focus:border-cyan-400"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">お気に入り</Label>
              <div className="flex items-center gap-2 pt-2">
                <Button
                  type="button"
                  variant={formData.favorited ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleInputChange('favorited', !formData.favorited)}
                  className={`flex items-center gap-2 ${
                    formData.favorited 
                      ? 'bg-red-500 hover:bg-red-600 text-white' 
                      : 'border-red-300 text-red-600 hover:bg-red-50'
                  }`}
                >
                  <Heart className={`h-4 w-4 ${formData.favorited ? 'fill-current' : ''}`} />
                  {formData.favorited ? 'お気に入り' : '通常'}
                </Button>
              </div>
            </div>
          </div>

          {/* タイプとカテゴリ */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">メディアタイプ</Label>
              <Select value={formData.type} onValueChange={(value: any) => handleInputChange('type', value)}>
                <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {typeOptions.map((option) => {
                    const IconComponent = option.icon
                    return (
                      <SelectItem key={option.value} value={option.value}>
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4" />
                          {option.label}
                        </div>
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">カテゴリ</Label>
              <Select value={formData.category} onValueChange={(value: any) => handleInputChange('category', value)}>
                <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${option.color}`}></div>
                        {option.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 場所 */}
          <div className="space-y-2">
            <Label htmlFor="location" className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              場所（任意）
            </Label>
            <Input
              id="location"
              value={formData.location || ''}
              onChange={(e) => handleInputChange('location', e.target.value)}
              placeholder="例: リビング、公園、お家"
              className="border-cyan-200 focus:border-cyan-400"
            />
          </div>

          {/* 画像アップロード */}
          <ImageUpload
            onImageUploaded={handleImageUploaded}
            onImageRemove={handleImageRemove}
            disabled={isSubmitting}
          />

          {/* タグ */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Tag className="h-4 w-4" />
              タグ
            </Label>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="タグを入力..."
                className="flex-1 border-cyan-200 focus:border-cyan-400"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addTag()
                  }
                }}
              />
              <Button 
                type="button" 
                onClick={addTag}
                size="sm"
                variant="outline"
                className="border-cyan-300 text-cyan-700 hover:bg-cyan-50"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            {/* タグ表示 */}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag, index) => (
                  <Badge 
                    key={index} 
                    variant="outline" 
                    className="flex items-center gap-1 bg-cyan-50 border-cyan-200 text-cyan-700"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-red-500"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* アクションボタン */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1"
              disabled={isSubmitting}
            >
              キャンセル
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  作成中...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  メモリーを作成
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}