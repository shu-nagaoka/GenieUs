'use client'

import React, { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Calendar,
  Clock,
  MapPin,
  Stethoscope,
  Users,
  Save,
  Loader2,
  Edit,
  Trash2
} from 'lucide-react'
import { updateScheduleEvent, deleteScheduleEvent, ScheduleEvent, ScheduleEventUpdateRequest } from '@/libs/api/schedules'

interface EditScheduleModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  event: ScheduleEvent | null
  onEventUpdated: () => void
  onEventDeleted: () => void
}

export function EditScheduleModal({ open, onOpenChange, event, onEventUpdated, onEventDeleted }: EditScheduleModalProps) {
  const [formData, setFormData] = useState<ScheduleEventUpdateRequest>({
    title: '',
    date: '',
    time: '',
    type: 'other',
    location: '',
    description: '',
    status: 'upcoming',
    created_by: 'user'
  })
  
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  // イベントデータをフォームに設定
  useEffect(() => {
    if (event && open) {
      setFormData({
        title: event.title,
        date: event.date,
        time: event.time,
        type: event.type,
        location: event.location,
        description: event.description,
        status: event.status,
        created_by: event.created_by
      })
      setShowDeleteConfirm(false)
    }
  }, [event, open])

  const typeOptions = [
    { value: 'medical', label: '医療・健康', icon: Stethoscope, color: 'from-red-500 to-red-600' },
    { value: 'outing', label: 'お出かけ', icon: MapPin, color: 'from-green-500 to-green-600' },
    { value: 'school', label: '学校行事', icon: Users, color: 'from-purple-500 to-purple-600' },
    { value: 'other', label: 'その他', icon: Calendar, color: 'from-gray-500 to-gray-600' }
  ]

  const statusOptions = [
    { value: 'upcoming', label: '予定', color: 'text-blue-600' },
    { value: 'completed', label: '完了', color: 'text-green-600' },
    { value: 'cancelled', label: 'キャンセル', color: 'text-gray-600' }
  ]

  const createdByOptions = [
    { value: 'user', label: '手動登録' },
    { value: 'genie', label: 'Genie提案' }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!event) return
    
    if (!formData.title?.trim()) {
      alert('タイトルを入力してください')
      return
    }
    
    if (!formData.date) {
      alert('日付を選択してください')
      return
    }
    
    if (!formData.time) {
      alert('時間を選択してください')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const result = await updateScheduleEvent(event.id, formData)
      
      if (result.success) {
        onOpenChange(false)
        onEventUpdated()
        alert('予定が更新されました！')
      } else {
        alert(result.message || '予定の更新に失敗しました')
      }
    } catch (error) {
      console.error('予定更新エラー:', error)
      alert('予定の更新中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!event) return
    
    setIsDeleting(true)
    
    try {
      const result = await deleteScheduleEvent(event.id)
      
      if (result.success) {
        onOpenChange(false)
        onEventDeleted()
        alert('予定が削除されました')
      } else {
        alert(result.message || '予定の削除に失敗しました')
      }
    } catch (error) {
      console.error('予定削除エラー:', error)
      alert('予定の削除中にエラーが発生しました')
    } finally {
      setIsDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  const handleInputChange = (field: keyof ScheduleEventUpdateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  if (!event) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <Edit className="h-6 w-6 text-cyan-600" />
            予定を編集
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            予定の情報を編集できます
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
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="例: 1歳6ヶ月健診、水族館デビュー"
                className="border-cyan-200 focus:border-cyan-400"
                required
              />
            </div>

            {/* 日付と時間 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="date" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  日付 *
                </Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date || ''}
                  onChange={(e) => handleInputChange('date', e.target.value)}
                  className="border-cyan-200 focus:border-cyan-400"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="time" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  時間 *
                </Label>
                <Input
                  id="time"
                  type="time"
                  value={formData.time || ''}
                  onChange={(e) => handleInputChange('time', e.target.value)}
                  className="border-cyan-200 focus:border-cyan-400"
                  required
                />
              </div>
            </div>

            {/* タイプとステータス */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium text-gray-700">予定タイプ</Label>
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
                <Label className="text-sm font-medium text-gray-700">ステータス</Label>
                <Select value={formData.status} onValueChange={(value: any) => handleInputChange('status', value)}>
                  <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {statusOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        <span className={option.color}>{option.label}</span>
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
                placeholder="例: みなと保健センター、すみだ水族館"
                className="border-cyan-200 focus:border-cyan-400"
              />
            </div>

            {/* 説明 */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm font-medium text-gray-700">
                説明（任意）
              </Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="この予定について詳しく説明してください..."
                rows={3}
                className="border-cyan-200 focus:border-cyan-400"
              />
            </div>

            {/* 作成者 */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">作成者</Label>
              <Select value={formData.created_by} onValueChange={(value: any) => handleInputChange('created_by', value)}>
                <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {createdByOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
                className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    更新中...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
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
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                予定を削除しますか？
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                「{event.title}」を削除します。この操作は取り消せません。
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
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    削除中...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
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