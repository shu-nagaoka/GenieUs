#!/usr/bin/env python3
"""画像アップロード機能のテストスクリプト"""

import io
import requests
from PIL import Image

def create_test_image():
    """テスト用の画像を作成"""
    # 200x200のテスト画像を作成
    img = Image.new('RGB', (200, 200), color='lightblue')
    
    # 画像をバイトデータに変換
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def test_image_upload():
    """画像アップロードAPIをテスト"""
    print("🧪 画像アップロードAPIテスト開始...")
    
    # テスト画像作成
    test_image = create_test_image()
    
    # アップロードリクエスト
    url = "http://localhost:8000/api/v1/files/upload/image"
    files = {
        'file': ('test_image.png', test_image, 'image/png')
    }
    data = {
        'user_id': 'test_user'
    }
    
    try:
        print("📤 アップロード実行中...")
        response = requests.post(url, files=files, data=data)
        
        print(f"📊 ステータスコード: {response.status_code}")
        print(f"📋 レスポンス: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ アップロード成功!")
                print(f"📁 ファイルURL: {result.get('file_url')}")
                print(f"🆔 ファイルID: {result.get('file_id')}")
                return result
            else:
                print("❌ アップロード失敗")
                return None
        else:
            print(f"❌ HTTPエラー: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return None

def test_image_analysis(file_url):
    """画像分析APIをテスト"""
    print("\n🔍 画像分析APIテスト開始...")
    
    # ファイル名を抽出
    filename = file_url.split('/')[-1]
    local_file_path = f"/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/{filename}"
    
    url = "http://localhost:8000/api/v1/image-analysis/analyze"
    data = {
        'image_path': local_file_path,
        'child_id': 'test_child',
        'analysis_type': 'general'
    }
    
    try:
        print("🔬 分析実行中...")
        response = requests.post(url, json=data)
        
        print(f"📊 ステータスコード: {response.status_code}")
        print(f"📋 レスポンス: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 分析成功!")
            return True
        else:
            print("❌ 分析失敗")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

if __name__ == "__main__":
    print("🧪 画像アップロード・分析統合テスト")
    print("=" * 50)
    
    # Step 1: 画像アップロードテスト
    upload_result = test_image_upload()
    
    if upload_result and upload_result.get('file_url'):
        # Step 2: 画像分析テスト
        test_image_analysis(upload_result['file_url'])
    else:
        print("❌ アップロードが失敗したため、分析テストをスキップします")
    
    print("\n🏁 テスト完了")