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
  TrendingUp,
  Baby,
  Ruler,
  Scale,
  MessageCircle,
  Smile,
  Heart,
  Star,
  Calendar,
  Award,
  Camera,
  X,
  Plus,
  Save,
  Loader2
} from 'lucide-react'
import { createGrowthRecord, GrowthRecordCreateRequest } from '@/lib/api/growth-records'
import { ImageUpload } from '@/components/features/memories/image-upload'

interface CreateGrowthRecordModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onRecordCreated: () => void
}

export function CreateGrowthRecordModal({ open, onOpenChange, onRecordCreated }: CreateGrowthRecordModalProps) {
  const [formData, setFormData] = useState<GrowthRecordCreateRequest>({
    child_name: '',
    date: new Date().toISOString().split('T')[0],
    age_in_months: 0,
    type: 'body_growth',
    category: 'movement',
    title: '',
    description: '',
    detected_by: 'parent'
  })
  
  const [newEmotion, setNewEmotion] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null)

  const typeOptions = [
    { value: 'body_growth', label: 'からだの成長', icon: Ruler, color: 'from-blue-500 to-blue-600' },
    { value: 'language_growth', label: 'ことばの成長', icon: MessageCircle, color: 'from-green-500 to-green-600' },
    { value: 'skills', label: 'できること', icon: Star, color: 'from-purple-500 to-purple-600' },
    { value: 'social_skills', label: 'お友達との関わり', icon: Heart, color: 'from-pink-500 to-pink-600' },
    { value: 'hobbies', label: '習い事・特技', icon: Award, color: 'from-amber-500 to-amber-600' },
    { value: 'life_skills', label: '生活スキル', icon: TrendingUp, color: 'from-teal-500 to-teal-600' }
  ]

  const categoryOptions = {
    body_growth: [
      { value: 'height', label: '身長', icon: Ruler },
      { value: 'weight', label: '体重', icon: Scale },
      { value: 'movement', label: '運動・歩行', icon: TrendingUp }
    ],
    language_growth: [
      { value: 'speech', label: 'おしゃべり', icon: MessageCircle },
      { value: 'first_words', label: '初めての言葉', icon: MessageCircle },
      { value: 'vocabulary', label: '語彙', icon: MessageCircle }
    ],
    skills: [
      { value: 'colors', label: '色がわかる', icon: Star },
      { value: 'numbers', label: '数を数える', icon: Star },
      { value: 'puzzle', label: 'パズル', icon: Star },
      { value: 'drawing', label: 'お絵描き', icon: Star }
    ],
    social_skills: [
      { value: 'playing_together', label: '一緒に遊ぶ', icon: Heart },
      { value: 'helping', label: 'お手伝い', icon: Heart },
      { value: 'sharing', label: '分け合う', icon: Heart },
      { value: 'kindness', label: 'やさしさ', icon: Heart }
    ],
    hobbies: [
      { value: 'piano', label: 'ピアノ', icon: Award },
      { value: 'swimming', label: '水泳', icon: Award },
      { value: 'dancing', label: 'ダンス', icon: Award },
      { value: 'sports', label: 'スポーツ', icon: Award }
    ],
    life_skills: [
      { value: 'toilet', label: 'トイレ', icon: TrendingUp },
      { value: 'brushing', label: '歯磨き', icon: TrendingUp },
      { value: 'dressing', label: 'お着替え', icon: TrendingUp },
      { value: 'cleaning', label: 'お片付け', icon: TrendingUp }
    ]
  }

  const getCurrentCategoryOptions = () => {
    return categoryOptions[formData.type as keyof typeof categoryOptions] || []
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.child_name.trim()) {
      alert('お子さんの名前を入力してください')
      return
    }
    
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
      const recordData = {
        ...formData,
        image_url: uploadedImageUrl
      }
      
      const result = await createGrowthRecord(recordData)
      
      if (result.success) {
        // フォームをリセット
        setFormData({
          child_name: '',
          date: new Date().toISOString().split('T')[0],
          age_in_months: 0,
          type: 'milestone',
          category: 'movement',
          title: '',
          description: '',
          detected_by: 'parent'
        })
        setNewEmotion('')
        setUploadedImageUrl(null)
        
        // モーダルを閉じて親コンポーネントに通知
        onOpenChange(false)
        onRecordCreated()
        
        alert('成長記録が作成されました！')
      } else {
        alert(result.message || '成長記録の作成に失敗しました')
      }
    } catch (error) {
      console.error('成長記録作成エラー:', error)
      alert('成長記録の作成中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const addEmotion = () => {
    if (newEmotion.trim() && !formData.emotions?.includes(newEmotion.trim())) {
      setFormData(prev => ({
        ...prev,
        emotions: [...(prev.emotions || []), newEmotion.trim()]
      }))
      setNewEmotion('')
    }
  }

  const removeEmotion = (emotionToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      emotions: prev.emotions?.filter(emotion => emotion !== emotionToRemove) || []
    }))
  }

  const handleInputChange = (field: keyof GrowthRecordCreateRequest, value: any) => {
    setFormData(prev => {
      const updated = {
        ...prev,
        [field]: value
      }
      
      // タイプが変更された場合、カテゴリをリセット
      if (field === 'type') {
        const newCategoryOptions = categoryOptions[value as keyof typeof categoryOptions] || []
        updated.category = newCategoryOptions[0]?.value || 'movement'
      }
      
      return updated
    })
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
            <TrendingUp className="h-6 w-6 text-blue-600" />
            新しい成長記録を作成
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            お子さんの大切な成長の瞬間を記録しましょう
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          {/* 子どもの名前と年齢 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="child_name" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Baby className="h-4 w-4" />
                お子さんの名前 *
              </Label>
              <Input
                id="child_name"
                value={formData.child_name}
                onChange={(e) => handleInputChange('child_name', e.target.value)}
                placeholder="例: 花子ちゃん"
                className="border-blue-200 focus:border-blue-400"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="age_in_months" className="text-sm font-medium text-gray-700">
                年齢（月齢）*
              </Label>
              <Input
                id="age_in_months"
                type="number"
                min="0"
                max="120"
                value={formData.age_in_months}
                onChange={(e) => handleInputChange('age_in_months', parseInt(e.target.value) || 0)}
                placeholder="8"
                className="border-blue-200 focus:border-blue-400"
                required
              />
            </div>
          </div>

          {/* タイトル */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium text-gray-700">
              タイトル *
            </Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="例: 初めてのつかまり立ち、新しい言葉を覚えた"
              className="border-blue-200 focus:border-blue-400"
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
              placeholder="この成長について詳しく説明してください..."
              rows={3}
              className="border-blue-200 focus:border-blue-400"
              required
            />
          </div>

          {/* 日付 */}
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
              className="border-blue-200 focus:border-blue-400"
            />
          </div>

          {/* タイプとカテゴリ */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">発達タイプ</Label>
              <Select value={formData.type} onValueChange={(value: any) => handleInputChange('type', value)}>
                <SelectTrigger className="border-blue-200 focus:border-blue-400">
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
                <SelectTrigger className="border-blue-200 focus:border-blue-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {getCurrentCategoryOptions().map((option) => {
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
          </div>

          {/* 測定値（身体発達の場合） */}
          {formData.type === 'physical' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="value" className="text-sm font-medium text-gray-700">
                  測定値
                </Label>
                <Input
                  id="value"
                  value={formData.value || ''}
                  onChange={(e) => handleInputChange('value', e.target.value)}
                  placeholder="例: 67.5"
                  className="border-blue-200 focus:border-blue-400"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="unit" className="text-sm font-medium text-gray-700">
                  単位
                </Label>
                <Input
                  id="unit"
                  value={formData.unit || ''}
                  onChange={(e) => handleInputChange('unit', e.target.value)}
                  placeholder="例: cm, kg"
                  className="border-blue-200 focus:border-blue-400"
                />
              </div>
            </div>
          )}

          {/* 画像アップロード */}
          <ImageUpload
            onImageUploaded={handleImageUploaded}
            onImageRemove={handleImageRemove}
            disabled={isSubmitting}
          />

          {/* 感情（感情発達の場合） */}
          {(formData.type === 'emotional' || formData.type === 'photo') && (
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Heart className="h-4 w-4" />
                感情・表情
              </Label>
              <div className="flex gap-2">
                <Input
                  value={newEmotion}
                  onChange={(e) => setNewEmotion(e.target.value)}
                  placeholder="感情を入力..."
                  className="flex-1 border-blue-200 focus:border-blue-400"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addEmotion()
                    }
                  }}
                />
                <Button 
                  type="button" 
                  onClick={addEmotion}
                  size="sm"
                  variant="outline"
                  className="border-blue-300 text-blue-700 hover:bg-blue-50"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              
              {/* 感情表示 */}
              {formData.emotions && formData.emotions.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.emotions.map((emotion, index) => (
                    <Badge 
                      key={index} 
                      variant="outline" 
                      className="flex items-center gap-1 bg-blue-50 border-blue-200 text-blue-700"
                    >
                      {emotion}
                      <button
                        type="button"
                        onClick={() => removeEmotion(emotion)}
                        className="ml-1 hover:text-red-500"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 発達段階 */}
          <div className="space-y-2">
            <Label htmlFor="development_stage" className="text-sm font-medium text-gray-700">
              発達段階（任意）
            </Label>
            <Input
              id="development_stage"
              value={formData.development_stage || ''}
              onChange={(e) => handleInputChange('development_stage', e.target.value)}
              placeholder="例: 標準範囲、順調な発達、注意が必要"
              className="border-blue-200 focus:border-blue-400"
            />
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
              className="flex-1 bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-white"
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
                  記録を作成
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}