from __future__ import annotations

import re
from pathlib import Path

from app.config import settings
from app.schemas import PageMatch, QueryResponse
from app.services.wiki_service import extract_title


def tokenize_query(query: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9가-힣]+", query.lower()) if len(token) > 1]


def strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content

    lines = content.splitlines()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :])
    return content


def build_excerpt(content: str, tokens: list[str]) -> str:
    body = strip_frontmatter(content)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    for token in tokens:
        for line in lines:
            if token in line.lower():
                return line[:220]
    for line in lines:
        if not line.startswith("#"):
            return line[:220]
    return ""


def score_page(path: Path, query: str, tokens: list[str]) -> tuple[int, str]:
    content_raw = path.read_text(encoding="utf-8")
    content = strip_frontmatter(content_raw).lower()
    title = extract_title(path).lower()

    if not tokens:
        score = content.count(query.lower())
    else:
        score = sum(content.count(token) for token in tokens)
        score += sum(title.count(token) * 3 for token in tokens)

    excerpt = build_excerpt(content_raw, tokens or [query.lower()])
    return score, excerpt


def query_wiki(query: str, limit: int) -> QueryResponse:
    tokens = tokenize_query(query)
    matches: list[PageMatch] = []

    for path in settings.wiki_root.rglob("*.md"):
        score, excerpt = score_page(path, query, tokens)
        if score <= 0:
            continue

        matches.append(
            PageMatch(
                path=path.relative_to(settings.repo_root).as_posix(),
                title=extract_title(path),
                score=score,
                excerpt=excerpt,
            )
        )

    matches.sort(key=lambda item: item.score, reverse=True)
    top_matches = matches[:limit]

    if not top_matches:
        return QueryResponse(
            answer="현재 wiki에서 관련 문서를 찾지 못했습니다. 새 source를 ingest하거나 query 문구를 더 구체화하는 편이 좋습니다.",
            related_pages=[],
            citations=[],
        )

    answer_lines = [f"'{query}' 기준으로 wiki에서 관련도가 높은 문서 {len(top_matches)}개를 찾았습니다."]
    for match in top_matches:
        answer_lines.append(f"- {match.title}: {match.excerpt}")

    return QueryResponse(
        answer="\n".join(answer_lines),
        related_pages=top_matches,
        citations=[match.path for match in top_matches],
    )
