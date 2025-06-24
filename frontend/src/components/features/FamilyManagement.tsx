/**
 * 家族情報管理コンポーネント
 * CRUD操作を提供する統合UI
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Plus, Trash2, Edit, Users, Baby, Heart, Sparkles, Clock } from 'lucide-react';
import { FaBirthdayCake, FaAllergies, FaStethoscope } from 'react-icons/fa';
import { MdChildCare, MdFamilyRestroom } from 'react-icons/md';
import Link from 'next/link';
import { getFamilyInfo, registerFamilyInfo, updateFamilyInfo, deleteFamilyInfo as deleteFamilyInfoAPI } from '@/lib/api/family';

interface Child {
  name: string;
  age: string;
  gender: string;
  birth_date: string;
  characteristics: string;
  allergies: string;
  medical_notes: string;
}

interface FamilyInfo {
  family_id?: string;
  user_id?: string;
  parent_name: string;
  family_structure: string;
  concerns: string;
  children: Child[];
  created_at?: string;
  updated_at?: string;
}

export default function FamilyManagement() {
  const [familyInfo, setFamilyInfo] = useState<FamilyInfo>({
    parent_name: '',
    family_structure: '',
    concerns: '',
    children: []
  });

  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [hasExistingData, setHasExistingData] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // 初期データ読み込み
  useEffect(() => {
    loadFamilyInfo();
  }, []);

  // 年齢計算関数
  const calculateAge = (birthDate: string) => {
    if (!birthDate) return '';
    const birth = new Date(birthDate);
    const today = new Date();
    const months = (today.getFullYear() - birth.getFullYear()) * 12 + today.getMonth() - birth.getMonth();
    
    if (months < 12) {
      return `${months}ヶ月`;
    } else {
      const years = Math.floor(months / 12);
      const remainingMonths = months % 12;
      return remainingMonths > 0 ? `${years}歳${remainingMonths}ヶ月` : `${years}歳`;
    }
  };

  // 子どもの人数とアレルギー情報をサマリー
  const getChildrenSummary = () => {
    const childrenCount = familyInfo.children.length;
    const allergiesCount = familyInfo.children.filter(child => child.allergies && child.allergies.trim() !== '').length;
    return { childrenCount, allergiesCount };
  };

  const loadFamilyInfo = async () => {
    try {
      setIsLoading(true);
      setMessage(null);
      
      const result = await getFamilyInfo('frontend_user');
      console.log('家族情報読み込み結果:', result);

      if (result.success && result.data) {
        setFamilyInfo(result.data);
        setHasExistingData(true);
        setIsEditing(false);
      } else {
        setFamilyInfo({
          parent_name: '',
          family_structure: '',
          concerns: '',
          children: []
        });
        setHasExistingData(false);
        setIsEditing(true);
      }
    } catch (error) {
      console.error('家族情報の読み込みエラー:', error);
      setMessage({ type: 'error', text: `家族情報の読み込みに失敗しました: ${error instanceof Error ? error.message : 'Unknown error'}` });
      setHasExistingData(false);
      setIsEditing(true);
    } finally {
      setIsLoading(false);
    }
  };

  const saveFamilyInfo = async () => {
    try {
      setIsLoading(true);
      setMessage(null);

      const familyData = {
        parent_name: familyInfo.parent_name,
        family_structure: familyInfo.family_structure,
        concerns: familyInfo.concerns,
        children: familyInfo.children,
      };

      console.log('送信データ:', familyData);

      const result = hasExistingData 
        ? await updateFamilyInfo(familyData, 'frontend_user')
        : await registerFamilyInfo(familyData, 'frontend_user');

      console.log('API応答:', result);

      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: hasExistingData ? '家族情報を更新しました' : '家族情報を登録しました' 
        });
        setHasExistingData(true);
        setIsEditing(false);
        await loadFamilyInfo();
      } else {
        setMessage({ type: 'error', text: result.error || result.message || '保存に失敗しました' });
      }
    } catch (error) {
      console.error('保存エラー:', error);
      setMessage({ type: 'error', text: `保存中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}` });
    } finally {
      setIsLoading(false);
    }
  };

  const deleteFamilyInfo = async () => {
    if (!confirm('家族情報を削除してもよろしいですか？この操作は取り消せません。')) {
      return;
    }

    try {
      setIsLoading(true);
      setMessage(null);

      const result = await deleteFamilyInfoAPI('frontend_user');
      console.log('削除結果:', result);

      if (result.success) {
        setMessage({ type: 'success', text: '家族情報を削除しました' });
        setFamilyInfo({
          parent_name: '',
          family_structure: '',
          concerns: '',
          children: []
        });
        setHasExistingData(false);
        setIsEditing(true);
      } else {
        setMessage({ type: 'error', text: result.error || result.message || '削除に失敗しました' });
      }
    } catch (error) {
      console.error('削除エラー:', error);
      setMessage({ type: 'error', text: `削除中にエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}` });
    } finally {
      setIsLoading(false);
    }
  };

  const addChild = () => {
    setFamilyInfo(prev => ({
      ...prev,
      children: [...prev.children, {
        name: '',
        age: '',
        gender: '',
        birth_date: '',
        characteristics: '',
        allergies: '',
        medical_notes: ''
      }]
    }));
  };

  const removeChild = (index: number) => {
    setFamilyInfo(prev => ({
      ...prev,
      children: prev.children.filter((_, i) => i !== index)
    }));
  };

  const updateChild = (index: number, field: keyof Child, value: string) => {
    setFamilyInfo(prev => ({
      ...prev,
      children: prev.children.map((child, i) => 
        i === index ? { ...child, [field]: value } : child
      )
    }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
            <Sparkles className="h-6 w-6 text-blue-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p className="text-gray-600 font-medium">家族情報を読み込んでいます...</p>
        </div>
      </div>
    );
  }

  const { childrenCount, allergiesCount } = getChildrenSummary();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* ページヘッダー */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-blue-100">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
                <MdFamilyRestroom className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">家族情報</h1>
                <p className="text-gray-600">あなたの大切な家族を管理・記録します</p>
              </div>
            </div>
            
            {hasExistingData && !isEditing && (
              <div className="flex space-x-3">
                <Link href="/chat">
                  <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Genieに相談
                  </Button>
                </Link>
                <Button onClick={() => setIsEditing(true)} variant="outline" className="border-blue-200 text-blue-700 hover:bg-blue-50">
                  <Edit className="h-4 w-4 mr-2" />
                  編集
                </Button>
                <Button onClick={deleteFamilyInfo} variant="destructive" className="bg-red-500 hover:bg-red-600">
                  <Trash2 className="h-4 w-4 mr-2" />
                  削除
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6 space-y-8">
        {/* 家族サマリーカード */}
        {hasExistingData && !isEditing && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm font-medium">家族構成</p>
                    <p className="text-2xl font-bold mt-1">{familyInfo.family_structure || '未設定'}</p>
                  </div>
                  <MdFamilyRestroom className="h-8 w-8 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm font-medium">お子さん</p>
                    <p className="text-2xl font-bold mt-1">{childrenCount}人</p>
                  </div>
                  <MdChildCare className="h-8 w-8 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-amber-100 text-sm font-medium">アレルギー</p>
                    <p className="text-2xl font-bold mt-1">{allergiesCount}件</p>
                  </div>
                  <FaAllergies className="h-8 w-8 text-amber-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100 text-sm font-medium">最終更新</p>
                    <p className="text-2xl font-bold mt-1">
                      {familyInfo.updated_at ? 
                        new Date(familyInfo.updated_at).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' }) 
                        : '今日'
                      }
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-purple-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* メッセージ表示 */}
        {message && (
          <Card className={`mb-6 ${message.type === 'error' ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'} shadow-lg`}>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className={`h-5 w-5 ${message.type === 'error' ? 'text-red-600' : 'text-green-600'}`} />
                <p className={`text-sm font-medium ${message.type === 'error' ? 'text-red-700' : 'text-green-700'}`}>
                  {message.text}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 基本情報カード */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center gap-3">
              <Users className="h-6 w-6" />
              基本情報
            </CardTitle>
            <CardDescription className="text-blue-100">
              ご家族の基本的な情報を入力してください
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 p-6">
            <div>
              <Label htmlFor="parent_name">保護者名</Label>
              <Input
                id="parent_name"
                value={familyInfo.parent_name}
                onChange={(e) => setFamilyInfo(prev => ({ ...prev, parent_name: e.target.value }))}
                placeholder="田中太郎"
                disabled={!isEditing}
              />
            </div>
            
            <div>
              <Label htmlFor="family_structure">家族構成</Label>
              <Input
                id="family_structure"
                value={familyInfo.family_structure}
                onChange={(e) => setFamilyInfo(prev => ({ ...prev, family_structure: e.target.value }))}
                placeholder="夫婦+子ども1人"
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="concerns">主な心配事・相談したいこと</Label>
              <Textarea
                id="concerns"
                value={familyInfo.concerns}
                onChange={(e) => setFamilyInfo(prev => ({ ...prev, concerns: e.target.value }))}
                placeholder="離乳食の進め方が心配、夜泣きが続いている など"
                rows={3}
                disabled={!isEditing}
              />
            </div>
          </CardContent>
        </Card>

        {/* 子どもの情報カード */}
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-t-lg">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-3">
                  <Baby className="h-6 w-6" />
                  お子さんの情報
                </CardTitle>
                <CardDescription className="text-green-100">
                  お子さんそれぞれの詳しい情報を入力してください
                </CardDescription>
              </div>
              {isEditing && (
                <Button onClick={addChild} className="bg-white/20 hover:bg-white/30 border-white/30 text-white" size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  子どもを追加
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="p-6">
            {familyInfo.children.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                まだお子さんの情報が登録されていません
                {isEditing && <br />}
                {isEditing && "「子どもを追加」ボタンから登録してください"}
              </p>
            ) : (
              <div className="space-y-6">
                {familyInfo.children.map((child, index) => (
                  <Card key={index} className="border-0 shadow-lg bg-gradient-to-br from-white to-blue-50 hover:shadow-xl transition-all duration-300">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                            {child.name ? child.name.charAt(0) : '👶'}
                          </div>
                          <div>
                            <h4 className="font-bold text-lg text-gray-800">{child.name || `お子さん ${index + 1}`}</h4>
                            {child.age && (
                              <p className="text-sm text-gray-600 flex items-center gap-1">
                                <FaBirthdayCake className="h-3 w-3" />
                                {child.age}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {child.birth_date && (
                            <Badge className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
                              {calculateAge(child.birth_date)}
                            </Badge>
                          )}
                          {child.allergies && child.allergies.trim() !== '' && (
                            <Badge className="bg-gradient-to-r from-red-400 to-red-500 text-white">
                              <FaAllergies className="h-3 w-3 mr-1" />
                              アレルギー
                            </Badge>
                          )}
                          {isEditing && (
                            <Button
                              onClick={() => removeChild(index)}
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label>お名前</Label>
                          <Input
                            value={child.name}
                            onChange={(e) => updateChild(index, 'name', e.target.value)}
                            placeholder="田中花子"
                            disabled={!isEditing}
                          />
                        </div>
                        
                        <div>
                          <Label>年齢</Label>
                          <Input
                            value={child.age}
                            onChange={(e) => updateChild(index, 'age', e.target.value)}
                            placeholder="8ヶ月"
                            disabled={!isEditing}
                          />
                        </div>
                        
                        <div>
                          <Label>性別</Label>
                          <Input
                            value={child.gender}
                            onChange={(e) => updateChild(index, 'gender', e.target.value)}
                            placeholder="女の子"
                            disabled={!isEditing}
                          />
                        </div>
                        
                        <div>
                          <Label>生年月日</Label>
                          <Input
                            value={child.birth_date}
                            onChange={(e) => updateChild(index, 'birth_date', e.target.value)}
                            placeholder="2024-04-01"
                            type="date"
                            disabled={!isEditing}
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-4 mt-6">
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                          <Label className="flex items-center gap-2 text-blue-800 font-semibold mb-2">
                            <Heart className="h-4 w-4" />
                            特徴・性格
                          </Label>
                          <Textarea
                            value={child.characteristics}
                            onChange={(e) => updateChild(index, 'characteristics', e.target.value)}
                            placeholder="人見知りが激しい、よく笑う、活発で元気 など"
                            rows={2}
                            disabled={!isEditing}
                            className="bg-white/80 border-blue-200 focus:border-blue-400"
                          />
                        </div>
                        
                        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                          <Label className="flex items-center gap-2 text-red-800 font-semibold mb-2">
                            <FaAllergies className="h-4 w-4" />
                            アレルギー情報
                          </Label>
                          <Input
                            value={child.allergies}
                            onChange={(e) => updateChild(index, 'allergies', e.target.value)}
                            placeholder="卵、牛乳、小麦 など（なしの場合は空欄）"
                            disabled={!isEditing}
                            className="bg-white/80 border-red-200 focus:border-red-400"
                          />
                        </div>
                        
                        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                          <Label className="flex items-center gap-2 text-green-800 font-semibold mb-2">
                            <FaStethoscope className="h-4 w-4" />
                            健康・医療メモ
                          </Label>
                          <Textarea
                            value={child.medical_notes}
                            onChange={(e) => updateChild(index, 'medical_notes', e.target.value)}
                            placeholder="予防接種の状況、通院歴、気になる症状、かかりつけ医 など"
                            rows={2}
                            disabled={!isEditing}
                            className="bg-white/80 border-green-200 focus:border-green-400"
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

        {/* AIチャット連携カード */}
        {hasExistingData && !isEditing && (
          <Card className="shadow-xl border-0 bg-gradient-to-br from-amber-50 to-orange-50">
            <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3">
                <Sparkles className="h-6 w-6" />
                AIチャット連携
              </CardTitle>
              <CardDescription className="text-amber-100">
                この家族情報はチャット機能で自動的に活用され、お子さんに合わせた個別のアドバイスを提供します
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="bg-white/60 p-4 rounded-lg border border-amber-200">
                <p className="text-sm text-amber-800 mb-4">
                  💡 チャットでは、お子さんの名前、年齢、特徴、アレルギー情報などを考慮した
                  パーソナライズされた回答を受け取ることができます。
                </p>
                <Link href="/chat">
                  <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg">
                    <Sparkles className="h-4 w-4 mr-2" />
                    今すぐGenieに相談する
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}