from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    raw_root: Path
    raw_sources_root: Path
    wiki_root: Path
    wiki_sources_root: Path
    storage_root: Path
    asset_root: Path
    db_path: Path
    templates_root: Path
    static_root: Path


def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[1]
    storage_root = repo_root / "storage"

    return Settings(
        repo_root=repo_root,
        raw_root=repo_root / "raw",
        raw_sources_root=repo_root / "raw" / "sources",
        wiki_root=repo_root / "wiki",
        wiki_sources_root=repo_root / "wiki" / "sources",
        storage_root=storage_root,
        asset_root=storage_root / "assets",
        db_path=storage_root / "app.db",
        templates_root=repo_root / "app" / "templates",
        static_root=repo_root / "app" / "static",
    )


settings = get_settings()


def ensure_runtime_directories() -> None:
    for path in (
        settings.raw_sources_root,
        settings.wiki_sources_root,
        settings.storage_root,
        settings.asset_root,
        settings.templates_root,
        settings.static_root,
    ):
        path.mkdir(parents=True, exist_ok=True)
