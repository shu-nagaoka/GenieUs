import base64
import logging
from pathlib import Path
from typing import Any

from google.adk.tools import FunctionTool
from src.application.usecases.image_analysis_usecase import ImageAnalysisUseCase


def create_image_analysis_tool(image_analysis_usecase: ImageAnalysisUseCase, logger: logging.Logger):
    """画像解析ツール作成（薄いアダプター）"""
    logger.info("画像解析ツール作成開始")

    async def analyze_child_image(
        image_path: str = "",  # デフォルト値設定（空文字）
        child_id: str = "default_child",
        analysis_type: str = "general",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """子どもの画像を分析してデータを抽出

        Args:
            image_path: 画像ファイルのパス
            child_id: 子どものID
            analysis_type: 分析タイプ（general, feeding, development等）
            **kwargs: 追加のコンテキスト情報

        Returns:
            Dict[str, Any]: 分析結果

        """
        try:
            logger.info(f"画像解析ツール実行開始: child_id={child_id}, analysis_type={analysis_type}")

            # コンテキストからimage_pathを取得を試行
            context_image_path = kwargs.get("context", {}).get("image_path")

            # 優先順位: 引数 > コンテキスト
            final_image_path = image_path or context_image_path

            if final_image_path and final_image_path != image_path:
                logger.info(f"コンテキストから画像パスを取得: {len(final_image_path) if final_image_path else 0}文字")
                image_path = final_image_path

            # image_pathが空の場合の処理
            if not image_path or image_path.strip() == "":
                logger.info("image_pathが提供されていません - デモンストレーションモードで実行")
                return {
                    "success": True,
                    "child_id": child_id,
                    "detected_items": ["お子さんの笑顔", "健康的な表情"],
                    "confidence": 0.8,
                    "suggestions": ["画像を提供していただければ、より詳細な分析ができます"],
                    "emotion_detected": "happy",
                    "activity_type": "playing",
                    "extracted_events": [],
                    "safety_concerns": [],
                    "has_safety_concerns": False,
                    "timestamp": None,
                    "ai_model": "gemini-2.5-flash",
                    "error": None,
                    # ツール専用フィールド（下位互換性）
                    "emotion": "happy",
                    "activity": "playing",
                    "message": "📸 画像分析デモモード: 実際の画像を提供していただければ、より詳細な分析を行えます",
                }

            # ローカルファイルパスかBase64データかを判定
            is_file_path = _is_local_file_path(image_path)
            if is_file_path:
                logger.info(f"ローカルファイルパス検出: {image_path}")
                # ローカルファイルを読み込んでBase64に変換
                image_path = await _read_local_file_as_base64(image_path, logger)
            else:
                logger.info(f"Base64データ受信: {len(image_path)}文字")

            # コンテキスト情報の構築
            analysis_context = {
                "analysis_type": analysis_type,
                **kwargs,  # user_id, session_id等の追加情報
            }

            # UseCase層の呼び出し
            result = await image_analysis_usecase.analyze_child_image(
                image_path=image_path,
                child_id=child_id,
                analysis_context=analysis_context,
            )

            # 食事関連判定を実行
            food_analysis = _analyze_food_content(result)

            # 統一レスポンス形式で返却（ImageAnalysisResponse互換）
            if result.get("success", True):
                return {
                    "success": True,
                    "child_id": child_id,
                    "detected_items": result.get("detected_items", []),
                    "confidence": result.get("confidence", 0.0),
                    "suggestions": result.get("suggestions", []),
                    "emotion_detected": result.get("emotion_detected", "unknown"),
                    "activity_type": result.get("activity_type", "unknown"),
                    "extracted_events": result.get("extracted_events", []),
                    "safety_concerns": result.get("safety_concerns", []),
                    "has_safety_concerns": bool(result.get("safety_concerns", [])),
                    "timestamp": result.get("timestamp", None),
                    "ai_model": result.get("ai_model", "gemini-2.5-flash"),
                    "error": None,
                    # ツール専用フィールド（下位互換性）
                    "emotion": result.get("emotion_detected", "unknown"),
                    "activity": result.get("activity_type", "unknown"),
                    "message": _format_analysis_summary(result),
                    # 🍽️ Human-in-the-Loop食事管理統合フィールド
                    "is_food_related": food_analysis["is_food_related"],
                    "suggested_meal_data": food_analysis["suggested_meal_data"],
                    "registration_recommendation": food_analysis["registration_recommendation"],
                }
            else:
                error_msg = result.get("error", "画像解析中にエラーが発生しました")
                logger.error(f"画像解析UseCase実行エラー: {error_msg}")

                return {
                    "success": False,
                    "child_id": child_id,
                    "detected_items": [],
                    "confidence": 0.0,
                    "suggestions": ["画像解析中にエラーが発生しました。再度お試しください。"],
                    "emotion_detected": "unknown",
                    "activity_type": "unknown",
                    "extracted_events": [],
                    "safety_concerns": [],
                    "has_safety_concerns": False,
                    "timestamp": None,
                    "ai_model": "gemini-2.5-flash",
                    "error": error_msg,
                    # 🍽️ Human-in-the-Loop食事管理統合フィールド
                    "is_food_related": False,
                    "suggested_meal_data": None,
                    "registration_recommendation": "画像解析ができませんでした。手動で食事情報を入力することもできます。",
                }

        except Exception as e:
            logger.error(f"画像解析ツール実行エラー: {e}")
            return {
                "success": False,
                "child_id": child_id,
                "detected_items": [],
                "confidence": 0.0,
                "suggestions": [],
                "emotion_detected": "unknown",
                "activity_type": "unknown",
                "extracted_events": [],
                "safety_concerns": [],
                "has_safety_concerns": False,
                "timestamp": None,
                "ai_model": "gemini-2.5-flash",
                "error": str(e),
            }

    logger.info("画像解析ツール作成完了")

    return FunctionTool(func=analyze_child_image)


def _format_analysis_summary(result: dict[str, Any]) -> str:
    """分析結果の要約フォーマット"""
    if not result:
        return "画像分析を完了しました。"

    parts = ["📸 画像分析結果:"]

    if result.get("detected_items"):
        items = result["detected_items"][:3]  # 最初の3つ
        parts.append(f"  👀 検出項目: {', '.join(items)}")

    if result.get("emotion_detected"):
        emotion_map = {
            "happy": "😊 幸せそう",
            "sad": "😢 悲しそう",
            "angry": "😠 怒っている",
            "surprised": "😲 驚いている",
            "neutral": "😐 普通の表情",
        }
        emotion = emotion_map.get(result["emotion_detected"], result["emotion_detected"])
        parts.append(f"  💭 表情: {emotion}")

    if result.get("activity_type"):
        parts.append(f"  🎯 活動: {result['activity_type']}")

    if result.get("confidence"):
        confidence = result["confidence"]
        parts.append(f"  📊 信頼度: {confidence:.1%}")

    if result.get("safety_concerns"):
        parts.append(f"  ⚠️ 安全上の注意: {len(result['safety_concerns'])}件")

    return "\n".join(parts)


def _is_local_file_path(image_path: str) -> bool:
    """ローカルファイルパスかBase64データかを判定

    Args:
        image_path: 判定対象の文字列

    Returns:
        bool: ローカルファイルパスの場合True、Base64データの場合False
    """
    # Base64データの特徴を確認
    if image_path.startswith("data:image/"):
        return False
    if len(image_path) > 1000 and "/" not in image_path[:100]:
        # 長い文字列で先頭にスラッシュがない場合はBase64の可能性が高い
        return False

    # ファイルパスの特徴を確認
    if "/" in image_path or "\\" in image_path:
        return True
    if "." in image_path and any(ext in image_path.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
        return True

    return False


async def _read_local_file_as_base64(file_path: str, logger: logging.Logger) -> str:
    """ローカルファイルを読み込んでBase64エンコードして返す

    Args:
        file_path: 読み込むファイルのパス
        logger: ロガー

    Returns:
        str: Base64エンコードされた画像データ

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        Exception: ファイル読み込みエラー
    """
    try:
        # セキュリティ: パストラバーサル攻撃を防止
        file_path_obj = Path(file_path).resolve()

        # アップロードディレクトリ配下のファイルのみ許可
        # backend/src/tools/image_analysis_tool.py から backend/src/data/uploads へのパス
        uploads_dir = Path(__file__).parent.parent / "data" / "uploads"
        uploads_dir = uploads_dir.resolve()

        logger.info(f"アップロードディレクトリ: {uploads_dir}")
        logger.info(f"ファイルパス絶対化: {file_path_obj}")
        logger.info(f"パス検証: {str(file_path_obj).startswith(str(uploads_dir))}")

        if not str(file_path_obj).startswith(str(uploads_dir)):
            logger.error(f"不正なファイルパス: {file_path} (許可ディレクトリ外)")
            raise ValueError(f"アクセス許可されていないディレクトリです: {file_path}")

        if not file_path_obj.exists():
            logger.error(f"ファイルが存在しません: {file_path}")
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        logger.info(f"ローカルファイル読み込み開始: {file_path}")
        logger.info(f"解決後パス: {file_path_obj}")
        logger.info(f"ファイルサイズ: {file_path_obj.stat().st_size}バイト")

        # ファイルをバイナリで読み込み
        with open(file_path_obj, "rb") as f:
            file_data = f.read()
            logger.info(f"ファイルデータ読み込み成功: {len(file_data)}バイト")

        # Base64エンコード
        base64_data = base64.b64encode(file_data).decode("utf-8")

        # ファイル拡張子からMIMEタイプを推定
        extension = file_path_obj.suffix.lower()
        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_type_map.get(extension, "image/jpeg")

        # data URL形式で返す
        data_url = f"data:{mime_type};base64,{base64_data}"

        logger.info(f"ローカルファイル読み込み完了: {len(data_url)}文字のBase64データに変換")
        return data_url

    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"ローカルファイル読み込みエラー: {e}")
        raise Exception(f"ファイル読み込み中にエラーが発生しました: {e}")


def _analyze_food_content(analysis_result: dict) -> dict:
    """画像解析結果から食事関連データを分析

    Args:
        analysis_result: 画像解析結果

    Returns:
        dict: 食事関連分析結果
    """
    # 食事関連キーワードの定義
    food_keywords = [
        # 主食
        "ご飯",
        "パン",
        "うどん",
        "そば",
        "ラーメン",
        "パスタ",
        "スパゲッティ",
        "おにぎり",
        "サンドイッチ",
        "ピザ",
        "お粥",
        "雑炊",
        # 主菜
        "肉",
        "魚",
        "鶏肉",
        "豚肉",
        "牛肉",
        "卵",
        "ハンバーグ",
        "唐揚げ",
        "焼き魚",
        "刺身",
        "ステーキ",
        "とんかつ",
        "チキン",
        # 副菜・野菜
        "野菜",
        "サラダ",
        "野菜炒め",
        "煮物",
        "お浸し",
        "漬物",
        "きんぴら",
        "トマト",
        "きゅうり",
        "人参",
        "キャベツ",
        "レタス",
        "ブロッコリー",
        # 汁物
        "味噌汁",
        "みそ汁",
        "スープ",
        "お吸い物",
        "豚汁",
        "けんちん汁",
        # 乳製品・デザート
        "ヨーグルト",
        "チーズ",
        "牛乳",
        "プリン",
        "ゼリー",
        "アイス",
        "ケーキ",
        "クッキー",
        "チョコレート",
        "果物",
        "りんご",
        "バナナ",
        # 離乳食・幼児食
        "離乳食",
        "幼児食",
        "ベビーフード",
        "おやつ",
        "ボーロ",
        "せんべい",
        # 飲み物
        "ジュース",
        "お茶",
        "水",
        "コーヒー",
        "紅茶",
        "麦茶",
        # 食事シーン
        "食事",
        "朝食",
        "昼食",
        "夕食",
        "おやつ",
        "間食",
        "お弁当",
        "定食",
    ]

    # 検出項目から食事関連項目を抽出
    detected_items = analysis_result.get("detected_items", [])
    food_items = []

    for item in detected_items:
        for keyword in food_keywords:
            if keyword in item:
                food_items.append(item)
                break

    # 食事関連の信頼度計算
    is_food_related = len(food_items) > 0
    food_confidence = len(food_items) / max(len(detected_items), 1) if detected_items else 0

    # 提案する食事データの生成
    suggested_meal_data = None
    registration_recommendation = ""

    if is_food_related:
        # 食事時間の推定
        meal_time = _estimate_meal_time(detected_items)

        # 栄養バランスの簡易評価
        nutrition_balance = _estimate_nutrition_balance(food_items)

        suggested_meal_data = {
            "meal_name": _generate_meal_name(food_items),
            "detected_foods": food_items,
            "estimated_meal_time": meal_time,
            "nutrition_balance": nutrition_balance,
            "confidence": food_confidence,
            "auto_detected": True,
        }

        # 登録推奨メッセージの生成
        if food_confidence > 0.5:
            registration_recommendation = (
                f"この画像には{len(food_items)}種類の食べ物が検出されました。"
                f"食事管理システムに「{suggested_meal_data['meal_name']}」として登録しますか？"
            )
        else:
            registration_recommendation = (
                "食事らしい画像が検出されましたが、詳細が不明確です。手動で食事情報を入力して登録することもできます。"
            )
    else:
        registration_recommendation = "この画像は食事関連ではないようです。"

    return {
        "is_food_related": is_food_related,
        "food_items": food_items,
        "food_confidence": food_confidence,
        "suggested_meal_data": suggested_meal_data,
        "registration_recommendation": registration_recommendation,
    }


def _estimate_meal_time(detected_items: list) -> str:
    """検出項目から食事時間を推定

    Args:
        detected_items: 検出された項目リスト

    Returns:
        str: 推定された食事時間
    """
    # 現在時刻から基本的な推定
    from datetime import datetime

    now = datetime.now()
    hour = now.hour

    # 時間帯による推定
    if 5 <= hour < 10:
        return "breakfast"
    elif 11 <= hour < 15:
        return "lunch"
    elif 17 <= hour < 22:
        return "dinner"
    else:
        return "snack"


def _estimate_nutrition_balance(food_items: list) -> dict:
    """検出された食べ物から栄養バランスを簡易推定

    Args:
        food_items: 検出された食べ物リスト

    Returns:
        dict: 栄養バランス情報
    """
    # 栄養素カテゴリの定義
    carb_foods = ["ご飯", "パン", "うどん", "そば", "ラーメン", "パスタ"]
    protein_foods = ["肉", "魚", "卵", "鶏肉", "豚肉", "牛肉", "ハンバーグ", "唐揚げ"]
    vegetable_foods = ["野菜", "サラダ", "野菜炒め", "トマト", "きゅうり", "人参"]
    dairy_foods = ["ヨーグルト", "チーズ", "牛乳"]

    balance = {"carbohydrates": False, "proteins": False, "vegetables": False, "dairy": False, "balance_score": 0}

    # 各栄養素の存在をチェック
    for item in food_items:
        if any(food in item for food in carb_foods):
            balance["carbohydrates"] = True
        if any(food in item for food in protein_foods):
            balance["proteins"] = True
        if any(food in item for food in vegetable_foods):
            balance["vegetables"] = True
        if any(food in item for food in dairy_foods):
            balance["dairy"] = True

    # バランススコア計算（0-4）
    balance["balance_score"] = sum(
        [balance["carbohydrates"], balance["proteins"], balance["vegetables"], balance["dairy"]]
    )

    return balance


def _generate_meal_name(food_items: list) -> str:
    """検出された食べ物から食事名を生成

    Args:
        food_items: 検出された食べ物リスト

    Returns:
        str: 生成された食事名
    """
    if not food_items:
        return "検出された食事"

    # 主要な食べ物を特定
    main_foods = []
    for item in food_items[:3]:  # 最初の3つまで
        # 詳細すぎる説明を簡略化
        simplified = item.split("の")[0].split("と")[0]
        main_foods.append(simplified)

    if len(main_foods) == 1:
        return main_foods[0]
    elif len(main_foods) == 2:
        return f"{main_foods[0]}と{main_foods[1]}"
    else:
        return f"{main_foods[0]}定食"
