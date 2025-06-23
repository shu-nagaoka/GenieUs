from typing import Any

from dependency_injector import providers

from src.config.settings import get_settings
from src.di_provider.container import DIContainer
from src.share.logger import setup_logger

logger = setup_logger(__name__)

_container_instance = None


def get_container(
    env_file: str | None = None,
    force_new: bool = False,
    overrides: dict[str, Any] | None = None,
) -> DIContainer:
    """DIコンテナのシングルトンインスタンスを取得する"""
    global _container_instance

    if _container_instance is None or force_new:
        _container_instance = create_container(env_file, overrides)

    return _container_instance


def create_container(env_file: str | None = None, overrides: dict[str, Any] | None = None) -> DIContainer:
    """DIコンテナを生成するファクトリ関数"""
    logger.info("DIコンテナを初期化しています...")
    container = DIContainer()

    if env_file:
        logger.info(f"環境ファイル {env_file} を使用します")
        container.config.override(providers.Singleton(get_settings, env_file))
        # os.environ["ENV_FILE"] = env_file
    if overrides:
        logger.info("カスタムオーバーライドを適用しています")
        _apply_overrides(container, overrides)

    container.wire(
        modules=[
            "src.application.usecases",
        ],
    )
    logger.info("DIコンテナの初期化が完了しました")

    return container


def _apply_overrides(container: DIContainer, overrides: dict[str, Any]) -> None:
    """コンテナに対してオーバーライドを適用する"""
    for provider_path, override_value in overrides.items():
        parts = provider_path.split(".")
        provider = container

        for part in parts[:-1]:
            provider = getattr(provider, part)

        target_provider = getattr(provider, parts[-1])

        if isinstance(override_value, providers.Provider):
            target_provider.override(override_value)
        else:
            target_provider.override(providers.Object(override_value))
        logger.debug(f"プロバイダー {provider_path} をオーバーライドしました")
