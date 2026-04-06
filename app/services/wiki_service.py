from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from app.config import settings


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "source"


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def split_tags(raw_tags: str | None) -> list[str]:
    if not raw_tags:
        return []
    tags = [tag.strip() for tag in raw_tags.split(",")]
    return [tag for tag in tags if tag]


def ensure_unique_stem(directory: Path, base_stem: str) -> str:
    candidate = base_stem
    counter = 2
    while (directory / f"{candidate}.md").exists():
        candidate = f"{base_stem}-{counter}"
        counter += 1
    return candidate


def insert_line_into_section(file_path: Path, section_heading: str, line_to_insert: str) -> None:
    content = file_path.read_text(encoding="utf-8")
    if line_to_insert in content:
        return

    lines = content.splitlines()
    section_index = next(
        (index for index, line in enumerate(lines) if line.strip() == section_heading),
        None,
    )
    if section_index is None:
        lines.append("")
        lines.append(section_heading)
        lines.append("")
        lines.append(line_to_insert)
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    insert_at = len(lines)
    for index in range(section_index + 1, len(lines)):
        if lines[index].startswith("## "):
            insert_at = index
            if index > section_index + 1 and not lines[index - 1].strip():
                insert_at = index - 1
            break

    lines.insert(insert_at, line_to_insert)
    if (
        insert_at + 1 < len(lines)
        and lines[insert_at + 1].startswith("## ")
    ):
        lines.insert(insert_at + 1, "")
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_log_entry(title: str, bullets: list[str]) -> None:
    log_path = settings.wiki_root / "log.md"
    today = datetime.now().strftime("%Y-%m-%d")

    entry_lines = ["", f"## [{today}] ingest | {title}", ""]
    entry_lines.extend(f"- {bullet}" for bullet in bullets)
    log_path.write_text(
        log_path.read_text(encoding="utf-8") + "\n".join(entry_lines) + "\n",
        encoding="utf-8",
    )


def build_raw_source_markdown(
    *,
    title: str,
    source_type: str,
    created: str,
    tags: list[str],
    description: str | None,
    source_url: str | None,
    asset_relative_path: str | None,
    body_text: str | None,
) -> str:
    tag_lines = "\n".join(f"  - {tag}" for tag in tags) if tags else "  - inbox"
    description_line = description.strip() if description else ""
    body = body_text.strip() if body_text else ""

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"kind: {source_type}",
        f"created: {created}",
        "status: inbox",
    ]

    if source_url:
        lines.extend(
            [
                "links:",
                f"  - {source_url}",
            ]
        )
    else:
        lines.append("links: []")

    lines.extend(
        [
            "tags:",
            tag_lines,
            "---",
            "",
            f"# {title}",
            "",
            "## Source Info",
            "",
            f"- kind: {source_type}",
            f"- created: {created}",
        ]
    )

    if source_url:
        lines.append(f"- source_url: {source_url}")
    if asset_relative_path:
        lines.append(f"- asset_path: {asset_relative_path}")

    lines.extend(["", "## Summary", ""])
    if description_line:
        lines.append(description_line)

    lines.extend(["", "## Notes", ""])
    if body:
        lines.append(body)

    lines.extend(["", "## Extraction TODO", "", "- [ ] source note 생성", "- [ ] 관련 wiki 페이지 갱신", "- [ ] index/log 반영"])

    return "\n".join(lines) + "\n"


def build_wiki_source_note(
    *,
    title: str,
    created: str,
    updated: str,
    tags: list[str],
    source_url: str | None,
    raw_relative_path: str,
    asset_relative_path: str | None,
    description: str | None,
    body_text: str | None,
) -> str:
    summary = (description or body_text or "업로드 시점 메타데이터 기반 초안입니다.").strip()
    summary = summary[:500]
    tag_lines = "\n".join(f"  - {tag}" for tag in (tags or ["llm-wiki"]))

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        "type: source",
        "status: draft",
        f"created: {created}",
        f"updated: {updated}",
        "tags:",
        tag_lines,
    ]

    if source_url:
        lines.extend(
            [
                "sources:",
                f"  - {source_url}",
            ]
        )
    else:
        lines.append("sources: []")

    lines.extend(
        [
            "---",
            "",
            f"# {title}",
            "",
            "## 요약",
            "",
            summary,
            "",
            "## 원천 정보",
            "",
            f"- raw source: [{raw_relative_path}]({raw_relative_path})",
        ]
    )

    if source_url:
        lines.append(f"- source url: {source_url}")
    if asset_relative_path:
        lines.append(f"- asset: [{asset_relative_path}]({asset_relative_path})")

    lines.extend(
        [
            "",
            "## 핵심 포인트",
            "",
            "- 이 문서는 업로드 직후 생성된 초안 source note다.",
            "- 이후 ingest가 고도화되면 개념/엔터티 문서와 더 강하게 연결된다.",
            "",
            "## 연결 문서",
            "",
            "- [[overview]]",
            "- [[log]]",
        ]
    )

    return "\n".join(lines) + "\n"


def register_source_in_index(page_stem: str, title: str, description: str | None) -> None:
    index_path = settings.wiki_root / "index.md"
    short_description = (description or "업로드된 원천 자료에서 생성된 source note").strip()
    short_description = short_description.replace("\n", " ")
    line = f"- [[sources/{page_stem}]]: {title} | {short_description[:80]}"
    insert_line_into_section(index_path, "## Sources", line)


def list_wiki_pages() -> list[dict[str, str]]:
    pages: list[dict[str, str]] = []
    for path in sorted(settings.wiki_root.rglob("*.md")):
        relative_path = path.relative_to(settings.wiki_root).as_posix()
        title = extract_title(path)
        pages.append({"path": relative_path, "title": title})
    return pages


def extract_title(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    frontmatter_title = re.search(r'^title:\s+"?(.+?)"?$', content, flags=re.MULTILINE)
    if frontmatter_title:
        return frontmatter_title.group(1)

    heading = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    return heading.group(1) if heading else path.stem
