from __future__ import annotations

import subprocess
from pathlib import Path

from app.config import settings


def maybe_commit_ingest(paths: list[str], title: str) -> str:
    git_dir = settings.repo_root / ".git"
    if not git_dir.exists():
        return "Git commit skipped: repository is not initialized."

    try:
        inside_repo = run_git(["rev-parse", "--is-inside-work-tree"])
    except RuntimeError as error:
        return f"Git commit skipped: {error}"

    if inside_repo.strip().lower() != "true":
        return "Git commit skipped: working directory is not inside a Git repository."

    repo_relative_paths = [path for path in paths if path]
    if not repo_relative_paths:
        return "Git commit skipped: no paths were provided."

    try:
        run_git(["add", "--", *repo_relative_paths])
        staged = run_git(["diff", "--cached", "--name-only", "--", *repo_relative_paths]).strip()
        if not staged:
            return "Git commit skipped: no staged changes for ingest output."

        commit_message = f"ingest: {title}"
        run_git(["commit", "-m", commit_message])
        return f"Git commit created: {commit_message}"
    except RuntimeError as error:
        return f"Git commit skipped: {error}"


def run_git(arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=settings.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise RuntimeError(stderr)
    return completed.stdout
