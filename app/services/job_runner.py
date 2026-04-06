from __future__ import annotations

import queue
import threading
from typing import Final

from app.db import get_connection
from app.services.source_service import process_job


_JOB_QUEUE: Final[queue.Queue[str]] = queue.Queue()
_STOP_EVENT = threading.Event()
_WORKER_THREAD: threading.Thread | None = None


def start_job_runner() -> None:
    global _WORKER_THREAD

    if _WORKER_THREAD is not None and _WORKER_THREAD.is_alive():
        return

    _STOP_EVENT.clear()
    _WORKER_THREAD = threading.Thread(
        target=_worker_loop,
        name="idai-job-runner",
        daemon=True,
    )
    _WORKER_THREAD.start()
    _enqueue_incomplete_jobs()


def stop_job_runner() -> None:
    _STOP_EVENT.set()
    _JOB_QUEUE.put("__shutdown__")


def enqueue_job(job_id: str) -> None:
    _JOB_QUEUE.put(job_id)


def _enqueue_incomplete_jobs() -> None:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id
            FROM jobs
            WHERE status IN ('queued', 'processing')
            ORDER BY created_at ASC
            """
        ).fetchall()

    for row in rows:
        _JOB_QUEUE.put(row["id"])


def _worker_loop() -> None:
    while not _STOP_EVENT.is_set():
        try:
            job_id = _JOB_QUEUE.get(timeout=0.5)
        except queue.Empty:
            continue

        if job_id == "__shutdown__":
            _JOB_QUEUE.task_done()
            continue

        try:
            process_job(job_id)
        finally:
            _JOB_QUEUE.task_done()
