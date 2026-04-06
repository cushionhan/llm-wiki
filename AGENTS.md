# AGENTS.md

이 저장소는 Obsidian 문서 기반의 `LLM wiki`를 유지하기 위한 작업 공간이다. 이 파일의 목적은 에이전트를 일반 채팅 모델이 아니라 `지속적으로 축적되는 markdown 지식베이스의 유지보수자`로 동작시키는 것이다.

## 목표

- `raw/`의 원천 자료를 읽어 `wiki/`에 구조화된 지식을 축적한다.
- 질의 응답을 일회성 채팅으로 끝내지 않고 재사용 가능한 문서로 저장한다.
- 위키의 링크, 중복, 상충 정보, 고립 페이지를 지속적으로 정리한다.
- 모든 운영은 PowerShell 기반으로 진행한다.

## 저장소 계층

### 1. raw/

- 사용자가 수집한 원천 자료를 둔다.
- 원문 markdown, PDF, 이미지, 발췌 노트, 링크 목록을 포함할 수 있다.
- 이 계층은 불변으로 취급한다.
- 기존 raw 문서는 수정하지 말고, 필요하면 별도의 보충 문서를 새로 추가한다.

### 2. wiki/

- 에이전트가 관리하는 산출물 계층이다.
- 개요, 개념, 엔터티, source note, 종합 분석, 비교 문서를 저장한다.
- 가능한 한 서로 연결된 `[[wikilink]]` 구조를 유지한다.
- 지식이 바뀌면 기존 페이지를 갱신하고, 변화 이력은 `wiki/log.md`에 남긴다.

### 3. schema

- 현재 파일(`AGENTS.md`)이 schema 역할을 수행한다.
- 구조, 규칙, 명명법, ingest/query/lint 절차를 여기에 누적 개선한다.

## 디렉터리 규칙

- `wiki/index.md`: 전체 위키의 콘텐츠 인덱스. 새 페이지를 만들면 반드시 갱신한다.
- `wiki/log.md`: append-only 운영 로그. ingest/query/lint/scaffold 작업은 반드시 기록한다.
- `wiki/overview.md`: 전체 주제의 상위 개요 페이지.
- `wiki/sources/`: 원천 자료를 요약한 source note.
- `wiki/concepts/`: 개념, 방법론, 프레임워크 페이지.
- `wiki/entities/`: 인물, 조직, 도구, 프로젝트 같은 고유명사 페이지.
- `wiki/syntheses/`: 비교, 분석, Q&A 결과물, 보고서.

## 문서 작성 규약

- 파일명은 가능하면 ASCII 소문자 `kebab-case`를 사용한다.
- 문서 제목은 frontmatter의 `title`에 자연어로 적는다.
- 날짜는 `YYYY-MM-DD` 형식을 사용한다.
- 위키 문서는 가능하면 아래 frontmatter를 사용한다.

```yaml
---
title: 문서 제목
type: concept
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
sources: []
---
```

- 본문에는 가능한 한 다음 섹션 중 필요한 것만 사용한다.
  - `## 요약`
  - `## 핵심 포인트`
  - `## 연결 문서`
  - `## 열린 질문`
  - `## 참고 소스`

## 링크 규칙

- Obsidian wikilink `[[page-name]]`를 우선 사용한다.
- 섹션 링크가 필요하면 `[[page-name#section]]`을 사용한다.
- 같은 개념이 여러 곳에서 반복되면 새 개념 페이지를 만들고 기존 페이지에서 링크한다.
- 새 페이지를 만들었는데 inbound link가 없으면 관련 페이지에서 반드시 연결한다.

## 운영 절차

### Ingest

새 원천 자료를 반영할 때는 다음 순서를 따른다.

1. `raw/`에서 새 자료를 읽는다.
2. `wiki/sources/`에 source note를 만든다.
3. 기존 `wiki/` 페이지 중 영향을 받는 페이지를 찾는다.
4. 개요/개념/엔터티/종합 문서를 갱신한다.
5. `wiki/index.md`에 새 페이지를 등록하거나 설명을 갱신한다.
6. `wiki/log.md`에 작업 내역을 append 한다.

### Query

- 질의에 답할 때는 먼저 `wiki/index.md`를 보고 관련 페이지를 찾는다.
- 필요한 페이지만 읽어 답변한다.
- 장기적으로 가치 있는 답변이라면 `wiki/syntheses/`에 새 문서로 저장한다.
- 저장한 경우 `wiki/index.md`와 `wiki/log.md`를 함께 갱신한다.

### Lint

- 정기적으로 `scripts/Test-Wiki.ps1`를 실행해 깨진 링크, 인덱스 누락, 고립 페이지를 찾는다.
- 오래된 주장, 상충 정보, 연결 누락을 점검한다.
- lint 결과로 바뀐 내용은 `wiki/log.md`에 기록한다.

## PowerShell 우선 원칙

- 탐색과 보조 작업은 PowerShell로 수행한다.
- 텍스트 검색은 `rg`가 없으면 `Select-String`을 사용한다.
- 이 저장소의 보조 스크립트는 모두 `scripts/*.ps1`에 둔다.

## 첫 세션 기준 운영 방침

- 현재 저장소는 Karpathy의 `LLM Wiki` 아이디어를 출발점으로 삼는다.
- 초기 위키에는 해당 아이디어의 요약, 아키텍처, 구현 방향을 seed knowledge로 넣는다.
- 이후 사용자가 제공하는 실제 원천 자료를 `raw/`에 축적하면서 주제별 wiki로 확장한다.
