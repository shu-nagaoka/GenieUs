'use client'

import React, { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Save, 
  Loader2, 
  Plus,
  X,
  Trophy,
  Star,
  Trash2
} from 'lucide-react'
import { FaTrophy } from 'react-icons/fa'
import { updateEffortRecord, deleteEffortRecord, EffortRecordUpdateRequest } from '@/libs/api/effort-records'

interface EditEffortRecordModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  recordData: {
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
  } | null
  onSuccess: () => void
}

export function EditEffortRecordModal({ 
  open, 
  onOpenChange, 
  recordData,
  onSuccess 
}: EditEffortRecordModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [newHighlight, setNewHighlight] = useState('')
  const [newAchievement, setNewAchievement] = useState('')
  
  const [formData, setFormData] = useState<EffortRecordUpdateRequest>({
    date: '',
    period: '過去1週間',
    effort_count: 0,
    highlights: [],
    score: 5.0,
    categories: {
      feeding: 70,
      sleep: 70,
      play: 70,
      care: 70
    },
    summary: '',
    achievements: []
  })

  // 編集対象データでフォームを初期化
  useEffect(() => {
    if (recordData && open) {
      setFormData({
        date: recordData.date,
        period: recordData.period,
        effort_count: recordData.effortCount,
        highlights: [...recordData.highlights],
        score: recordData.score,
        categories: {
          feeding: recordData.categories.feeding,
          sleep: recordData.categories.sleep,
          play: recordData.categories.play,
          care: recordData.categories.care
        },
        summary: recordData.summary,
        achievements: [...recordData.achievements]
      })
      setNewHighlight('')
      setNewAchievement('')
    }
  }, [recordData, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!recordData?.id) return
    
    if (!formData.summary?.trim()) {
      alert('サマリーを入力してください')
      return
    }
    
    if (!formData.effort_count || formData.effort_count <= 0) {
      alert('努力回数を入力してください')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      const result = await updateEffortRecord(recordData.id, formData)
      if (result.success) {
        onSuccess()
        onOpenChange(false)
        alert('努力記録を更新しました')
      } else {
        throw new Error(result.message || '更新に失敗しました')
      }
    } catch (error) {
      console.error('努力記録更新エラー:', error)
      alert('努力記録の更新中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!recordData?.id) return
    
    if (!confirm('この努力記録を削除しますか？この操作は取り消せません。')) {
      return
    }
    
    setIsDeleting(true)
    
    try {
      const result = await deleteEffortRecord(recordData.id)
      if (result.success) {
        onSuccess()
        onOpenChange(false)
        alert('努力記録を削除しました')
      } else {
        throw new Error(result.message || '削除に失敗しました')
      }
    } catch (error) {
      console.error('努力記録削除エラー:', error)
      alert('努力記録の削除中にエラーが発生しました')
    } finally {
      setIsDeleting(false)
    }
  }

  const addHighlight = () => {
    if (newHighlight.trim() && !formData.highlights?.includes(newHighlight.trim())) {
      setFormData(prev => ({
        ...prev,
        highlights: [...(prev.highlights || []), newHighlight.trim()]
      }))
      setNewHighlight('')
    }
  }

  const removeHighlight = (index: number) => {
    setFormData(prev => ({
      ...prev,
      highlights: prev.highlights?.filter((_, i) => i !== index) || []
    }))
  }

  const addAchievement = () => {
    if (newAchievement.trim() && !formData.achievements?.includes(newAchievement.trim())) {
      setFormData(prev => ({
        ...prev,
        achievements: [...(prev.achievements || []), newAchievement.trim()]
      }))
      setNewAchievement('')
    }
  }

  const removeAchievement = (index: number) => {
    setFormData(prev => ({
      ...prev,
      achievements: prev.achievements?.filter((_, i) => i !== index) || []
    }))
  }

  const updateCategory = (category: keyof NonNullable<typeof formData.categories>, value: number) => {
    setFormData(prev => ({
      ...prev,
      categories: {
        ...prev.categories!,
        [category]: value
      }
    }))
  }

  if (!recordData) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <FaTrophy className="h-6 w-6 text-emerald-600" />
            努力記録を編集
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            記録内容を更新または削除できます
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          {/* 基本情報 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date" className="text-sm font-medium text-gray-700">
                記録日 *
              </Label>
              <Input
                id="date"
                type="date"
                value={formData.date}
                onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                className="border-gray-200 focus:border-emerald-400"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="period" className="text-sm font-medium text-gray-700">
                期間 *
              </Label>
              <Select value={formData.period} onValueChange={(value) => setFormData(prev => ({ ...prev, period: value }))}>
                <SelectTrigger className="border-gray-200 focus:border-emerald-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="過去3日間">過去3日間</SelectItem>
                  <SelectItem value="過去1週間">過去1週間</SelectItem>
                  <SelectItem value="過去2週間">過去2週間</SelectItem>
                  <SelectItem value="過去1ヶ月">過去1ヶ月</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="effort_count" className="text-sm font-medium text-gray-700">
                努力回数 *
              </Label>
              <Input
                id="effort_count"
                type="number"
                min="0"
                value={formData.effort_count}
                onChange={(e) => setFormData(prev => ({ ...prev, effort_count: parseInt(e.target.value) || 0 }))}
                className="border-gray-200 focus:border-emerald-400"
                placeholder="例: 25"
                required
              />
            </div>
          </div>

          {/* スコア */}
          <div className="space-y-2">
            <Label htmlFor="score" className="text-sm font-medium text-gray-700">
              総合スコア (1-10) *
            </Label>
            <div className="flex items-center gap-4">
              <Input
                id="score"
                type="number"
                min="1"
                max="10"
                step="0.1"
                value={formData.score}
                onChange={(e) => setFormData(prev => ({ ...prev, score: parseFloat(e.target.value) || 5.0 }))}
                className="border-gray-200 focus:border-emerald-400 w-24"
                required
              />
              <span className="text-sm text-gray-600">/ 10.0</span>
            </div>
          </div>

          {/* カテゴリ別スコア */}
          <div className="space-y-4">
            <Label className="text-sm font-medium text-gray-700">カテゴリ別スコア (%)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'feeding', label: '食事・授乳', color: 'from-orange-500 to-red-600' },
                { key: 'sleep', label: '睡眠', color: 'from-blue-500 to-indigo-600' },
                { key: 'play', label: '遊び・学び', color: 'from-green-500 to-emerald-600' },
                { key: 'care', label: 'ケア・世話', color: 'from-purple-500 to-pink-600' }
              ].map(({ key, label, color }) => (
                <div key={key} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    <span className="text-sm font-bold text-gray-800">{formData.categories?.[key as keyof NonNullable<typeof formData.categories>]}%</span>
                  </div>
                  <Input
                    type="range"
                    min="0"
                    max="100"
                    value={formData.categories?.[key as keyof NonNullable<typeof formData.categories>] || 70}
                    onChange={(e) => updateCategory(key as keyof NonNullable<typeof formData.categories>, parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div 
                      className={`h-2 bg-gradient-to-r ${color} rounded-full transition-all duration-300`}
                      style={{ width: `${formData.categories?.[key as keyof NonNullable<typeof formData.categories>] || 70}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* サマリー */}
          <div className="space-y-2">
            <Label htmlFor="summary" className="text-sm font-medium text-gray-700">
              期間サマリー *
            </Label>
            <Textarea
              id="summary"
              value={formData.summary}
              onChange={(e) => setFormData(prev => ({ ...prev, summary: e.target.value }))}
              placeholder="この期間の努力や成果について詳しく記述してください..."
              rows={4}
              className="border-gray-200 focus:border-emerald-400"
              required
            />
          </div>

          {/* ハイライト */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Star className="h-4 w-4" />
              ハイライト
            </Label>
            
            <div className="flex gap-2">
              <Input
                value={newHighlight}
                onChange={(e) => setNewHighlight(e.target.value)}
                placeholder="特別な出来事や成果を追加..."
                className="border-gray-200 focus:border-emerald-400"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addHighlight())}
              />
              <Button
                type="button"
                onClick={addHighlight}
                variant="outline"
                className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {formData.highlights?.map((highlight, index) => (
                <Badge key={index} variant="outline" className="text-emerald-700 border-emerald-300 bg-emerald-50">
                  {highlight}
                  <button
                    type="button"
                    onClick={() => removeHighlight(index)}
                    className="ml-2 text-emerald-600 hover:text-emerald-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          {/* 達成事項 */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Trophy className="h-4 w-4" />
              達成事項
            </Label>
            
            <div className="flex gap-2">
              <Input
                value={newAchievement}
                onChange={(e) => setNewAchievement(e.target.value)}
                placeholder="達成したマイルストーンや目標を追加..."
                className="border-gray-200 focus:border-emerald-400"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAchievement())}
              />
              <Button
                type="button"
                onClick={addAchievement}
                variant="outline"
                className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {formData.achievements?.map((achievement, index) => (
                <Badge key={index} variant="outline" className="text-purple-700 border-purple-300 bg-purple-50">
                  {achievement}
                  <button
                    type="button"
                    onClick={() => removeAchievement(index)}
                    className="ml-2 text-purple-600 hover:text-purple-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          {/* アクションボタン */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1"
              disabled={isSubmitting || isDeleting}
            >
              キャンセル
            </Button>
            
            <Button
              type="button"
              variant="destructive"
              onClick={handleDelete}
              className="flex-1"
              disabled={isSubmitting || isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  削除中...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  削除
                </>
              )}
            </Button>
            
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-700 hover:to-teal-800 text-white"
              disabled={isSubmitting || isDeleting}
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
      </DialogContent>
    </Dialog>
  )
}