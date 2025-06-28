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
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Users, Plus, Save, Loader2, Baby, Calendar, X } from 'lucide-react'
import { FaPaw } from 'react-icons/fa'
import { MdFamilyRestroom } from 'react-icons/md'

interface Child {
  name: string
  age: string
  gender: string
  birth_date: string
  characteristics: string
  allergies: string
  medical_notes: string
  concerns: string[]
}

interface Pet {
  name: string
  type: 'dog' | 'cat' | 'other'
  age: string
  characteristics: string
}

interface FamilyComposition {
  parent_name: string
  family_members: {
    has_father: boolean
    has_mother: boolean
    has_grandfather: boolean
    has_grandmother: boolean
    children_count: number
    has_pets: boolean
  }
  pets: Pet[]
  children: Child[]
  living_situation: string
  living_area: string
}

interface FamilyCompositionModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  familyData?: FamilyComposition | null
  onSave: (data: FamilyComposition) => Promise<void>
}

export function FamilyCompositionModal({
  open,
  onOpenChange,
  familyData,
  onSave,
}: FamilyCompositionModalProps) {
  const [formData, setFormData] = useState<FamilyComposition>({
    parent_name: '',
    family_members: {
      has_father: false,
      has_mother: false,
      has_grandfather: false,
      has_grandmother: false,
      children_count: 0,
      has_pets: false,
    },
    pets: [],
    children: [],
    living_situation: '',
    living_area: '',
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  // フォームデータの初期化
  useEffect(() => {
    if (familyData && open) {
      // 既存データを変換（子どもに concerns が無い場合は空配列を追加）
      const convertedData = {
        ...familyData,
        children: familyData.children.map(child => ({
          ...child,
          concerns: child.concerns || [],
        })),
      }
      setFormData(convertedData)
    } else if (open) {
      // 新規作成時のデフォルト値
      setFormData({
        parent_name: '',
        family_members: {
          has_father: false,
          has_mother: false,
          has_grandfather: false,
          has_grandmother: false,
          children_count: 0,
          has_pets: false,
        },
        pets: [],
        children: [],
        living_situation: '',
        living_area: '',
      })
    }
  }, [familyData, open])

  // 子どもの数が変更された時の処理
  useEffect(() => {
    const currentChildrenCount = formData.children.length
    const targetCount = formData.family_members.children_count

    if (targetCount > currentChildrenCount) {
      // 子どもを追加
      const newChildren = [...formData.children]
      for (let i = currentChildrenCount; i < targetCount; i++) {
        newChildren.push({
          name: '',
          age: '',
          gender: '',
          birth_date: '',
          characteristics: '',
          allergies: '',
          medical_notes: '',
          concerns: [],
        })
      }
      setFormData(prev => ({ ...prev, children: newChildren }))
    } else if (targetCount < currentChildrenCount) {
      // 子どもを削除
      setFormData(prev => ({
        ...prev,
        children: prev.children.slice(0, targetCount),
      }))
    }
  }, [formData.family_members.children_count])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.parent_name.trim()) {
      alert('保護者名を入力してください')
      return
    }

    setIsSubmitting(true)

    try {
      await onSave(formData)
      onOpenChange(false)
    } catch (error) {
      console.error('家族情報保存エラー:', error)
      alert('家族情報の保存中にエラーが発生しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateFamilyMember = (field: keyof typeof formData.family_members, value: any) => {
    setFormData(prev => ({
      ...prev,
      family_members: { ...prev.family_members, [field]: value },
    }))
  }

  const updateChild = (index: number, field: keyof Child, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      children: prev.children.map((child, i) =>
        i === index ? { ...child, [field]: value } : child
      ),
    }))
  }

  const addPet = () => {
    setFormData(prev => ({
      ...prev,
      pets: [...prev.pets, { name: '', type: 'dog', age: '', characteristics: '' }],
    }))
  }

  const removePet = (index: number) => {
    setFormData(prev => ({
      ...prev,
      pets: prev.pets.filter((_, i) => i !== index),
    }))
  }

  const updatePet = (index: number, field: keyof Pet, value: string) => {
    setFormData(prev => ({
      ...prev,
      pets: prev.pets.map((pet, i) => (i === index ? { ...pet, [field]: value } : pet)),
    }))
  }

  const getFamilyStructureDescription = () => {
    const { has_father, has_mother, has_grandfather, has_grandmother, children_count, has_pets } =
      formData.family_members

    // 基本構成を決定
    let baseStructure = ''
    if (has_father && has_mother) {
      baseStructure = '夫婦'
    } else if (has_father) {
      baseStructure = 'パパ'
    } else if (has_mother) {
      baseStructure = 'ママ'
    }

    // 子どもの情報
    const childrenPart = children_count > 0 ? `お子さん${children_count}人` : ''

    // 祖父母の情報
    const grandparentsInfo = []
    if (has_grandfather) grandparentsInfo.push('おじいちゃん')
    if (has_grandmother) grandparentsInfo.push('おばあちゃん')
    const grandparentsPart = grandparentsInfo.length > 0 ? grandparentsInfo.join('・') : ''

    // ペットの情報
    const petsPart = has_pets && formData.pets.length > 0 ? `ペット${formData.pets.length}匹` : ''

    // 自然な日本語で組み立て
    const parts = []
    if (baseStructure) parts.push(baseStructure)
    if (childrenPart) parts.push(childrenPart)

    let description = parts.join('と') || '未設定'

    // 追加情報を括弧内で表示
    const additionalInfo = []
    if (grandparentsPart) additionalInfo.push(grandparentsPart)
    if (petsPart) additionalInfo.push(petsPart)

    if (additionalInfo.length > 0) {
      description += ` (${additionalInfo.join('、')})`
    }

    return description
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-4xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-gray-800">
            <MdFamilyRestroom className="h-6 w-6 text-gray-600" />
            {familyData ? '家族情報を編集' : '家族情報を登録'}
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            ご家族の構成や、お子さんの情報を教えてください
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          {/* 保護者名 */}
          <div className="space-y-2">
            <Label htmlFor="parent_name" className="text-sm font-medium text-gray-700">
              保護者名 *
            </Label>
            <Input
              id="parent_name"
              value={formData.parent_name}
              onChange={e => setFormData(prev => ({ ...prev, parent_name: e.target.value }))}
              placeholder="例: 田中花子"
              className="border-gray-200 focus:border-gray-400"
              required
            />
          </div>

          {/* 居住エリア */}
          <div className="space-y-3">
            <Label className="text-sm font-medium text-gray-700">お住まいのエリア（任意）</Label>
            <p className="text-xs text-gray-500">
              地域に応じた子育て情報をお届けするために使用します
            </p>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="space-y-2">
                <Label className="text-xs text-gray-600">都道府県</Label>
                <select
                  value={formData.living_area.split('-')[0] || ''}
                  onChange={e => {
                    const prefecture = e.target.value
                    setFormData(prev => ({ ...prev, living_area: prefecture }))
                  }}
                  className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
                >
                  <option value="">選択してください</option>
                  <option value="北海道">北海道</option>
                  <option value="青森県">青森県</option>
                  <option value="岩手県">岩手県</option>
                  <option value="宮城県">宮城県</option>
                  <option value="秋田県">秋田県</option>
                  <option value="山形県">山形県</option>
                  <option value="福島県">福島県</option>
                  <option value="茨城県">茨城県</option>
                  <option value="栃木県">栃木県</option>
                  <option value="群馬県">群馬県</option>
                  <option value="埼玉県">埼玉県</option>
                  <option value="千葉県">千葉県</option>
                  <option value="東京都">東京都</option>
                  <option value="神奈川県">神奈川県</option>
                  <option value="新潟県">新潟県</option>
                  <option value="富山県">富山県</option>
                  <option value="石川県">石川県</option>
                  <option value="福井県">福井県</option>
                  <option value="山梨県">山梨県</option>
                  <option value="長野県">長野県</option>
                  <option value="岐阜県">岐阜県</option>
                  <option value="静岡県">静岡県</option>
                  <option value="愛知県">愛知県</option>
                  <option value="三重県">三重県</option>
                  <option value="滋賀県">滋賀県</option>
                  <option value="京都府">京都府</option>
                  <option value="大阪府">大阪府</option>
                  <option value="兵庫県">兵庫県</option>
                  <option value="奈良県">奈良県</option>
                  <option value="和歌山県">和歌山県</option>
                  <option value="鳥取県">鳥取県</option>
                  <option value="島根県">島根県</option>
                  <option value="岡山県">岡山県</option>
                  <option value="広島県">広島県</option>
                  <option value="山口県">山口県</option>
                  <option value="徳島県">徳島県</option>
                  <option value="香川県">香川県</option>
                  <option value="愛媛県">愛媛県</option>
                  <option value="高知県">高知県</option>
                  <option value="福岡県">福岡県</option>
                  <option value="佐賀県">佐賀県</option>
                  <option value="長崎県">長崎県</option>
                  <option value="熊本県">熊本県</option>
                  <option value="大分県">大分県</option>
                  <option value="宮崎県">宮崎県</option>
                  <option value="鹿児島県">鹿児島県</option>
                  <option value="沖縄県">沖縄県</option>
                </select>
              </div>

              {(formData.living_area.startsWith('東京都') ||
                formData.living_area.startsWith('大阪府') ||
                formData.living_area.startsWith('神奈川県')) && (
                <div className="space-y-2">
                  <Label className="text-xs text-gray-600">
                    {formData.living_area.startsWith('東京都')
                      ? '区・市'
                      : formData.living_area.startsWith('大阪府')
                        ? '市・区'
                        : '市・区'}
                  </Label>
                  <select
                    value={formData.living_area.split('-')[1] || ''}
                    onChange={e => {
                      const prefecture = formData.living_area.split('-')[0]
                      const area = e.target.value
                      setFormData(prev => ({
                        ...prev,
                        living_area: area ? `${prefecture}-${area}` : prefecture,
                      }))
                    }}
                    className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm focus:border-gray-400 focus:outline-none"
                  >
                    <option value="">選択してください</option>
                    {formData.living_area.startsWith('東京都') && (
                      <>
                        <option value="千代田区">千代田区</option>
                        <option value="中央区">中央区</option>
                        <option value="港区">港区</option>
                        <option value="新宿区">新宿区</option>
                        <option value="文京区">文京区</option>
                        <option value="台東区">台東区</option>
                        <option value="墨田区">墨田区</option>
                        <option value="江東区">江東区</option>
                        <option value="品川区">品川区</option>
                        <option value="目黒区">目黒区</option>
                        <option value="大田区">大田区</option>
                        <option value="世田谷区">世田谷区</option>
                        <option value="渋谷区">渋谷区</option>
                        <option value="中野区">中野区</option>
                        <option value="杉並区">杉並区</option>
                        <option value="豊島区">豊島区</option>
                        <option value="北区">北区</option>
                        <option value="荒川区">荒川区</option>
                        <option value="板橋区">板橋区</option>
                        <option value="練馬区">練馬区</option>
                        <option value="足立区">足立区</option>
                        <option value="葛飾区">葛飾区</option>
                        <option value="江戸川区">江戸川区</option>
                        <option value="八王子市">八王子市</option>
                        <option value="立川市">立川市</option>
                        <option value="武蔵野市">武蔵野市</option>
                        <option value="三鷹市">三鷹市</option>
                        <option value="府中市">府中市</option>
                        <option value="調布市">調布市</option>
                        <option value="その他市部">その他市部</option>
                      </>
                    )}
                    {formData.living_area.startsWith('神奈川県') && (
                      <>
                        <option value="横浜市">横浜市</option>
                        <option value="川崎市">川崎市</option>
                        <option value="相模原市">相模原市</option>
                        <option value="藤沢市">藤沢市</option>
                        <option value="茅ヶ崎市">茅ヶ崎市</option>
                        <option value="平塚市">平塚市</option>
                        <option value="鎌倉市">鎌倉市</option>
                        <option value="その他">その他</option>
                      </>
                    )}
                    {formData.living_area.startsWith('大阪府') && (
                      <>
                        <option value="大阪市">大阪市</option>
                        <option value="堺市">堺市</option>
                        <option value="豊中市">豊中市</option>
                        <option value="吹田市">吹田市</option>
                        <option value="枚方市">枚方市</option>
                        <option value="茨木市">茨木市</option>
                        <option value="その他">その他</option>
                      </>
                    )}
                  </select>
                </div>
              )}

              {formData.living_area && (
                <div className="space-y-2">
                  <Label className="text-xs text-gray-600">その他詳細（任意）</Label>
                  <Input
                    value={formData.living_area.split('-')[2] || ''}
                    onChange={e => {
                      const parts = formData.living_area.split('-')
                      const base = parts.slice(0, 2).join('-')
                      const detail = e.target.value
                      setFormData(prev => ({
                        ...prev,
                        living_area: detail ? `${base}-${detail}` : base,
                      }))
                    }}
                    placeholder="駅名、地域名など"
                    className="border-gray-200 text-sm focus:border-gray-400"
                  />
                </div>
              )}
            </div>

            {formData.living_area && (
              <div className="mt-2 rounded border border-blue-200 bg-blue-50 p-2">
                <p className="text-xs text-blue-700">
                  <strong>設定エリア:</strong> {formData.living_area.replace(/-/g, ' ')}
                </p>
              </div>
            )}
          </div>

          {/* 家族構成 */}
          <div className="space-y-3">
            <Label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Users className="h-4 w-4" />
              家族構成
            </Label>

            <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <div className="mb-3 grid grid-cols-2 gap-3 md:grid-cols-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="has_father"
                    checked={formData.family_members.has_father}
                    onCheckedChange={checked => updateFamilyMember('has_father', checked)}
                  />
                  <Label htmlFor="has_father" className="text-sm">
                    パパ
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="has_mother"
                    checked={formData.family_members.has_mother}
                    onCheckedChange={checked => updateFamilyMember('has_mother', checked)}
                  />
                  <Label htmlFor="has_mother" className="text-sm">
                    ママ
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="has_grandfather"
                    checked={formData.family_members.has_grandfather}
                    onCheckedChange={checked => updateFamilyMember('has_grandfather', checked)}
                  />
                  <Label htmlFor="has_grandfather" className="text-sm">
                    おじいちゃん
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="has_grandmother"
                    checked={formData.family_members.has_grandmother}
                    onCheckedChange={checked => updateFamilyMember('has_grandmother', checked)}
                  />
                  <Label htmlFor="has_grandmother" className="text-sm">
                    おばあちゃん
                  </Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="has_pets"
                    checked={formData.family_members.has_pets}
                    onCheckedChange={checked => updateFamilyMember('has_pets', checked)}
                  />
                  <Label htmlFor="has_pets" className="text-sm">
                    ペット
                  </Label>
                </div>

                <div className="col-span-2 space-y-2 md:col-span-3">
                  <Label className="text-sm">子どもの人数</Label>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        updateFamilyMember(
                          'children_count',
                          Math.max(0, formData.family_members.children_count - 1)
                        )
                      }
                      disabled={formData.family_members.children_count <= 0}
                    >
                      -
                    </Button>
                    <span className="rounded border bg-white px-4 py-2">
                      {formData.family_members.children_count}人
                    </span>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        updateFamilyMember(
                          'children_count',
                          formData.family_members.children_count + 1
                        )
                      }
                    >
                      +
                    </Button>
                  </div>
                </div>
              </div>

              <div className="col-span-2 mt-3 rounded border border-gray-300 bg-white p-2 md:col-span-3">
                <div className="mb-1 text-sm text-gray-600">家族構成プレビュー:</div>
                <Badge variant="outline" className="border-gray-400 bg-white text-gray-700">
                  {getFamilyStructureDescription()}
                </Badge>
              </div>
            </div>
          </div>

          {/* 子どもの詳細情報 */}
          {formData.family_members.children_count > 0 && (
            <div className="space-y-4">
              <Label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Baby className="h-4 w-4" />
                お子さんの情報
              </Label>

              {formData.children.map((child, index) => (
                <div key={index} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <h4 className="mb-3 font-medium text-gray-800">{index + 1}人目のお子さん</h4>

                  <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-3">
                    <div className="space-y-2">
                      <Label className="text-sm">お名前</Label>
                      <Input
                        value={child.name}
                        onChange={e => updateChild(index, 'name', e.target.value)}
                        placeholder="例: 太郎"
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm">性別</Label>
                      <select
                        value={child.gender}
                        onChange={e => updateChild(index, 'gender', e.target.value)}
                        className="w-full rounded-md border border-gray-200 px-3 py-2 focus:border-gray-400"
                      >
                        <option value="">選択してください</option>
                        <option value="male">男の子</option>
                        <option value="female">女の子</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <Label className="flex items-center gap-1 text-sm">
                        <Calendar className="h-3 w-3" />
                        生年月日
                      </Label>
                      <Input
                        type="date"
                        value={child.birth_date}
                        onChange={e => updateChild(index, 'birth_date', e.target.value)}
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>
                  </div>

                  <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label className="text-sm">アレルギー・注意点</Label>
                      <Textarea
                        value={child.allergies}
                        onChange={e => updateChild(index, 'allergies', e.target.value)}
                        placeholder="食物アレルギー、薬物アレルギーなど"
                        rows={2}
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm">性格・特徴</Label>
                      <Textarea
                        value={child.characteristics}
                        onChange={e => updateChild(index, 'characteristics', e.target.value)}
                        placeholder="活発、人見知り、好きなことなど"
                        rows={2}
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>
                  </div>

                  {/* 子どもごとの悩み・相談事 */}
                  <div className="mt-4">
                    <Label className="mb-3 block text-sm font-medium text-gray-700">
                      {child.name || `${index + 1}人目のお子さん`}の悩み・相談事（任意）
                    </Label>
                    <div className="rounded-lg border border-gray-200 bg-white p-3">
                      <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                        {[
                          '睡眠の悩み',
                          '食事の好き嫌い',
                          '発達について',
                          'イヤイヤ期',
                          'おむつ・トイレ',
                          '言葉の発達',
                          '運動発達',
                          '人見知り',
                          '夜泣き',
                          '癇癪',
                          '兄弟げんか',
                          '習い事選び',
                          '保育園・幼稚園',
                          '友達関係',
                          'しつけ・マナー',
                          'その他',
                        ].map(concern => (
                          <div key={concern} className="flex items-center space-x-2">
                            <Checkbox
                              id={`child_${index}_concern_${concern}`}
                              checked={child.concerns?.includes(concern) || false}
                              onCheckedChange={checked => {
                                const currentConcerns = child.concerns || []
                                if (checked) {
                                  updateChild(index, 'concerns', [...currentConcerns, concern])
                                } else {
                                  updateChild(
                                    index,
                                    'concerns',
                                    currentConcerns.filter(c => c !== concern)
                                  )
                                }
                              }}
                            />
                            <Label
                              htmlFor={`child_${index}_concern_${concern}`}
                              className="text-xs text-gray-700"
                            >
                              {concern}
                            </Label>
                          </div>
                        ))}
                      </div>

                      {child.concerns && child.concerns.length > 0 && (
                        <div className="mt-2 rounded border border-gray-200 bg-gray-50 p-2">
                          <div className="flex flex-wrap gap-1">
                            {child.concerns.map((concern, cIndex) => (
                              <Badge
                                key={cIndex}
                                variant="outline"
                                className="border-gray-400 text-xs text-gray-600"
                              >
                                {concern}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ペット情報 */}
          {formData.family_members.has_pets && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <FaPaw className="h-4 w-4" />
                  ペット情報
                </Label>
                <Button
                  type="button"
                  onClick={addPet}
                  size="sm"
                  variant="outline"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  <Plus className="mr-1 h-4 w-4" />
                  ペット追加
                </Button>
              </div>

              {formData.pets.map((pet, index) => (
                <div key={index} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <h4 className="font-medium text-gray-800">ペット {index + 1}</h4>
                    <Button
                      type="button"
                      onClick={() => removePet(index)}
                      size="sm"
                      variant="ghost"
                      className="text-red-600 hover:bg-red-50"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    <div className="space-y-2">
                      <Label className="text-sm">名前</Label>
                      <Input
                        value={pet.name}
                        onChange={e => updatePet(index, 'name', e.target.value)}
                        placeholder="例: ポチ"
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm">種類</Label>
                      <select
                        value={pet.type}
                        onChange={e =>
                          updatePet(index, 'type', e.target.value as 'dog' | 'cat' | 'other')
                        }
                        className="w-full rounded-md border border-gray-200 px-3 py-2 focus:border-gray-400"
                      >
                        <option value="dog">犬</option>
                        <option value="cat">猫</option>
                        <option value="other">その他</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-sm">年齢</Label>
                      <Input
                        value={pet.age}
                        onChange={e => updatePet(index, 'age', e.target.value)}
                        placeholder="例: 3歳"
                        className="border-gray-200 focus:border-gray-400"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

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
              className="flex-1 bg-gradient-to-r from-gray-600 to-gray-700 text-white hover:from-gray-700 hover:to-gray-800"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  {familyData ? '更新する' : '登録する'}
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
