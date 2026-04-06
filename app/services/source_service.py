from __future__ import annotations

import json
import re
from datetime import datetime
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings
from app.db import get_connection
from app.schemas import JobSummary, SourceCreateResponse, SourceSummary
from app.services.git_service import maybe_commit_ingest
from app.services.wiki_service import (
    append_log_entry,
    build_raw_source_markdown,
    build_wiki_source_note,
    ensure_unique_stem,
    register_source_in_index,
    slugify,
    split_tags,
)


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-")
    return cleaned or "upload.bin"


async def create_source(
    *,
    title: str,
    source_type: str,
    description: str | None,
    source_url: str | None,
    tags_raw: str | None,
    body_text: str | None,
    upload: UploadFile | None,
) -> SourceCreateResponse:
    created_at = datetime.now().isoformat(timespec="seconds")
    source_id = uuid4().hex
    job_id = uuid4().hex
    tags = split_tags(tags_raw)

    asset_relative_path: str | None = None
    if upload and upload.filename:
        asset_dir = settings.asset_root / source_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        sanitized_name = sanitize_filename(upload.filename)
        asset_path = asset_dir / sanitized_name
        asset_bytes = await upload.read()
        asset_path.write_bytes(asset_bytes)
        asset_relative_path = asset_path.relative_to(settings.repo_root).as_posix()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sources (
                id, title, source_type, status, created_at, description,
                source_url, tags_json, raw_path, wiki_path, asset_path, body_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                title,
                source_type,
                "queued",
                created_at,
                description,
                source_url,
                json.dumps(tags, ensure_ascii=False),
                "",
                "",
                asset_relative_path,
                body_text,
            ),
        )
        connection.execute(
            """
            INSERT INTO jobs (id, source_id, status, created_at, started_at, completed_at, detail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                source_id,
                "queued",
                created_at,
                None,
                None,
                "Queued for background ingest.",
            ),
        )

    source = SourceSummary(
        id=source_id,
        title=title,
        source_type=source_type,  # type: ignore[arg-type]
        status="queued",
        created_at=created_at,
        description=description,
        source_url=source_url,
        tags=tags,
        raw_path="",
        wiki_path="",
        asset_path=asset_relative_path,
        body_text=body_text,
    )
    job = JobSummary(
        id=job_id,
        source_id=source_id,
        status="queued",
        created_at=created_at,
        completed_at=None,
        detail="Queued for background ingest.",
    )
    return SourceCreateResponse(source=source, job=job)


def process_job(job_id: str) -> None:
    started_at = datetime.now().isoformat(timespec="seconds")
    source_row = _mark_job_processing(job_id, started_at)
    if source_row is None:
        return

    try:
        result = _materialize_source(source_row)
        commit_detail = maybe_commit_ingest(
            [
                result["raw_path"],
                result["wiki_path"],
                "wiki/index.md",
                "wiki/log.md",
            ],
            source_row["title"],
        )
        _mark_job_completed(
            job_id=job_id,
            source_id=source_row["id"],
            completed_at=datetime.now().isoformat(timespec="seconds"),
            raw_path=result["raw_path"],
            wiki_path=result["wiki_path"],
            detail=f"Ingest completed. {commit_detail}",
        )
    except Exception as error:
        _mark_job_failed(
            job_id=job_id,
            source_id=source_row["id"],
            completed_at=datetime.now().isoformat(timespec="seconds"),
            detail=f"Ingest failed: {error}",
        )


def _materialize_source(source_row) -> dict[str, str]:
    created_day = source_row["created_at"].split("T")[0]
    slug = slugify(source_row["title"])
    short_id = source_row["id"][:8]
    tags = json.loads(source_row["tags_json"])

    raw_dir_name = f"{created_day}-{slug}-{short_id}"
    raw_dir = settings.raw_sources_root / raw_dir_name
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_source_path = raw_dir / "source.md"
    raw_relative_path = raw_source_path.relative_to(settings.repo_root).as_posix()
    raw_content = build_raw_source_markdown(
        title=source_row["title"],
        source_type=source_row["source_type"],
        created=created_day,
        tags=tags,
        description=source_row["description"],
        source_url=source_row["source_url"],
        asset_relative_path=source_row["asset_path"],
        body_text=source_row["body_text"],
    )
    raw_source_path.write_text(raw_content, encoding="utf-8")

    page_stem = ensure_unique_stem(settings.wiki_sources_root, slug)
    wiki_source_path = settings.wiki_sources_root / f"{page_stem}.md"
    wiki_relative_path = wiki_source_path.relative_to(settings.repo_root).as_posix()
    wiki_note = build_wiki_source_note(
        title=source_row["title"],
        created=created_day,
        updated=created_day,
        tags=tags,
        source_url=source_row["source_url"],
        raw_relative_path=f"../../{raw_relative_path}",
        asset_relative_path=f"../../{source_row['asset_path']}" if source_row["asset_path"] else None,
        description=source_row["description"],
        body_text=source_row["body_text"],
    )
    wiki_source_path.write_text(wiki_note, encoding="utf-8")

    register_source_in_index(page_stem, source_row["title"], source_row["description"])
    append_log_entry(
        source_row["title"],
        [
            f"source_type: {source_row['source_type']}",
            f"raw: `{raw_relative_path}`",
            f"wiki: `{wiki_relative_path}`",
        ],
    )

    return {
        "raw_path": raw_relative_path,
        "wiki_path": wiki_relative_path,
    }


def _mark_job_processing(job_id: str, started_at: str):
    with get_connection() as connection:
        job_row = connection.execute(
            """
            SELECT source_id
            FROM jobs
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()
        if job_row is None:
            return None

        connection.execute(
            """
            UPDATE jobs
            SET status = ?, started_at = ?, detail = ?
            WHERE id = ?
            """,
            ("processing", started_at, "Background ingest in progress.", job_id),
        )
        connection.execute(
            """
            UPDATE sources
            SET status = ?
            WHERE id = ?
            """,
            ("processing", job_row["source_id"]),
        )
        source_row = connection.execute(
            """
            SELECT id, title, source_type, status, created_at, description,
                   source_url, tags_json, raw_path, wiki_path, asset_path, body_text
            FROM sources
            WHERE id = ?
            """,
            (job_row["source_id"],),
        ).fetchone()
        return source_row


def _mark_job_completed(
    *,
    job_id: str,
    source_id: str,
    completed_at: str,
    raw_path: str,
    wiki_path: str,
    detail: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE sources
            SET status = ?, raw_path = ?, wiki_path = ?
            WHERE id = ?
            """,
            ("completed", raw_path, wiki_path, source_id),
        )
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, completed_at = ?, detail = ?
            WHERE id = ?
            """,
            ("completed", completed_at, detail, job_id),
        )


def _mark_job_failed(
    *,
    job_id: str,
    source_id: str,
    completed_at: str,
    detail: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE sources
            SET status = ?
            WHERE id = ?
            """,
            ("failed", source_id),
        )
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, completed_at = ?, detail = ?
            WHERE id = ?
            """,
            ("failed", completed_at, detail, job_id),
        )


def list_sources() -> list[SourceSummary]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, source_type, status, created_at, description,
                   source_url, tags_json, raw_path, wiki_path, asset_path, body_text
            FROM sources
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [_to_source_summary(row) for row in rows]


def get_source(source_id: str) -> SourceSummary | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, source_type, status, created_at, description,
                   source_url, tags_json, raw_path, wiki_path, asset_path, body_text
            FROM sources
            WHERE id = ?
            """,
            (source_id,),
        ).fetchone()

    if row is None:
        return None

    return _to_source_summary(row)


def list_jobs() -> list[JobSummary]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, source_id, status, created_at, completed_at, detail
            FROM jobs
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        JobSummary(
            id=row["id"],
            source_id=row["source_id"],
            status=row["status"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
            detail=row["detail"],
        )
        for row in rows
    ]


def get_job(job_id: str) -> JobSummary | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, source_id, status, created_at, completed_at, detail
            FROM jobs
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()

    if row is None:
        return None

    return JobSummary(
        id=row["id"],
        source_id=row["source_id"],
        status=row["status"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
        detail=row["detail"],
    )


def _to_source_summary(row) -> SourceSummary:
    return SourceSummary(
        id=row["id"],
        title=row["title"],
        source_type=row["source_type"],
        status=row["status"],
        created_at=row["created_at"],
        description=row["description"],
        source_url=row["source_url"],
        tags=json.loads(row["tags_json"]),
        raw_path=row["raw_path"],
        wiki_path=row["wiki_path"],
        asset_path=row["asset_path"],
        body_text=row["body_text"],
    )
