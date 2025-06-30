"""成長記録管理UseCase"""

import logging
from datetime import datetime
from typing import Any

from src.domain.entities import GrowthRecord


class GrowthRecordUseCase:
    """成長記録管理のビジネスロジック"""

    def __init__(self, growth_record_repository, family_repository, logger: logging.Logger):
        """Args:
        growth_record_repository: 成長記録リポジトリ
        family_repository: 家族情報リポジトリ
        logger: ロガー（DIコンテナから注入）

        """
        self.growth_record_repository = growth_record_repository
        self.family_repository = family_repository
        self.logger = logger

    async def create_growth_record(self, user_id: str, record_data: dict) -> dict[str, Any]:
        """成長記録を作成

        Args:
            user_id: ユーザーID
            record_data: 成長記録データ

        Returns:
            Dict[str, Any]: 作成結果

        """
        try:
            self.logger.info(f"成長記録作成開始: user_id={user_id}")

            # child_idが提供されていてchild_nameが空の場合、child_nameを解決
            if record_data.get("child_id") and not record_data.get("child_name"):
                child_name = await self._resolve_child_name(user_id, record_data["child_id"])
                if child_name:
                    record_data["child_name"] = child_name
                    self.logger.info(f"child_name解決成功: child_id={record_data['child_id']}, child_name={child_name}")
                else:
                    self.logger.warning(f"child_name解決失敗: child_id={record_data['child_id']}")
                    return {"success": False, "message": "指定されたchild_idに対応する子どもが見つかりません"}

            # 子どもの情報から記録時点での月齢を自動計算
            if record_data.get("child_id") and record_data.get("date"):
                calculated_age = await self._calculate_age_at_record_date(
                    user_id,
                    record_data["child_id"],
                    record_data["date"],
                )
                if calculated_age is not None:
                    record_data["age_in_months"] = calculated_age
                elif record_data.get("age_in_months") is None:
                    record_data["age_in_months"] = 0

            # 成長記録エンティティ作成
            growth_record = GrowthRecord.from_dict(user_id, record_data)

            # リポジトリに保存
            result = await self.growth_record_repository.save_growth_record(growth_record)

            self.logger.info(f"成長記録作成完了: user_id={user_id}, record_id={result.get('record_id')}")
            return {"success": True, "id": result.get("record_id"), "data": growth_record.to_dict()}

        except Exception as e:
            self.logger.error(f"成長記録作成エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"成長記録の作成に失敗しました: {e!s}"}

    async def get_growth_records(self, user_id: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """成長記録一覧を取得

        Args:
            user_id: ユーザーID
            filters: フィルター条件

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"成長記録取得開始: user_id={user_id}")

            records = await self.growth_record_repository.get_growth_records(user_id, filters)

            # child_nameが設定されていない場合は解決する
            for record in records:
                if record.child_id and not record.child_name:
                    child_name = await self._resolve_child_name(user_id, record.child_id)
                    if child_name:
                        record.child_name = child_name

            self.logger.info(f"成長記録取得完了: user_id={user_id}, count={len(records)}")
            return {"success": True, "data": [record.to_dict() for record in records]}

        except Exception as e:
            self.logger.error(f"成長記録取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"成長記録の取得に失敗しました: {e!s}"}

    async def get_growth_record(self, user_id: str, record_id: str) -> dict[str, Any]:
        """特定の成長記録を取得

        Args:
            user_id: ユーザーID
            record_id: 記録ID

        Returns:
            Dict[str, Any]: 取得結果

        """
        try:
            self.logger.info(f"成長記録詳細取得開始: user_id={user_id}, record_id={record_id}")

            record = await self.growth_record_repository.get_growth_record(user_id, record_id)

            if record:
                self.logger.info(f"成長記録詳細取得成功: user_id={user_id}, record_id={record_id}")
                return {"success": True, "data": record.to_dict()}
            else:
                return {"success": False, "message": "成長記録が見つかりません"}

        except Exception as e:
            self.logger.error(f"成長記録詳細取得エラー: user_id={user_id}, record_id={record_id}, error={e}")
            return {"success": False, "message": f"成長記録の取得に失敗しました: {e!s}"}

    async def update_growth_record(self, user_id: str, record_id: str, update_data: dict) -> dict[str, Any]:
        """成長記録を更新

        Args:
            user_id: ユーザーID
            record_id: 記録ID
            update_data: 更新データ

        Returns:
            Dict[str, Any]: 更新結果

        """
        try:
            self.logger.info(f"成長記録更新開始: user_id={user_id}, record_id={record_id}")

            # 既存記録を取得
            existing_record = await self.growth_record_repository.get_growth_record(user_id, record_id)
            if not existing_record:
                return {"success": False, "message": "成長記録が見つかりません"}

            # 更新データをマージ
            updated_data = existing_record.to_dict()
            updated_data.update(update_data)
            updated_data["updated_at"] = datetime.now().isoformat()

            # 年齢再計算（日付が変更された場合）
            if update_data.get("date"):
                calculated_age = await self._calculate_age_at_record_date(
                    user_id,
                    updated_data.get("child_id"),
                    update_data["date"],
                )
                if calculated_age is not None:
                    updated_data["age_in_months"] = calculated_age

            # エンティティ作成して保存
            updated_record = GrowthRecord.from_dict(user_id, updated_data)
            result = await self.growth_record_repository.update_growth_record(updated_record)

            self.logger.info(f"成長記録更新完了: user_id={user_id}, record_id={record_id}")
            return {"success": True, "data": updated_record.to_dict()}

        except Exception as e:
            self.logger.error(f"成長記録更新エラー: user_id={user_id}, record_id={record_id}, error={e}")
            return {"success": False, "message": f"成長記録の更新に失敗しました: {e!s}"}

    async def delete_growth_record(self, user_id: str, record_id: str) -> dict[str, Any]:
        """成長記録を削除

        Args:
            user_id: ユーザーID
            record_id: 記録ID

        Returns:
            Dict[str, Any]: 削除結果

        """
        try:
            self.logger.info(f"成長記録削除開始: user_id={user_id}, record_id={record_id}")

            result = await self.growth_record_repository.delete_growth_record(user_id, record_id)

            if result:
                self.logger.info(f"成長記録削除完了: user_id={user_id}, record_id={record_id}")
                return {"success": True, "message": "成長記録を削除しました", "deleted_data": result.to_dict()}
            else:
                return {"success": False, "message": "成長記録が見つかりません"}

        except Exception as e:
            self.logger.error(f"成長記録削除エラー: user_id={user_id}, record_id={record_id}, error={e}")
            return {"success": False, "message": f"成長記録の削除に失敗しました: {e!s}"}

    async def get_children_for_growth_records(self, user_id: str) -> dict[str, Any]:
        """成長記録用の子ども一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: 子ども一覧

        """
        try:
            self.logger.info(f"子ども一覧取得開始: user_id={user_id}")

            family_info = await self.family_repository.get_family_info(user_id)

            if not family_info:
                return {"success": True, "data": []}

            children = []
            for i, child in enumerate(family_info.children):
                # 子どもIDを生成
                child_id = f"{user_id}_child_{i}"

                # 現在の月齢を計算
                age_in_months = 0
                age_display = ""
                if child.get("birth_date"):
                    try:
                        birth_date = datetime.strptime(child["birth_date"], "%Y-%m-%d")
                        current_date = datetime.now()
                        age_in_months = (current_date.year - birth_date.year) * 12 + (
                            current_date.month - birth_date.month
                        )
                        if current_date.day < birth_date.day:
                            age_in_months -= 1
                        age_in_months = max(0, age_in_months)

                        # 年齢表示文字列生成
                        years = age_in_months // 12
                        months = age_in_months % 12
                        if years > 0 and months > 0:
                            age_display = f"{years}歳{months}ヶ月"
                        elif years > 0:
                            age_display = f"{years}歳"
                        else:
                            age_display = f"{months}ヶ月"
                    except:
                        pass

                children.append(
                    {
                        "child_id": child_id,
                        "name": child.get("name", ""),
                        "age": age_display,
                        "age_in_months": age_in_months,
                        "gender": child.get("gender", ""),
                        "birth_date": child.get("birth_date", ""),
                    },
                )

            self.logger.info(f"子ども一覧取得完了: user_id={user_id}, count={len(children)}")
            return {"success": True, "data": children}

        except Exception as e:
            self.logger.error(f"子ども一覧取得エラー: user_id={user_id}, error={e}")
            return {"success": False, "message": f"子ども一覧の取得に失敗しました: {e!s}"}

    async def _calculate_age_at_record_date(self, user_id: str, child_id: str, record_date: str) -> int | None:
        """記録日時点での年齢を計算

        Args:
            user_id: ユーザーID
            child_id: 子どもID
            record_date: 記録日付

        Returns:
            Optional[int]: 月齢（計算失敗時はNone）

        """
        try:
            family_info = await self.family_repository.get_family_info(user_id)
            if not family_info:
                return None

            # 子どもIDからインデックスを取得
            child_index = int(child_id.split("_")[-1])
            if 0 <= child_index < len(family_info.children):
                child = family_info.children[child_index]

                if child.get("birth_date"):
                    birth_date = datetime.strptime(child["birth_date"], "%Y-%m-%d")
                    record_date_obj = datetime.strptime(record_date, "%Y-%m-%d")

                    age_in_months = (record_date_obj.year - birth_date.year) * 12 + (
                        record_date_obj.month - birth_date.month
                    )
                    if record_date_obj.day < birth_date.day:
                        age_in_months -= 1

                    return max(0, age_in_months)

            return None
        except Exception as e:
            self.logger.error(f"年齢計算エラー: {e}")
            return None

    async def _resolve_child_name(self, user_id: str, child_id: str) -> str | None:
        """child_idからchild_nameを解決

        Args:
            user_id: ユーザーID
            child_id: 子どもID

        Returns:
            Optional[str]: 子どもの名前（見つからない場合はNone）

        """
        try:
            family_info = await self.family_repository.get_family_info(user_id)
            if not family_info:
                return None

            # child_idからインデックスを取得
            child_index = int(child_id.split("_")[-1])
            if 0 <= child_index < len(family_info.children):
                return family_info.children[child_index].get("name", "")

            return None
        except Exception as e:
            self.logger.error(f"child_name解決エラー: {e}")
            return None
