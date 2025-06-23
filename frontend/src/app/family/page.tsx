'use client'

import { useState } from 'react'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import {
  HiOutlineUsers,
  HiOutlinePlus,
  HiOutlinePencil,
  HiOutlineTrash,
  HiOutlineHeart,
  HiOutlineCake,
  HiOutlineUser
} from 'react-icons/hi2'
import { 
  FaBaby,
  FaChild,
  FaUserTie
} from 'react-icons/fa'

interface FamilyMember {
  id: string
  name: string
  relationship: string
  birthDate: string
  gender: string
  notes?: string
  avatar?: string
}

export default function FamilyPage() {
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([
    {
      id: '1',
      name: 'さくらちゃん',
      relationship: '子ども',
      birthDate: '2023-03-15',
      gender: '女の子',
      notes: '離乳食を開始しました'
    }
  ])
  
  const [isAddingMember, setIsAddingMember] = useState(false)
  const [editingMember, setEditingMember] = useState<FamilyMember | null>(null)
  const [newMember, setNewMember] = useState<Partial<FamilyMember>>({
    name: '',
    relationship: '',
    birthDate: '',
    gender: '',
    notes: ''
  })

  const calculateAge = (birthDate: string) => {
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

  const getRelationshipIcon = (relationship: string) => {
    switch (relationship) {
      case '子ども':
        return <FaBaby className="h-4 w-4" />
      case 'パパ':
      case 'ママ':
        return <FaUserTie className="h-4 w-4" />
      default:
        return <HiOutlineUser className="h-4 w-4" />
    }
  }

  const getAgeColor = (birthDate: string) => {
    const birth = new Date(birthDate)
    const today = new Date()
    const months = (today.getFullYear() - birth.getFullYear()) * 12 + today.getMonth() - birth.getMonth()
    
    if (months < 12) return 'bg-pink-100 text-pink-800'
    if (months < 36) return 'bg-blue-100 text-blue-800'
    return 'bg-green-100 text-green-800'
  }

  const handleAddMember = () => {
    if (newMember.name && newMember.relationship && newMember.birthDate && newMember.gender) {
      const member: FamilyMember = {
        id: Date.now().toString(),
        name: newMember.name,
        relationship: newMember.relationship,
        birthDate: newMember.birthDate,
        gender: newMember.gender,
        notes: newMember.notes || ''
      }
      setFamilyMembers([...familyMembers, member])
      setNewMember({ name: '', relationship: '', birthDate: '', gender: '', notes: '' })
      setIsAddingMember(false)
    }
  }

  const handleEditMember = (member: FamilyMember) => {
    setEditingMember(member)
    setNewMember(member)
    setIsAddingMember(true)
  }

  const handleUpdateMember = () => {
    if (editingMember && newMember.name && newMember.relationship && newMember.birthDate && newMember.gender) {
      const updatedMembers = familyMembers.map(member =>
        member.id === editingMember.id
          ? { ...member, ...newMember } as FamilyMember
          : member
      )
      setFamilyMembers(updatedMembers)
      setEditingMember(null)
      setNewMember({ name: '', relationship: '', birthDate: '', gender: '', notes: '' })
      setIsAddingMember(false)
    }
  }

  const handleDeleteMember = (id: string) => {
    setFamilyMembers(familyMembers.filter(member => member.id !== id))
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-slate-50">
        {/* ページヘッダー */}
        <div className="bg-white">
          <div className="px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                  <HiOutlineUsers className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-heading font-semibold text-gray-800">家族情報</h1>
                  <p className="text-sm text-blue-600">ご家族の情報を管理します</p>
                </div>
              </div>
              <Button
                onClick={() => setIsAddingMember(true)}
                className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
              >
                <HiOutlinePlus className="h-4 w-4 mr-2" />
                家族を追加
              </Button>
            </div>
          </div>
        </div>

        <div className="px-4 py-6">
          {/* 家族メンバー一覧 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {familyMembers.map((member) => (
              <Card key={member.id} className="bg-white hover:shadow-lg transition-all duration-200">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center">
                        {getRelationshipIcon(member.relationship)}
                      </div>
                      <div>
                        <CardTitle className="text-lg text-gray-800">{member.name}</CardTitle>
                        <p className="text-sm text-gray-600">{member.relationship}</p>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditMember(member)}
                        className="h-8 w-8 p-0"
                      >
                        <HiOutlinePencil className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteMember(member.id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                      >
                        <HiOutlineTrash className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <HiOutlineCake className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-600">
                        {new Date(member.birthDate).toLocaleDateString('ja-JP')}
                      </span>
                      <Badge className={getAgeColor(member.birthDate)}>
                        {calculateAge(member.birthDate)}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <HiOutlineHeart className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-600">{member.gender}</span>
                    </div>
                    
                    {member.notes && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-blue-800">{member.notes}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* 家族追加・編集フォーム */}
          {isAddingMember && (
            <Card className="bg-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HiOutlinePlus className="h-5 w-5" />
                  {editingMember ? '家族情報を編集' : '新しい家族を追加'}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">お名前</Label>
                    <Input
                      id="name"
                      value={newMember.name || ''}
                      onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
                      placeholder="例: さくらちゃん"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="relationship">続柄</Label>
                    <Select value={newMember.relationship || ''} onValueChange={(value) => setNewMember({ ...newMember, relationship: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="続柄を選択" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="子ども">子ども</SelectItem>
                        <SelectItem value="パパ">パパ</SelectItem>
                        <SelectItem value="ママ">ママ</SelectItem>
                        <SelectItem value="おじいちゃん">おじいちゃん</SelectItem>
                        <SelectItem value="おばあちゃん">おばあちゃん</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="birthDate">生年月日</Label>
                    <Input
                      id="birthDate"
                      type="date"
                      value={newMember.birthDate || ''}
                      onChange={(e) => setNewMember({ ...newMember, birthDate: e.target.value })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="gender">性別</Label>
                    <Select value={newMember.gender || ''} onValueChange={(value) => setNewMember({ ...newMember, gender: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="性別を選択" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="男の子">男の子</SelectItem>
                        <SelectItem value="女の子">女の子</SelectItem>
                        <SelectItem value="男性">男性</SelectItem>
                        <SelectItem value="女性">女性</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="notes">メモ（任意）</Label>
                  <Textarea
                    id="notes"
                    value={newMember.notes || ''}
                    onChange={(e) => setNewMember({ ...newMember, notes: e.target.value })}
                    placeholder="アレルギーや特記事項など"
                    rows={3}
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={editingMember ? handleUpdateMember : handleAddMember}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
                  >
                    {editingMember ? '更新' : '追加'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsAddingMember(false)
                      setEditingMember(null)
                      setNewMember({ name: '', relationship: '', birthDate: '', gender: '', notes: '' })
                    }}
                  >
                    キャンセル
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
          
          {familyMembers.length === 0 && !isAddingMember && (
            <Card className="bg-white">
              <CardContent className="p-8 text-center">
                <HiOutlineUsers className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-800 mb-2">まだ家族が登録されていません</h3>
                <p className="text-gray-600 mb-4">最初の家族を追加してみましょう</p>
                <Button
                  onClick={() => setIsAddingMember(true)}
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
                >
                  <HiOutlinePlus className="h-4 w-4 mr-2" />
                  家族を追加
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </AppLayout>
  )
}