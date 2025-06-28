'use client'

import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
  Edit,
  Trash2,
} from 'lucide-react'
import { updateMemory, deleteMemory, MemoryRecordUpdateRequest } from '@/libs/api/memories'
import { ImageUpload } from './image-upload'

interface MemoryRecord {
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

interface EditMemoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  memory: MemoryRecord | null
  onMemoryUpdated: () => void
  onMemoryDeleted: () => void
}

export function EditMemoryModal({
  open,
  onOpenChange,
  memory,
  onMemoryUpdated,
  onMemoryDeleted,
}: EditMemoryModalProps) {
  const [formData, setFormData] = useState<MemoryRecordUpdateRequest>({
    title: '',
    description: '',
    date: '',
    type: 'photo',
    category: 'daily',
    location: '',
    tags: [],
    favorited: false,
  })

  const [newTag, setNewTag] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)

  // メモリーデータをフォームに設定
  useEffect(() => {
    if (memory && open) {
      setFormData({
        title: memory.title,
        description: memory.description,
        date: memory.date,
        type: memory.type,
        category: memory.category,
        location: memory.location || '',
        tags: [...memory.tags],
        favorited: memory.favorited,
      })
      setNewTag('')
      setShowDeleteConfirm(false)
      setUploadedImageUrl(null)
    }
  }, [memory, open])

  const typeOptions = [
    { value: 'photo', label: '写真', icon: Camera },
    { value: 'video', label: '動画', icon: Video },
    { value: 'album', label: 'アルバム', icon: Archive },
  ]

  const categoryOptions = [
    { value: 'milestone', label: 'マイルストーン', color: 'from-purple-500 to-purple-600' },
    { value: 'daily', label: '日常', color: 'from-blue-500 to-blue-600' },
    { value: 'family', label: '家族', color: 'from-green-500 to-green-600' },
    { value: 'special', label: '特別', color: 'from-pink-500 to-pink-600' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!memory) return

    if (!formData.title?.trim()) {
      alert('タイトルを入力してください')
      return
    }

    if (!formData.description?.trim()) {
      alert('説明を入力してください')
      return
    }

    setIsSubmitting(true)

    try {
      // アップロードされた画像URLがある場合は更新
      const updateData = {
        ...formData,
        ...(uploadedImageUrl && {
          media_url: uploadedImageUrl,
          thumbnail_url: uploadedImageUrl,
        }),
      }

      const result = await updateMemory(memory.id, updateData)

      if (result.success) {
        onOpenChange(false)
        onMemoryUpdated()
        alert('メモリーが更新されました！')
      } else {
        alert(result.message || 'メモリーの更新に失敗しました')
      }
    } catch (error) {
      console.error('メモリー更新エラー:', error)
      alert('メモリーの更新中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!memory) return

    setIsDeleting(true)

    try {
      const result = await deleteMemory(memory.id)

      if (result.success) {
        onOpenChange(false)
        onMemoryDeleted()
        alert('メモリーが削除されました')
      } else {
        alert(result.message || 'メモリーの削除に失敗しました')
      }
    } catch (error) {
      console.error('メモリー削除エラー:', error)
      alert('メモリーの削除中にエラーが発生しました')
    } finally {
      setIsDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  const addTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()],
      }))
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || [],
    }))
  }

  const handleInputChange = (field: keyof MemoryRecordUpdateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleImageUploaded = (fileUrl: string) => {
    setUploadedImageUrl(fileUrl)
  }

  const handleImageRemove = () => {
    setUploadedImageUrl(null)
  }

  if (!memory) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <Edit className="h-6 w-6 text-cyan-600" />
            メモリーを編集
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            メモリーの情報を編集できます
          </DialogDescription>
        </DialogHeader>

        {!showDeleteConfirm ? (
          <form onSubmit={handleSubmit} className="space-y-6 pt-4">
            {/* タイトル */}
            <div className="space-y-2">
              <Label htmlFor="title" className="text-sm font-medium text-gray-700">
                タイトル *
              </Label>
              <Input
                id="title"
                value={formData.title || ''}
                onChange={e => handleInputChange('title', e.target.value)}
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
                value={formData.description || ''}
                onChange={e => handleInputChange('description', e.target.value)}
                placeholder="この瞬間について詳しく説明してください..."
                rows={3}
                className="border-cyan-200 focus:border-cyan-400"
                required
              />
            </div>

            {/* 日付とお気に入り */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label
                  htmlFor="date"
                  className="flex items-center gap-2 text-sm font-medium text-gray-700"
                >
                  <Calendar className="h-4 w-4" />
                  日付
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date || ''}
                  onChange={e => handleInputChange('date', e.target.value)}
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
                        ? 'bg-red-500 text-white hover:bg-red-600'
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
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-700">メディアタイプ</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value: any) => handleInputChange('type', value)}
                >
                  <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {typeOptions.map(option => {
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
                <Select
                  value={formData.category}
                  onValueChange={(value: any) => handleInputChange('category', value)}
                >
                  <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categoryOptions.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        <div className="flex items-center gap-2">
                          <div
                            className={`h-3 w-3 rounded-full bg-gradient-to-r ${option.color}`}
                          ></div>
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
              <Label
                htmlFor="location"
                className="flex items-center gap-2 text-sm font-medium text-gray-700"
              >
                <MapPin className="h-4 w-4" />
                場所（任意）
              </Label>
              <Input
                id="location"
                value={formData.location || ''}
                onChange={e => handleInputChange('location', e.target.value)}
                placeholder="例: リビング、公園、お家"
                className="border-cyan-200 focus:border-cyan-400"
              />
            </div>

            {/* 画像アップロード */}
            <ImageUpload
              onImageUploaded={handleImageUploaded}
              onImageRemove={handleImageRemove}
              currentImageUrl={memory.mediaUrl}
              disabled={isSubmitting}
            />

            {/* タグ */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Tag className="h-4 w-4" />
                タグ
              </Label>
              <div className="flex gap-2">
                <Input
                  value={newTag}
                  onChange={e => setNewTag(e.target.value)}
                  placeholder="タグを入力..."
                  className="flex-1 border-cyan-200 focus:border-cyan-400"
                  onKeyPress={e => {
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
              {formData.tags && formData.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {formData.tags.map((tag, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="flex items-center gap-1 border-cyan-200 bg-cyan-50 text-cyan-700"
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
                type="button"
                variant="destructive"
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center gap-2"
                disabled={isSubmitting}
              >
                <Trash2 className="h-4 w-4" />
                削除
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-600 hover:to-blue-600"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    更新中...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    更新
                  </>
                )}
              </Button>
            </div>
          </form>
        ) : (
          /* 削除確認画面 */
          <div className="space-y-6 pt-4">
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="mb-2 text-lg font-medium text-gray-900">メモリーを削除しますか？</h3>
              <p className="mb-4 text-sm text-gray-500">
                「{memory.title}」を削除します。この操作は取り消せません。
              </p>
            </div>

            <div className="flex gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1"
                disabled={isDeleting}
              >
                キャンセル
              </Button>
              <Button
                type="button"
                variant="destructive"
                onClick={handleDelete}
                className="flex-1"
                disabled={isDeleting}
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
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
        )}
      </DialogContent>
    </Dialog>
  )
}
