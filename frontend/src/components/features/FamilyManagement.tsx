/**
 * 家族情報管理コンポーネント
 * CRUD操作を提供する統合UI
 */

'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { AlertCircle, Plus, Trash2, Edit, Users, Baby, Heart, Clock } from 'lucide-react'
import { FaBirthdayCake, FaAllergies, FaStethoscope } from 'react-icons/fa'
import { MdChildCare, MdFamilyRestroom } from 'react-icons/md'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import {
  getFamilyInfo,
  registerFamilyInfo,
  updateFamilyInfo,
  deleteFamilyInfo as deleteFamilyInfoAPI,
} from '@/libs/api/family'

interface Child {
  name: string
  age: string
  gender: string
  birth_date: string
  characteristics: string
  allergies: string
  medical_notes: string
}

interface FamilyInfo {
  family_id?: string
  user_id?: string
  parent_name: string
  family_structure: string
  concerns: string
  children: Child[]
  created_at?: string
  updated_at?: string
}

const FAMILY_STRUCTURE_OPTIONS = [
  { value: 'single_parent_1child', label: 'ひとり親+子ども1人' },
  { value: 'single_parent_2children', label: 'ひとり親+子ども2人' },
  { value: 'single_parent_3children', label: 'ひとり親+子ども3人以上' },
  { value: 'couple_1child', label: '夫婦+子ども1人' },
  { value: 'couple_2children', label: '夫婦+子ども2人' },
  { value: 'couple_3children', label: '夫婦+子ども3人以上' },
  { value: 'extended_family', label: '三世代同居（祖父母同居）' },
  { value: 'other', label: 'その他' },
]

export default function FamilyManagement() {
  const [familyInfo, setFamilyInfo] = useState<FamilyInfo>({
    parent_name: '',
    family_structure: '',
    concerns: '',
    children: [],
  })

  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [hasExistingData, setHasExistingData] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  // 初期データ読み込み
  useEffect(() => {
    loadFamilyInfo()
  }, [])

  // 年齢計算関数
  const calculateAge = (birthDate: string) => {
    if (!birthDate) return ''
    const birth = new Date(birthDate)
    const today = new Date()
    const months =
      (today.getFullYear() - birth.getFullYear()) * 12 + today.getMonth() - birth.getMonth()

    if (months < 12) {
      return `${months}ヶ月`
    } else {
      const years = Math.floor(months / 12)
      const remainingMonths = months % 12
      return remainingMonths > 0 ? `${years}歳${remainingMonths}ヶ月` : `${years}歳`
    }
  }

  // 子どもの人数とアレルギー情報をサマリー
  const getChildrenSummary = () => {
    const childrenCount = familyInfo.children.length
    const allergiesCount = familyInfo.children.filter(
      child => child.allergies && child.allergies.trim() !== ''
    ).length
    return { childrenCount, allergiesCount }
  }

  const loadFamilyInfo = async () => {
    try {
      setIsLoading(true)
      setMessage(null)

      const result = await getFamilyInfo('frontend_user')
      console.log('家族情報読み込み結果:', result)

      if (result.success && result.data) {
        setFamilyInfo(result.data)
        setHasExistingData(true)
        setIsEditing(false)
      } else {
        setFamilyInfo({
          parent_name: '',
          family_structure: '',
          concerns: '',
          children: [],
        })
        setHasExistingData(false)
        setIsEditing(true)
      }
    } catch (error) {
      console.error('家族情報の読み込みエラー:', error)
      setMessage({
        type: 'error',
        text: `家族情報の読み込みに失敗しました: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
      setHasExistingData(false)
      setIsEditing(true)
    } finally {
      setIsLoading(false)
    }
  }

  const saveFamilyInfo = async () => {
    try {
      setIsLoading(true)
      setMessage(null)

      const familyData = {
        parent_name: familyInfo.parent_name,
        family_structure: familyInfo.family_structure,
        concerns: familyInfo.concerns,
        children: familyInfo.children,
      }

      console.log('送信データ:', familyData)

      const result = hasExistingData
        ? await updateFamilyInfo(familyData, 'frontend_user')
        : await registerFamilyInfo(familyData, 'frontend_user')

      console.log('API応答:', result)

      if (result.success) {
        setMessage({
          type: 'success',
          text: hasExistingData ? '家族情報を更新しました' : '家族情報を登録しました',
        })
        setHasExistingData(true)
        setIsEditing(false)
        await loadFamilyInfo()
      } else {
        setMessage({ type: 'error', text: result.error || result.message || '保存に失敗しました' })
      }
    } catch (error) {
      console.error('保存エラー:', error)
      setMessage({
        type: 'error',
        text: `保存中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const deleteFamilyInfo = async () => {
    if (!confirm('家族情報を削除してもよろしいですか？この操作は取り消せません。')) {
      return
    }

    try {
      setIsLoading(true)
      setMessage(null)

      const result = await deleteFamilyInfoAPI('frontend_user')
      console.log('削除結果:', result)

      if (result.success) {
        setMessage({ type: 'success', text: '家族情報を削除しました' })
        setFamilyInfo({
          parent_name: '',
          family_structure: '',
          concerns: '',
          children: [],
        })
        setHasExistingData(false)
        setIsEditing(true)
      } else {
        setMessage({ type: 'error', text: result.error || result.message || '削除に失敗しました' })
      }
    } catch (error) {
      console.error('削除エラー:', error)
      setMessage({
        type: 'error',
        text: `削除中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const addChild = () => {
    setFamilyInfo(prev => ({
      ...prev,
      children: [
        ...prev.children,
        {
          name: '',
          age: '',
          gender: '',
          birth_date: '',
          characteristics: '',
          allergies: '',
          medical_notes: '',
        },
      ],
    }))
  }

  const removeChild = (index: number) => {
    setFamilyInfo(prev => ({
      ...prev,
      children: prev.children.filter((_, i) => i !== index),
    }))
  }

  const updateChild = (index: number, field: keyof Child, value: string) => {
    setFamilyInfo(prev => ({
      ...prev,
      children: prev.children.map((child, i) =>
        i === index ? { ...child, [field]: value } : child
      ),
    }))
  }

  if (isLoading) {
    return <LoadingSpinner message="家族情報を読み込んでいます..." />
  }

  const { childrenCount, allergiesCount } = getChildrenSummary()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ページヘッダー */}
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-600 shadow-sm">
                <MdFamilyRestroom className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">家族情報</h1>
                <p className="text-gray-600">あなたの大切な家族を管理・記録します</p>
              </div>
            </div>

            <div className="flex space-x-3">
              <Button
                onClick={() => setIsEditing(true)}
                className="bg-gray-700 text-white shadow-sm hover:bg-gray-800"
              >
                <Plus className="mr-2 h-4 w-4" />
                {hasExistingData ? '新規追加' : '新規登録'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl space-y-8 p-6">
        {/* 家族サマリーカード */}
        {hasExistingData && (
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
            <Card className="border border-gray-200 bg-gradient-to-br from-white to-gray-50 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">家族構成</p>
                    <p className="mt-1 text-2xl font-bold text-gray-900">
                      {FAMILY_STRUCTURE_OPTIONS.find(
                        option => option.value === familyInfo.family_structure
                      )?.label ||
                        familyInfo.family_structure ||
                        '未設定'}
                    </p>
                  </div>
                  <MdFamilyRestroom className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-gradient-to-br from-white to-gray-50 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">お子さん</p>
                    <p className="mt-1 text-2xl font-bold text-gray-900">{childrenCount}人</p>
                  </div>
                  <MdChildCare className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-gradient-to-br from-white to-gray-50 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">アレルギー</p>
                    <p className="mt-1 text-2xl font-bold text-gray-900">{allergiesCount}件</p>
                  </div>
                  <FaAllergies className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border border-gray-200 bg-gradient-to-br from-white to-gray-50 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">最終更新</p>
                    <p className="mt-1 text-2xl font-bold text-gray-900">
                      {familyInfo.updated_at
                        ? new Date(familyInfo.updated_at).toLocaleDateString('ja-JP', {
                            month: 'short',
                            day: 'numeric',
                          })
                        : '今日'}
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* メッセージ表示 */}
        {message && (
          <Card
            className={`mb-6 ${message.type === 'error' ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'} shadow-lg`}
          >
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertCircle
                  className={`h-5 w-5 ${message.type === 'error' ? 'text-red-600' : 'text-green-600'}`}
                />
                <p
                  className={`text-sm font-medium ${message.type === 'error' ? 'text-red-700' : 'text-green-700'}`}
                >
                  {message.text}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 基本情報カード */}
        <Card className="border border-gray-200 bg-white shadow-sm">
          <CardHeader className="border-b border-gray-200 bg-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-3 text-gray-800">
                  <Users className="h-6 w-6 text-gray-600" />
                  基本情報
                </CardTitle>
                <CardDescription className="text-gray-600">
                  ご家族の基本的な情報を入力してください
                </CardDescription>
              </div>
              {hasExistingData && !isEditing && (
                <div className="flex space-x-2">
                  <Button
                    onClick={() => setIsEditing(true)}
                    variant="outline"
                    size="sm"
                    className="border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    <Edit className="mr-1 h-4 w-4" />
                    編集
                  </Button>
                  <Button
                    onClick={deleteFamilyInfo}
                    variant="destructive"
                    size="sm"
                    className="bg-red-500 hover:bg-red-600"
                  >
                    <Trash2 className="mr-1 h-4 w-4" />
                    削除
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div>
              <Label htmlFor="parent_name">保護者名</Label>
              <Input
                id="parent_name"
                value={familyInfo.parent_name}
                onChange={e => setFamilyInfo(prev => ({ ...prev, parent_name: e.target.value }))}
                placeholder="田中太郎"
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="family_structure">家族構成</Label>
              <Select
                value={familyInfo.family_structure}
                onValueChange={value =>
                  setFamilyInfo(prev => ({ ...prev, family_structure: value }))
                }
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue placeholder="家族構成を選択してください" />
                </SelectTrigger>
                <SelectContent>
                  {FAMILY_STRUCTURE_OPTIONS.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="concerns">主な心配事・相談したいこと</Label>
              <Textarea
                id="concerns"
                value={familyInfo.concerns}
                onChange={e => setFamilyInfo(prev => ({ ...prev, concerns: e.target.value }))}
                placeholder="離乳食の進め方が心配、夜泣きが続いている など"
                rows={3}
                disabled={!isEditing}
              />
            </div>
          </CardContent>
        </Card>

        {/* 子どもの情報カード */}
        <Card className="border border-gray-200 bg-white shadow-sm">
          <CardHeader className="border-b border-gray-200 bg-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-3 text-gray-800">
                  <Baby className="h-6 w-6 text-gray-600" />
                  お子さんの情報
                </CardTitle>
                <CardDescription className="text-gray-600">
                  お子さんそれぞれの詳しい情報を入力してください
                </CardDescription>
              </div>
              {isEditing && (
                <Button
                  onClick={addChild}
                  className="bg-gray-600 text-white hover:bg-gray-700"
                  size="sm"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  子どもを追加
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="p-6">
            {familyInfo.children.length === 0 ? (
              <p className="py-8 text-center text-gray-500">
                まだお子さんの情報が登録されていません
                {isEditing && <br />}
                {isEditing && '「子どもを追加」ボタンから登録してください'}
              </p>
            ) : (
              <div className="space-y-6">
                {familyInfo.children.map((child, index) => (
                  <Card
                    key={index}
                    className="border border-gray-200 bg-white shadow-sm transition-all duration-300 hover:shadow-md"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-500 text-lg font-bold text-white shadow-sm">
                            {child.name ? child.name.charAt(0) : '👶'}
                          </div>
                          <div>
                            <h4 className="text-lg font-bold text-gray-800">
                              {child.name || `お子さん ${index + 1}`}
                            </h4>
                            {child.age && (
                              <p className="flex items-center gap-1 text-sm text-gray-600">
                                <FaBirthdayCake className="h-3 w-3" />
                                {child.age}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {child.birth_date && (
                            <Badge className="bg-gray-600 text-white">
                              {calculateAge(child.birth_date)}
                            </Badge>
                          )}
                          {child.allergies && child.allergies.trim() !== '' && (
                            <Badge className="bg-red-500 text-white">
                              <FaAllergies className="mr-1 h-3 w-3" />
                              アレルギー
                            </Badge>
                          )}
                          {isEditing && (
                            <Button
                              onClick={() => removeChild(index)}
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:bg-red-50 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div>
                          <Label>お名前</Label>
                          <Input
                            value={child.name}
                            onChange={e => updateChild(index, 'name', e.target.value)}
                            placeholder="田中花子"
                            disabled={!isEditing}
                          />
                        </div>

                        <div>
                          <Label>年齢（自動計算）</Label>
                          <Input
                            value={
                              child.birth_date
                                ? calculateAge(child.birth_date)
                                : '生年月日を入力してください'
                            }
                            disabled={true}
                            className="bg-gray-50 text-gray-600"
                          />
                        </div>

                        <div>
                          <Label>性別</Label>
                          <Input
                            value={child.gender}
                            onChange={e => updateChild(index, 'gender', e.target.value)}
                            placeholder="女の子"
                            disabled={!isEditing}
                          />
                        </div>

                        <div>
                          <Label>生年月日</Label>
                          <Input
                            value={child.birth_date}
                            onChange={e => updateChild(index, 'birth_date', e.target.value)}
                            placeholder="2024-04-01"
                            type="date"
                            disabled={!isEditing}
                          />
                        </div>
                      </div>

                      <div className="mt-6 space-y-4">
                        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                          <Label className="mb-2 flex items-center gap-2 font-semibold text-gray-800">
                            <Heart className="h-4 w-4" />
                            特徴・性格
                          </Label>
                          <Textarea
                            value={child.characteristics}
                            onChange={e => updateChild(index, 'characteristics', e.target.value)}
                            placeholder="人見知りが激しい、よく笑う、活発で元気 など"
                            rows={2}
                            disabled={!isEditing}
                            className="border-gray-300 bg-white focus:border-gray-500"
                          />
                        </div>

                        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                          <Label className="mb-2 flex items-center gap-2 font-semibold text-red-800">
                            <FaAllergies className="h-4 w-4" />
                            アレルギー情報
                          </Label>
                          <Input
                            value={child.allergies}
                            onChange={e => updateChild(index, 'allergies', e.target.value)}
                            placeholder="卵、牛乳、小麦 など（なしの場合は空欄）"
                            disabled={!isEditing}
                            className="border-red-300 bg-white focus:border-red-500"
                          />
                        </div>

                        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                          <Label className="mb-2 flex items-center gap-2 font-semibold text-green-800">
                            <FaStethoscope className="h-4 w-4" />
                            健康・医療メモ
                          </Label>
                          <Textarea
                            value={child.medical_notes}
                            onChange={e => updateChild(index, 'medical_notes', e.target.value)}
                            placeholder="予防接種の状況、通院歴、気になる症状、かかりつけ医 など"
                            rows={2}
                            disabled={!isEditing}
                            className="border-green-300 bg-white focus:border-green-500"
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>

          {isEditing && (
            <CardFooter className="flex justify-end space-x-2">
              {hasExistingData && (
                <Button onClick={() => setIsEditing(false)} variant="outline">
                  キャンセル
                </Button>
              )}
              <Button onClick={saveFamilyInfo} disabled={isLoading}>
                {isLoading ? '保存中...' : hasExistingData ? '更新' : '登録'}
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  )
}
