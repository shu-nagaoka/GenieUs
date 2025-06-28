'use client'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Utensils, Clock, Camera, User, Mic } from 'lucide-react'
import { getMealRecordsByChild, type MealRecord, type ApiResponse, type MealRecordListResponse } from '@/libs/api/meal-records'

interface MealRecordsListProps {
  childId: string
  limit?: number
  refreshTrigger?: number
}

export function MealRecordsList({ childId, limit = 20, refreshTrigger }: MealRecordsListProps) {
  const [records, setRecords] = useState<MealRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadMealRecords = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response: ApiResponse<MealRecordListResponse> = await getMealRecordsByChild(childId, limit)
      
      if (response.success && response.data?.meal_records) {
        setRecords(response.data.meal_records)
      } else {
        setError(response.error || '食事記録の取得に失敗しました')
      }
    } catch (err) {
      setError('食事記録の取得中にエラーが発生しました')
      console.error('Meal records loading error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMealRecords()
  }, [childId, limit, refreshTrigger])

  const getDetectionSourceIcon = (source: string) => {
    switch (source) {
      case 'image_ai':
        return <Camera className="h-4 w-4" />
      case 'voice_ai':
        return <Mic className="h-4 w-4" />
      case 'manual':
        return <User className="h-4 w-4" />
      default:
        return <Utensils className="h-4 w-4" />
    }
  }

  const getDetectionSourceLabel = (source: string) => {
    switch (source) {
      case 'image_ai':
        return '画像AI'
      case 'voice_ai':
        return '音声AI'
      case 'manual':
        return '手動入力'
      default:
        return '不明'
    }
  }

  const getMealTypeLabel = (type: string) => {
    switch (type) {
      case 'breakfast':
        return '朝食'
      case 'lunch':
        return '昼食'
      case 'dinner':
        return '夕食'
      case 'snack':
        return 'おやつ'
      default:
        return type
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
            <span className="ml-2">食事記録を読み込んでいます...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={loadMealRecords} variant="outline">
              再試行
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (records.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <Utensils className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>食事記録がまだありません</p>
            <p className="text-sm mt-2">写真を撮影して「はい」と答えると自動で記録されます</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Utensils className="h-5 w-5" />
            食事記録 ({records.length}件)
          </CardTitle>
        </CardHeader>
      </Card>

      {records.map((record) => (
        <Card key={record.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-medium">{record.meal_name}</h3>
                  <Badge variant="secondary">
                    {getMealTypeLabel(record.meal_type)}
                  </Badge>
                  <Badge variant="outline" className="flex items-center gap-1">
                    {getDetectionSourceIcon(record.detection_source)}
                    {getDetectionSourceLabel(record.detection_source)}
                  </Badge>
                </div>

                {record.detected_foods && record.detected_foods.length > 0 && (
                  <div className="mb-2">
                    <p className="text-sm font-medium text-gray-700 mb-1">検出された食品:</p>
                    <div className="flex flex-wrap gap-1">
                      {record.detected_foods.map((food, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {food}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTimestamp(record.timestamp)}
                  </span>
                  {record.confidence && (
                    <span>信頼度: {Math.round(record.confidence * 100)}%</span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {records.length === limit && (
        <div className="text-center">
          <Button variant="outline" onClick={loadMealRecords}>
            さらに読み込む
          </Button>
        </div>
      )}
    </div>
  )
}