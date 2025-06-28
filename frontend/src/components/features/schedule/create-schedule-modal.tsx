'use client'

import React, { useState } from 'react'
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
import {
  Calendar,
  Clock,
  MapPin,
  Stethoscope,
  Users,
  Plus,
  Save,
  Loader2,
  Baby,
} from 'lucide-react'
import { MdVaccines, MdOutdoorGrill } from 'react-icons/md'
import { createScheduleEvent, ScheduleEventCreateRequest } from '@/libs/api/schedules'

interface CreateScheduleModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onEventCreated: () => void
}

export function CreateScheduleModal({
  open,
  onOpenChange,
  onEventCreated,
}: CreateScheduleModalProps) {
  const [formData, setFormData] = useState<ScheduleEventCreateRequest>({
    title: '',
    date: new Date().toISOString().split('T')[0],
    time: '10:00',
    type: 'other',
    location: '',
    description: '',
    status: 'upcoming',
    created_by: 'user',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  const typeOptions = [
    { value: 'medical', label: '医療・健康', icon: Stethoscope, color: 'from-red-500 to-red-600' },
    { value: 'outing', label: 'お出かけ', icon: MapPin, color: 'from-green-500 to-green-600' },
    { value: 'school', label: '学校行事', icon: Users, color: 'from-purple-500 to-purple-600' },
    { value: 'other', label: 'その他', icon: Calendar, color: 'from-gray-500 to-gray-600' },
  ]

  const statusOptions = [
    { value: 'upcoming', label: '予定', color: 'text-blue-600' },
    { value: 'completed', label: '完了', color: 'text-green-600' },
    { value: 'cancelled', label: 'キャンセル', color: 'text-gray-600' },
  ]

  const createdByOptions = [
    { value: 'user', label: '手動登録' },
    { value: 'genie', label: 'Genie提案' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
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
      const result = await createScheduleEvent(formData)

      if (result.success) {
        // フォームをリセット
        setFormData({
          title: '',
          date: new Date().toISOString().split('T')[0],
          time: '10:00',
          type: 'other',
          location: '',
          description: '',
          status: 'upcoming',
          created_by: 'user',
        })

        // モーダルを閉じて親コンポーネントに通知
        onOpenChange(false)
        onEventCreated()

        alert('予定が作成されました！')
      } else {
        alert(result.message || '予定の作成に失敗しました')
      }
    } catch (error) {
      console.error('予定作成エラー:', error)
      alert('予定の作成中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field: keyof ScheduleEventCreateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <Calendar className="h-6 w-6 text-cyan-600" />
            新しい予定を作成
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            大切な予定を記録しましょう
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
              onChange={e => handleInputChange('title', e.target.value)}
              placeholder="例: 1歳6ヶ月健診、水族館デビュー"
              className="border-cyan-200 focus:border-cyan-400"
              required
            />
          </div>

          {/* 日付と時間 */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label
                htmlFor="date"
                className="flex items-center gap-2 text-sm font-medium text-gray-700"
              >
                <Calendar className="h-4 w-4" />
                日付 *
              </Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={e => handleInputChange('date', e.target.value)}
                className="border-cyan-200 focus:border-cyan-400"
                required
              />
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="time"
                className="flex items-center gap-2 text-sm font-medium text-gray-700"
              >
                <Clock className="h-4 w-4" />
                時間 *
              </Label>
              <Input
                id="time"
                type="time"
                value={formData.time}
                onChange={e => handleInputChange('time', e.target.value)}
                className="border-cyan-200 focus:border-cyan-400"
                required
              />
            </div>
          </div>

          {/* タイプとステータス */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">予定タイプ</Label>
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
              <Label className="text-sm font-medium text-gray-700">ステータス</Label>
              <Select
                value={formData.status}
                onValueChange={(value: any) => handleInputChange('status', value)}
              >
                <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map(option => (
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
              onChange={e => handleInputChange('description', e.target.value)}
              placeholder="この予定について詳しく説明してください..."
              rows={3}
              className="border-cyan-200 focus:border-cyan-400"
            />
          </div>

          {/* 作成者 */}
          <div className="space-y-2">
            <Label className="text-sm font-medium text-gray-700">作成者</Label>
            <Select
              value={formData.created_by}
              onValueChange={(value: any) => handleInputChange('created_by', value)}
            >
              <SelectTrigger className="border-cyan-200 focus:border-cyan-400">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {createdByOptions.map(option => (
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
              type="submit"
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-600 hover:to-blue-600"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  作成中...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  予定を作成
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
