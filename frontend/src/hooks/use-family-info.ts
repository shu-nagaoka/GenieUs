'use client'
import { useQuery } from '@tanstack/react-query'
import { getFamilyInfo, type FamilyInfo, type Child } from '@/libs/api/family'

export const FAMILY_INFO_QUERY_KEY = ['family-info'] as const

/**
 * 家族情報取得フック
 */
export function useFamilyInfo(userId: string = 'frontend_user') {
  return useQuery({
    queryKey: [...FAMILY_INFO_QUERY_KEY, userId],
    queryFn: () => getFamilyInfo(userId),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
    select: (response) => {
      if (response.success && response.data) {
        return response.data
      }
      return null
    },
    placeholderData: (previousData) => previousData,
  })
}

/**
 * 子供リスト取得フック
 */
export function useChildren(userId: string = 'frontend_user') {
  const { data: familyInfo, ...rest } = useFamilyInfo(userId)
  
  return {
    ...rest,
    data: familyInfo?.children || [],
    children: familyInfo?.children || [],
  }
}

/**
 * 最初の子供のIDを取得するフック
 */
export function usePrimaryChildId(userId: string = 'frontend_user') {
  const { data: familyInfo, isLoading, error } = useFamilyInfo(userId)
  
  const primaryChild = familyInfo?.children?.[0]
  const primaryChildId = primaryChild?.id || null
  
  return {
    childId: primaryChildId,
    child: primaryChild,
    isLoading,
    error,
  }
}

/**
 * 特定の子供の情報を取得するフック
 */
export function useChildInfo(childName: string, userId: string = 'frontend_user') {
  const { data: familyInfo, isLoading, error } = useFamilyInfo(userId)
  
  const child = familyInfo?.children?.find(child => child.name === childName) || null
  
  return {
    child,
    isLoading,
    error,
  }
}

/**
 * 子供選択用のオプション配列を取得するフック
 * NOTE: valueには子供の名前を使用（UIでの選択用）
 * 実際のAPIコール時にはchild.idを使用する
 */
export function useChildrenOptions(userId: string = 'frontend_user') {
  const { data: children, isLoading, error } = useChildren(userId)
  
  const options = children.map(child => ({
    value: child.name, // UI選択用は名前を使用
    label: `${child.name} (${child.age})`,
    child, // child.idはここに含まれる
  }))
  
  return {
    options,
    isLoading,
    error,
  }
}