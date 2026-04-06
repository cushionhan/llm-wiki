---
title: Wiki Log
type: log
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
sources: []
---

# Wiki Log

`## [YYYY-MM-DD] action | title` 형식을 유지합니다.

## [2026-04-06] scaffold | initial obsidian llm wiki bootstrap

- `raw/`, `wiki/`, `scripts/` 구조를 생성했다.
- `AGENTS.md`로 운영 스키마를 정의했다.
- Karpathy의 gist/X 링크를 초기 seed source로 등록했다.
- 초기 개요/개념/source note/index를 작성했다.

## [2026-04-06] synthesis | implementation blueprint

- 링크 분석 결과를 구현 청사진 문서로 정리했다.
- 현재 저장소가 어느 수준까지 구현되었고 다음 단계가 무엇인지 명시했다.

## [2026-04-06] synthesis | process diagrams

- 프로젝트 처리과정을 ingest, query, lint 기준 시퀀스 다이어그램으로 정리했다.
- Obsidian에서 바로 볼 수 있도록 mermaid 문법으로 문서화했다.

## [2026-04-06] synthesis | application architecture

- 웹 업로드 UI, 앱 서버, ingest worker, git 저장소, Obsidian 연동을 포함한 시스템 아키텍처를 정리했다.
- single-writer ingest, query 우선순위, 바이너리 자산 처리 원칙을 문서에 명시했다.

## [2026-04-06] scaffold | fastapi server mvp

- FastAPI 기반 업로드 UI와 source/query API를 추가했다.
- 업로드 시 `raw/sources/`, `wiki/sources/`, `wiki/index.md`, `wiki/log.md`를 갱신하는 동기식 ingest를 구현했다.
- SQLite 메타데이터 저장소와 PowerShell 실행 스크립트를 추가했다.

## [2026-04-06] refactor | background ingest worker

- source 업로드를 `queued -> processing -> completed/failed` job 구조로 바꿨다.
- 앱 시작 시 백그라운드 worker가 실행되고, 미완료 job을 자동으로 재큐잉한다.
- `.git` 저장소가 있을 경우 ingest 결과 파일만 선택적으로 자동 commit 시도하도록 훅을 추가했다.

## [2026-04-06] ingest | End-to-End Pipeline Validation 2026-04-06

- source_type: freeform_text
- raw: `raw/sources/2026-04-06-end-to-end-pipeline-validation-2026-04-06-f105f5dd/source.md`
- wiki: `wiki/sources/end-to-end-pipeline-validation-2026-04-06.md`
