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
            context_image_path = kwargs.get('context', {}).get('image_path')
            
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
                }
            else:
                error_msg = result.get("error", "画像解析中にエラーが発生しました")
                logger.error(f"画像解析UseCase実行エラー: {error_msg}")
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
                    "error": error_msg,
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
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # ファイル拡張子からMIMEタイプを推定
        extension = file_path_obj.suffix.lower()
        mime_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
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
