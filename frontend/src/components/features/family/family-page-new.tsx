'use client'

import React, { useState, useEffect } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Users,
  Plus,
  Edit,
  Baby,
  Heart,
  Calendar,
  MapPin,
  Phone,
  Mail,
  Home,
  Shield
} from 'lucide-react'
import { FaPaw, FaAllergies } from 'react-icons/fa'
import { MdFamilyRestroom, MdChildCare } from 'react-icons/md'
import { FamilyCompositionModal } from './family-composition-modal'
import { getFamilyInfo, registerFamilyInfo, updateFamilyInfo } from '@/lib/api/family'

interface Child {
  name: string
  age: string
  gender: string
  birth_date: string
  characteristics: string
  allergies: string
  medical_notes: string
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
    has_grandparents: boolean
    children_count: number
    has_pets: boolean
  }
  pets: Pet[]
  children: Child[]
  concerns: string
  living_situation: string
}

// APIデータとの変換用
interface ApiFamilyInfo {
  family_id?: string
  user_id?: string
  parent_name: string
  family_structure: string
  concerns: string
  children: Child[]
  created_at?: string
  updated_at?: string
}

export default function FamilyPageNew() {
  const [familyData, setFamilyData] = useState<FamilyComposition | null>(null)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [hasData, setHasData] = useState(false)

  useEffect(() => {
    loadFamilyData()
  }, [])

  const loadFamilyData = async () => {
    try {
      setLoading(true)
      const result = await getFamilyInfo('frontend_user')
      
      if (result.success && result.data) {
        // APIデータからFamilyComposition形式に変換
        const apiData = result.data as ApiFamilyInfo
        const convertedData: FamilyComposition = {
          parent_name: apiData.parent_name,
          family_members: {
            has_father: apiData.family_structure.includes('夫婦') || apiData.family_structure.includes('パパ'),
            has_mother: apiData.family_structure.includes('夫婦') || apiData.family_structure.includes('ママ'),
            has_grandparents: apiData.family_structure.includes('三世代') || apiData.family_structure.includes('祖父母'),
            children_count: apiData.children.length,
            has_pets: false // 既存データではペット情報がないため
          },
          pets: [], // 既存データではペット情報がないため
          children: apiData.children,
          concerns: apiData.concerns,
          living_situation: ''
        }
        setFamilyData(convertedData)
        setHasData(true)
      } else {
        setHasData(false)
      }
    } catch (error) {
      console.error('家族情報読み込みエラー:', error)
      setHasData(false)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (data: FamilyComposition) => {
    try {
      // FamilyComposition形式からAPI形式に変換
      const apiData = {
        parent_name: data.parent_name,
        family_structure: generateFamilyStructureString(data.family_members),
        concerns: data.concerns,
        children: data.children
      }

      const result = hasData 
        ? await updateFamilyInfo(apiData, 'frontend_user')
        : await registerFamilyInfo(apiData, 'frontend_user')

      if (result.success) {
        setFamilyData(data)
        setHasData(true)
        alert(hasData ? '家族情報を更新しました' : '家族情報を登録しました')
      } else {
        throw new Error(result.message || '保存に失敗しました')
      }
    } catch (error) {
      console.error('家族情報保存エラー:', error)
      throw error
    }
  }

  const generateFamilyStructureString = (members: FamilyComposition['family_members']) => {
    const parts = []
    if (members.has_father && members.has_mother) {
      parts.push('夫婦')
    } else if (members.has_father || members.has_mother) {
      parts.push('ひとり親')
    }
    
    if (members.children_count > 0) {
      parts.push(`子ども${members.children_count}人`)
    }
    
    if (members.has_grandparents) {
      parts.push('三世代同居')
    }
    
    return parts.join('+') || 'その他'
  }

  const calculateAge = (birthDate: string) => {
    if (!birthDate) return ''
    const birth = new Date(birthDate)
    const today = new Date()
    const months = (today.getFullYear() - birth.getFullYear()) * 12 + today.getMonth() - birth.getMonth()
    
    if (months < 12) {
      return `${months}ヶ月`
    } else {
      const years = Math.floor(months / 12)
      const remainingMonths = months % 12
      return remainingMonths > 0 ? `${years}歳${remainingMonths}ヶ月` : `${years}歳`
    }
  }

  const getFamilyStructureDisplay = () => {
    if (!familyData) return ''
    
    const members = []
    if (familyData.family_members.has_father) members.push('パパ')
    if (familyData.family_members.has_mother) members.push('ママ')
    if (familyData.family_members.children_count > 0) {
      members.push(`子ども${familyData.family_members.children_count}人`)
    }
    if (familyData.family_members.has_grandparents) members.push('おじいちゃん・おばあちゃん')
    if (familyData.family_members.has_pets && familyData.pets.length > 0) {
      members.push(`ペット${familyData.pets.length}匹`)
    }
    
    return members.join(' + ')
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 flex items-center justify-center">
          <div className="inline-flex items-center gap-2">
            <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-gray-600">家族情報を読み込み中...</span>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
        {/* ページヘッダー */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-emerald-100">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-lg">
                  <MdFamilyRestroom className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">家族情報</h1>
                  <p className="text-gray-600">ご家族の構成やお子さんの情報を管理します</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Button 
                  onClick={() => setShowModal(true)}
                  className="bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white shadow-lg"
                >
                  {hasData ? (
                    <>
                      <Edit className="h-4 w-4 mr-2" />
                      編集
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4 mr-2" />
                      家族情報を登録
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-6 space-y-8">
          {!hasData ? (
            // 未登録時の案内
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardContent className="p-12 text-center">
                <div className="mb-6">
                  <MdFamilyRestroom className="h-24 w-24 mx-auto text-emerald-300" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  家族情報をご登録ください
                </h3>
                <p className="text-gray-600 mb-8 max-w-md mx-auto">
                  ご家族の構成やお子さんの情報を登録していただくことで、
                  よりパーソナライズされたサポートを提供できます。
                </p>
                <Button 
                  onClick={() => setShowModal(true)}
                  size="lg"
                  className="bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white shadow-lg"
                >
                  <Plus className="h-5 w-5 mr-2" />
                  家族情報を登録する
                </Button>
              </CardContent>
            </Card>
          ) : (
            // 登録済み時の表示
            <>
              {/* 家族構成サマリー */}
              <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                <CardHeader className="bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-t-lg">
                  <CardTitle className="flex items-center gap-3">
                    <Users className="h-6 w-6" />
                    家族構成
                  </CardTitle>
                  <CardDescription className="text-emerald-100">
                    {familyData?.parent_name}さんのご家族
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-lg font-medium text-gray-800">
                      {getFamilyStructureDisplay()}
                    </div>
                    <Badge className="bg-emerald-100 text-emerald-700 border-emerald-300">
                      {familyData?.family_members.children_count}人のお子さん
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    <div className="text-center p-4 bg-emerald-50 rounded-lg">
                      <Users className="h-8 w-8 mx-auto text-emerald-600 mb-2" />
                      <div className="text-sm text-gray-600">保護者</div>
                      <div className="font-medium">
                        {(familyData?.family_members.has_father && familyData?.family_members.has_mother) ? '2人' :
                         (familyData?.family_members.has_father || familyData?.family_members.has_mother) ? '1人' : '0人'}
                      </div>
                    </div>
                    
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <Baby className="h-8 w-8 mx-auto text-blue-600 mb-2" />
                      <div className="text-sm text-gray-600">お子さん</div>
                      <div className="font-medium">{familyData?.family_members.children_count}人</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <Heart className="h-8 w-8 mx-auto text-purple-600 mb-2" />
                      <div className="text-sm text-gray-600">祖父母</div>
                      <div className="font-medium">
                        {familyData?.family_members.has_grandparents ? '同居' : '別居'}
                      </div>
                    </div>
                    
                    <div className="text-center p-4 bg-amber-50 rounded-lg">
                      <FaPaw className="h-8 w-8 mx-auto text-amber-600 mb-2" />
                      <div className="text-sm text-gray-600">ペット</div>
                      <div className="font-medium">
                        {familyData?.pets.length || 0}匹
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 子どもの詳細情報 */}
              {familyData?.children && familyData.children.length > 0 && (
                <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-t-lg">
                    <CardTitle className="flex items-center gap-3">
                      <MdChildCare className="h-6 w-6" />
                      お子さんの情報
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {familyData.children.map((child, index) => (
                        <div key={index} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-bold text-blue-800 flex items-center gap-2">
                              <Baby className="h-5 w-5" />
                              {child.name}
                            </h4>
                            <Badge variant="outline" className="text-blue-700 border-blue-300">
                              {child.gender === 'male' ? '男の子' : child.gender === 'female' ? '女の子' : ''}
                            </Badge>
                          </div>
                          
                          <div className="space-y-2 text-sm">
                            {child.birth_date && (
                              <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-blue-600" />
                                <span>{child.birth_date} ({calculateAge(child.birth_date)})</span>
                              </div>
                            )}
                            
                            {child.characteristics && (
                              <div>
                                <div className="font-medium text-blue-700 mb-1">性格・特徴</div>
                                <div className="text-gray-700">{child.characteristics}</div>
                              </div>
                            )}
                            
                            {child.allergies && (
                              <div className="bg-red-50 p-2 rounded border border-red-200">
                                <div className="font-medium text-red-700 mb-1 flex items-center gap-1">
                                  <FaAllergies className="h-3 w-3" />
                                  アレルギー・注意点
                                </div>
                                <div className="text-red-600 text-xs">{child.allergies}</div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* ペット情報 */}
              {familyData?.pets && familyData.pets.length > 0 && (
                <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-t-lg">
                    <CardTitle className="flex items-center gap-3">
                      <FaPaw className="h-6 w-6" />
                      ペット情報
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {familyData.pets.map((pet, index) => (
                        <div key={index} className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                          <h4 className="font-bold text-amber-800 mb-2">{pet.name}</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex items-center gap-2">
                              <FaPaw className="h-3 w-3 text-amber-600" />
                              <span>
                                {pet.type === 'dog' ? '犬' : pet.type === 'cat' ? '猫' : 'その他'}
                                {pet.age && ` (${pet.age})`}
                              </span>
                            </div>
                            {pet.characteristics && (
                              <div className="text-gray-700">{pet.characteristics}</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* 相談事・悩み */}
              {familyData?.concerns && (
                <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                  <CardHeader className="bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-t-lg">
                    <CardTitle className="flex items-center gap-3">
                      <Heart className="h-6 w-6" />
                      子育ての悩み・相談事
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="bg-pink-50 p-4 rounded-lg border border-pink-200">
                      <p className="text-gray-700">{familyData.concerns}</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>

      {/* 家族情報編集モーダル */}
      <FamilyCompositionModal
        open={showModal}
        onOpenChange={setShowModal}
        familyData={familyData}
        onSave={handleSave}
      />
    </AppLayout>
  )
}