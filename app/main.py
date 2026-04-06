from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import ensure_runtime_directories, settings
from app.db import initialize_database
from app.schemas import QueryRequest, QueryResponse, SourceCreateResponse, SourceSummary
from app.services.job_runner import enqueue_job, start_job_runner, stop_job_runner
from app.services.query_service import query_wiki
from app.services.source_service import create_source, get_job, get_source, list_jobs, list_sources
from app.services.wiki_service import list_wiki_pages


app = FastAPI(
    title="idai server",
    version="0.1.0",
    description="Obsidian 문서 기반 LLM wiki를 위한 서버 MVP",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_root), name="static")
templates = Jinja2Templates(directory=str(settings.templates_root))


@app.on_event("startup")
async def startup_event() -> None:
    ensure_runtime_directories()
    initialize_database()
    start_job_runner()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    stop_job_runner()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "recent_sources": list_sources()[:10],
            "wiki_pages": list_wiki_pages()[:20],
        },
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/sources", response_model=SourceCreateResponse)
async def create_source_endpoint(
    title: str = Form(...),
    source_type: str = Form(...),
    description: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    body_text: str | None = Form(default=None),
    upload: UploadFile | None = File(default=None),
) -> SourceCreateResponse:
    if source_type not in {"url", "pdf", "image", "freeform_text", "meeting_note"}:
        raise HTTPException(status_code=400, detail="Unsupported source_type")

    if source_type in {"pdf", "image"} and upload is None:
        raise HTTPException(status_code=400, detail="File upload is required for this source_type")

    if source_type == "url" and not source_url:
        raise HTTPException(status_code=400, detail="source_url is required for url source_type")

    response = await create_source(
        title=title,
        source_type=source_type,
        description=description,
        source_url=source_url,
        tags_raw=tags,
        body_text=body_text,
        upload=upload,
    )
    enqueue_job(response.job.id)
    return response


@app.get("/api/sources", response_model=list[SourceSummary])
async def list_sources_endpoint() -> list[SourceSummary]:
    return list_sources()


@app.get("/api/sources/{source_id}", response_model=SourceSummary)
async def get_source_endpoint(source_id: str) -> SourceSummary:
    source = get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@app.get("/api/jobs")
async def list_jobs_endpoint() -> list[dict]:
    return [job.model_dump() for job in list_jobs()]


@app.get("/api/jobs/{job_id}")
async def get_job_endpoint(job_id: str) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump()


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest) -> QueryResponse:
    return query_wiki(payload.query, payload.limit)


@app.get("/api/wiki/pages")
async def list_wiki_pages_endpoint() -> list[dict[str, str]]:
    return list_wiki_pages()
