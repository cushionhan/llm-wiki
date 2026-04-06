# idai

Obsidian 문서 기반 LLM wiki를 위한 파일 우선(file-first) 저장소입니다.

이 저장소의 목적은 Karpathy의 `LLM Wiki` 아이디어를 실제 운영 가능한 형태로 구체화하는 것입니다. 핵심은 질문 시점마다 원문을 다시 벡터 검색하는 것이 아니라, LLM이 `raw/`의 원천 자료를 읽고 `wiki/`에 구조화된 지식을 지속적으로 축적하고 유지하는 것입니다.

## 구조

- `raw/`: 원천 자료 보관소. 원문, 클리핑, 노트, 이미지 등. 불변(immutable) 계층입니다.
- `wiki/`: LLM이 관리하는 markdown wiki. 요약, 엔터티, 개념, 종합 분석, 인덱스, 로그가 위치합니다.
- `scripts/`: PowerShell 기반 보조 도구. 검색, 최근 로그 조회, 위키 검사, 소스 스캐폴딩에 사용합니다.
- `AGENTS.md`: 이 저장소에서 에이전트가 wiki를 어떻게 유지해야 하는지 정의하는 운영 스키마입니다.

## 기본 운영 루프

1. 새 자료를 `raw/`에 넣습니다.
2. LLM에게 ingest를 요청합니다.
3. LLM은 `wiki/`의 요약/개념/인덱스/로그를 갱신합니다.
4. 질의 결과 중 장기 가치가 있는 내용은 `wiki/`에 다시 저장합니다.
5. 주기적으로 `scripts/Test-Wiki.ps1`로 링크/인덱스/고립 페이지를 점검합니다.

## 시작 파일

- [AGENTS.md](D:\git\idai\AGENTS.md)
- [wiki/index.md](D:\git\idai\wiki\index.md)
- [wiki/log.md](D:\git\idai\wiki\log.md)
- [wiki/overview.md](D:\git\idai\wiki\overview.md)
- [wiki/concepts/llm-wiki-pattern.md](D:\git\idai\wiki\concepts\llm-wiki-pattern.md)
- [wiki/sources/karpathy-llm-wiki-links.md](D:\git\idai\wiki\sources\karpathy-llm-wiki-links.md)

## PowerShell 도구

```powershell
.\scripts\Search-Wiki.ps1 -Query "Karpathy"
.\scripts\Get-RecentLog.ps1 -Count 10
.\scripts\Test-Wiki.ps1
.\scripts\New-RawSource.ps1 -Title "Example article"
```

## Obsidian 사용

이 폴더 전체를 Obsidian vault로 열면 됩니다. `wiki/index.md`를 시작점으로 사용하고, `graph view`로 연결 구조를 확인하는 것을 권장합니다.

## 서버 MVP

현재 저장소에는 FastAPI 기반의 서버 MVP도 포함되어 있습니다.

- 업로드 페이지: `/`
- source 등록 API: `POST /api/sources`
- source 목록 API: `GET /api/sources`
- job 조회 API: `GET /api/jobs/{job_id}`
- query API: `POST /api/query`
- wiki 페이지 목록 API: `GET /api/wiki/pages`

### 서버 실행

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\scripts\Run-Server.ps1 -Reload
```

기본 주소는 `http://127.0.0.1:8000`입니다.

### 현재 MVP 동작 범위

- 원천 자료를 웹 폼에서 업로드할 수 있습니다.
- 업로드 요청은 우선 job으로 큐에 들어가고, 백그라운드 worker가 ingest를 처리합니다.
- ingest 완료 시 `raw/sources/`에 텍스트 source 파일이 생성됩니다.
- 업로드 메타데이터를 바탕으로 `wiki/sources/`에 초안 source note가 생성됩니다.
- `wiki/index.md`, `wiki/log.md`가 자동으로 갱신됩니다.
- query API는 현재 `wiki/` 문서를 검색해 관련 페이지와 발췌를 반환합니다.

### 설계 메모

- 대형 바이너리 자산은 Git 대신 `storage/` 아래에 저장됩니다.
- 텍스트성 위키와 raw 문서는 계속 repo 안에서 관리됩니다.
- ingest는 현재 내장 worker가 처리합니다.
- `.git` 저장소가 존재하면 ingest 완료 후 관련 파일만 자동으로 commit을 시도합니다.
