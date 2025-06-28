#!/usr/bin/env python3
"""リアルな画像分析テスト"""

import io
import requests
from PIL import Image, ImageDraw, ImageFont

def create_realistic_test_image():
    """子どもの食事シーンを模擬したテスト画像を作成"""
    # 400x300のテスト画像を作成
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # 背景
    draw.rectangle([0, 0, 400, 300], fill='lightyellow')
    
    # テーブル
    draw.rectangle([50, 150, 350, 280], fill='brown')
    
    # お皿
    draw.ellipse([120, 180, 200, 220], fill='white', outline='gray', width=2)
    
    # 食べ物（おにぎり風）
    draw.ellipse([140, 190, 170, 210], fill='white', outline='black')
    draw.rectangle([155, 195, 160, 205], fill='black')  # のり
    
    # コップ
    draw.rectangle([220, 185, 250, 215], fill='lightblue', outline='blue', width=2)
    
    # 簡単な顔（笑顔）
    draw.ellipse([270, 100, 330, 160], fill='#FFDBAC', outline='#8B4513', width=2)  # 肌色
    draw.ellipse([285, 120, 295, 130], fill='black')  # 左目
    draw.ellipse([305, 120, 315, 130], fill='black')  # 右目
    draw.arc([285, 135, 315, 150], 0, 180, fill='red', width=3)  # 笑顔
    
    # 手
    draw.ellipse([250, 160, 280, 180], fill='#FFDBAC')  # 肌色
    
    # タイトル（日本語代わり）
    try:
        # フォント設定（利用可能な場合）
        font = ImageFont.load_default()
        draw.text((10, 10), "Child Eating Scene - Test Image", fill='black', font=font)
        draw.text((10, 25), "Happy child having lunch", fill='black', font=font)
    except:
        # フォントが利用できない場合はスキップ
        pass
    
    # 画像をバイトデータに変換
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

def test_realistic_image_upload_and_analysis():
    """リアルな画像でアップロード・分析統合テスト"""
    print("🧪 リアルな画像分析テスト開始...")
    
    # Step 1: リアルなテスト画像作成
    print("🎨 子どもの食事シーンテスト画像作成中...")
    test_image = create_realistic_test_image()
    
    # Step 2: アップロード
    print("📤 画像アップロード中...")
    upload_url = "http://localhost:8000/api/v1/files/upload/image"
    files = {
        'file': ('realistic_child_scene.png', test_image, 'image/png')
    }
    data = {
        'user_id': 'test_user'
    }
    
    try:
        upload_response = requests.post(upload_url, files=files, data=data)
        print(f"📊 アップロードステータス: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            if upload_result.get('success'):
                print(f"✅ アップロード成功: {upload_result.get('file_url')}")
                filename = upload_result['file_url'].split('/')[-1]
                local_file_path = f"/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/{filename}"
                
                # Step 3: 画像分析
                print("🔍 画像分析実行中...")
                analysis_url = "http://localhost:8000/api/v1/image-analysis/analyze"
                analysis_data = {
                    'image_path': local_file_path,
                    'child_id': 'test_child',
                    'analysis_type': 'feeding'
                }
                
                analysis_response = requests.post(analysis_url, json=analysis_data)
                print(f"📊 分析ステータス: {analysis_response.status_code}")
                
                if analysis_response.status_code == 200:
                    result = analysis_response.json()
                    print("✅ 画像分析成功!")
                    print(f"🔍 検出項目: {result.get('detected_items', [])}")
                    print(f"😊 感情: {result.get('emotion_detected', 'unknown')}")
                    print(f"🎯 活動: {result.get('activity_type', 'unknown')}")
                    print(f"📊 信頼度: {result.get('confidence', 0):.2f}")
                    print(f"💡 提案: {result.get('suggestions', [])}")
                    
                    if result.get('safety_concerns'):
                        print(f"⚠️ 安全上の注意: {result.get('safety_concerns', [])}")
                    
                    return True
                else:
                    print(f"❌ 分析失敗: {analysis_response.text}")
                    return False
            else:
                print("❌ アップロード失敗")
                return False
        else:
            print(f"❌ アップロードHTTPエラー: {upload_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_streaming_with_realistic_image():
    """ストリーミングチャットでリアルな画像分析テスト"""
    print("\n🌊 ストリーミングチャットでリアルな画像テスト")
    
    # 実在する最新ファイルを取得
    import os
    uploads_dir = "/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images"
    files = [f for f in os.listdir(uploads_dir) if f.endswith('.png')]
    if not files:
        print("❌ テスト用画像ファイルが見つかりません")
        return False
    
    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(uploads_dir, f)))
    local_file_path = os.path.join(uploads_dir, latest_file)
    
    print(f"🖼️ 使用画像: {latest_file}")
    
    message = """この画像を詳しく分析してください。特に以下の点に注目してください：
1. 子どもの表情や感情状態
2. 食事の内容や摂取状況
3. 周囲の環境や安全性
4. 発達段階の指標"""
    
    url = "http://localhost:8000/api/streaming/streaming-chat"
    data = {
        "message": message,
        "user_id": "test_user",
        "session_id": "realistic_test_session",
        "conversation_history": [],
        "family_info": {
            "parent_name": "テスト ユーザー",
            "children": [{"name": "テスト子", "age": "2歳"}]
        },
        "message_type": "image",
        "has_image": True,
        "image_path": local_file_path,
        "multimodal_context": {
            "type": "image",
            "image_description": "子どもの食事シーンのリアルなテスト画像"
        },
        "web_search_enabled": False
    }
    
    try:
        print("🌊 ストリーミング分析開始...")
        response = requests.post(url, json=data, stream=True)
        
        if response.status_code == 200:
            print("✅ ストリーミング成功")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        print(f"📡 {line_str[6:]}")  # 'data: 'を除去して表示
            return True
        else:
            print(f"❌ ストリーミング失敗: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

if __name__ == "__main__":
    print("🧪 リアルな画像分析統合テスト")
    print("=" * 60)
    
    # Step 1: リアルな画像でのアップロード・分析テスト
    direct_result = test_realistic_image_upload_and_analysis()
    
    # Step 2: ストリーミングチャットテスト
    streaming_result = test_streaming_with_realistic_image()
    
    print(f"\n🏁 テスト結果")
    print(f"📋 リアル画像直接分析: {'✅ 成功' if direct_result else '❌ 失敗'}")
    print(f"🌊 ストリーミングチャット: {'✅ 成功' if streaming_result else '❌ 失敗'}")
    
    if direct_result and streaming_result:
        print("\n🎉 画像分析機能が正常に動作しています！")
        print("📸 実際の子どもの写真でもテストしてみてください")
    else:
        print("\n⚠️ 一部のテストが失敗しました。ログを確認してください。")