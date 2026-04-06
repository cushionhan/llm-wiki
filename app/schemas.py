from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


SourceType = Literal["url", "pdf", "image", "freeform_text", "meeting_note"]


class SourceSummary(BaseModel):
    id: str
    title: str
    source_type: SourceType
    status: str
    created_at: str
    description: str | None = None
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    raw_path: str
    wiki_path: str
    asset_path: str | None = None
    body_text: str | None = None


class JobSummary(BaseModel):
    id: str
    source_id: str
    status: str
    created_at: str
    completed_at: str | None = None
    detail: str | None = None


class SourceCreateResponse(BaseModel):
    source: SourceSummary
    job: JobSummary


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=10)


class PageMatch(BaseModel):
    path: str
    title: str
    score: int
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    related_pages: list[PageMatch]
    citations: list[str]
