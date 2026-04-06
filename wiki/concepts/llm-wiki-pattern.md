---
title: LLM Wiki Pattern
type: concept
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
  - obsidian
  - knowledge-base
sources:
  - karpathy-llm-wiki-links
---

# LLM Wiki Pattern

## 요약

`LLM Wiki` 패턴은 원문 파일을 그대로 검색하는 방식보다, LLM이 원문을 읽고 구조화된 markdown wiki를 지속적으로 갱신하도록 만드는 방식에 가깝다. 핵심은 질의 시점마다 지식을 재발견하는 것이 아니라, 지식을 미리 컴파일해 두고 계속 유지하는 것이다.

## 핵심 포인트

- 지식의 중심은 벡터 검색 결과가 아니라 `persistent artifact`로서의 wiki다.
- 원천 자료는 `raw/`에 불변으로 남긴다.
- LLM은 `wiki/`에 요약, 엔터티, 개념, 종합 문서를 작성하고 갱신한다.
- `AGENTS.md` 같은 schema 문서가 LLM의 행동 규칙을 정의한다.
- ingest, query, lint가 반복 루프를 형성한다.

## RAG와의 차이

- RAG는 질문이 들어올 때마다 원문 조각을 다시 찾아 결합한다.
- LLM wiki는 원문을 한 번 읽고 구조화된 지식층을 유지한다.
- 따라서 문서 간 연결, 상충 정보, 축적된 해석이 위키에 남는다.
- 중간 규모의 개인/팀 지식베이스에서는 이 방식이 더 생산적일 수 있다.

## 3계층 아키텍처

1. `raw/`: 원천 자료. LLM은 읽기만 하고 수정하지 않는다.
2. `wiki/`: LLM이 관리하는 markdown 지식층.
3. `AGENTS.md`: 위키 유지 규칙과 워크플로를 정의하는 schema.

## 운영 루프

### ingest

- 새 자료를 읽는다.
- source note를 만든다.
- 관련 개념/엔터티/요약 문서를 갱신한다.
- index와 log를 업데이트한다.

### query

- index에서 관련 페이지를 찾는다.
- 관련 페이지만 읽어 답한다.
- 재사용 가치가 있으면 종합 문서를 위키에 남긴다.

### lint

- 깨진 링크, 고립 페이지, 인덱스 누락, 상충 정보를 찾는다.
- 위키 구조를 정리하고 변경 사항을 로그에 남긴다.

## 이 저장소에 대한 시사점

- Obsidian은 탐색 인터페이스 역할을 한다.
- 이 저장소의 진짜 산출물은 채팅이 아니라 `wiki/`의 markdown 페이지들이다.
- 따라서 좋은 답변은 곧 좋은 문서여야 하며, 필요하면 즉시 파일로 남겨야 한다.

## 연결 문서

- [[overview]]
- [[sources/karpathy-llm-wiki-links]]
- [[log]]
