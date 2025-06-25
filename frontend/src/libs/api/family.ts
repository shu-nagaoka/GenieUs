/**
 * 家族情報API関連の型定義とヘルパー関数
 */

export interface Child {
  name: string;
  age: string;
  gender: string;
  birth_date: string;
  characteristics: string;
  allergies: string;
  medical_notes: string;
}

export interface FamilyInfo {
  family_id?: string;
  user_id?: string;
  parent_name: string;
  family_structure: string;
  concerns: string;
  children: Child[];
  created_at?: string;
  updated_at?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * 家族情報を取得
 */
export async function getFamilyInfo(userId: string = 'frontend_user'): Promise<ApiResponse<FamilyInfo>> {
  try {
    const response = await fetch(`${API_BASE_URL}/family/info?user_id=${userId}`);
    return await response.json();
  } catch (error) {
    console.error('家族情報取得エラー:', error);
    throw error;
  }
}

/**
 * 家族情報を登録
 */
export async function registerFamilyInfo(
  familyData: Omit<FamilyInfo, 'family_id' | 'user_id' | 'created_at' | 'updated_at'>,
  userId: string = 'frontend_user'
): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/family/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...familyData,
        user_id: userId
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('家族情報登録エラー:', error);
    throw error;
  }
}

/**
 * 家族情報を更新
 */
export async function updateFamilyInfo(
  familyData: Omit<FamilyInfo, 'family_id' | 'user_id' | 'created_at' | 'updated_at'>,
  userId: string = 'frontend_user'
): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/family/update`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...familyData,
        user_id: userId
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('家族情報更新エラー:', error);
    throw error;
  }
}

/**
 * 家族情報を削除
 */
export async function deleteFamilyInfo(userId: string = 'frontend_user'): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/family/delete?user_id=${userId}`, {
      method: 'DELETE',
    });
    return await response.json();
  } catch (error) {
    console.error('家族情報削除エラー:', error);
    throw error;
  }
}

/**
 * チャット用に家族情報を整形
 */
export function formatFamilyInfoForChat(familyInfo: FamilyInfo): Record<string, any> {
  return {
    parent_name: familyInfo.parent_name,
    family_structure: familyInfo.family_structure,
    concerns: familyInfo.concerns,
    children: familyInfo.children.map(child => ({
      name: child.name,
      age: child.age,
      gender: child.gender,
      birth_date: child.birth_date,
      characteristics: child.characteristics,
      allergies: child.allergies,
      medical_notes: child.medical_notes
    }))
  };
}