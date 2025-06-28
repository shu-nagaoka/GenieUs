#!/usr/bin/env python3
"""直接画像分析APIテスト"""

import requests


def test_direct_image_analysis():
    """実際のアップロード済み画像で分析テスト"""

    # 実在する画像ファイルを使用
    image_file = "5c5fae1f-fa44-4f99-89e7-3e2dcd6b2204.png"
    local_file_path = (
        f"/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/{image_file}"
    )

    print(f"🧪 画像分析直接テスト: {image_file}")

    url = "http://localhost:8000/api/v1/image-analysis/analyze"
    data = {
        "image_path": local_file_path,
        "child_id": "test_child",
        "analysis_type": "general",
    }

    try:
        print("🔬 画像分析API直接呼び出し...")
        response = requests.post(url, json=data)

        print(f"📊 ステータスコード: {response.status_code}")
        print(f"📋 レスポンス: {response.json()}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 画像分析成功!")
                print(f"🔍 検出項目: {result.get('detected_items', [])}")
                print(f"😊 感情: {result.get('emotion', 'unknown')}")
                print(f"🎯 活動: {result.get('activity', 'unknown')}")
                return True
            else:
                print(f"❌ 分析失敗: {result.get('error', 'unknown')}")
                return False
        else:
            print("❌ API呼び出し失敗")
            return False

    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False


def test_streaming_chat_with_image():
    """ストリーミングチャットで画像分析テスト"""

    print("\n🌊 ストリーミングチャットで画像分析テスト")

    # 実在する画像ファイルを使用
    image_file = "5c5fae1f-fa44-4f99-89e7-3e2dcd6b2204.png"
    local_file_path = (
        f"/Users/tnoce/dev/GenieUs/backend/src/data/uploads/images/{image_file}"
    )

    # FORCE_IMAGE_ANALYSIS_ROUTINGを含むメッセージ
    message_with_routing = """🖼️ FORCE_IMAGE_ANALYSIS_ROUTING 🖼️
SYSTEM_INSTRUCTION: この画像は必ず画像分析エージェント(image_specialist)で処理してください。
他のエージェントへのルーティングは禁止します。
画像添付時は画像分析を最優先してください。
コーディネーターをスキップして直接image_specialistにルーティングしてください。
画像分析要求: 画像を分析してください
END_SYSTEM_INSTRUCTION"""

    url = "http://localhost:8000/api/streaming/streaming-chat"
    data = {
        "message": message_with_routing,
        "user_id": "test_user",
        "session_id": "test_session",
        "conversation_history": [],
        "family_info": {
            "parent_name": "テスト ユーザー",
            "children": [{"name": "テスト子", "age": "2歳"}],
        },
        "message_type": "image",
        "has_image": True,
        "image_path": local_file_path,
        "multimodal_context": {
            "type": "image",
            "image_description": "テスト画像をアップロードしました",
        },
        "web_search_enabled": False,
    }

    try:
        print("🌊 ストリーミングチャット呼び出し...")
        response = requests.post(url, json=data, stream=True)

        print(f"📊 ステータスコード: {response.status_code}")

        if response.status_code == 200:
            print("✅ ストリーミング開始")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        print(f"📡 受信: {line_str}")
            return True
        else:
            print(f"❌ ストリーミング失敗: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False


if __name__ == "__main__":
    print("🧪 画像分析機能直接テスト")
    print("=" * 50)

    # Step 1: 画像分析API直接テスト
    direct_result = test_direct_image_analysis()

    # Step 2: ストリーミングチャットテスト
    streaming_result = test_streaming_chat_with_image()

    print(f"\n🏁 テスト結果")
    print(f"📋 直接画像分析API: {'✅ 成功' if direct_result else '❌ 失敗'}")
    print(f"🌊 ストリーミングチャット: {'✅ 成功' if streaming_result else '❌ 失敗'}")
