---
title: Implementation Blueprint
type: synthesis
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
  - implementation
  - obsidian
sources:
  - karpathy-llm-wiki-links
---

# Implementation Blueprint

## 목표 해석

이 스레드의 목표는 Karpathy가 제시한 `LLM이 유지하는 markdown wiki` 패턴을 Obsidian 친화적인 파일 구조와 운영 규칙으로 구체화하는 것이다. 여기서 동일한 수준이 의미하는 것은 단순히 문서를 모아두는 것이 아니라, 아래 조건을 만족하는 시스템을 만드는 것이다.

1. 원천 자료와 파생 지식을 분리할 것
2. wiki 자체가 지속적으로 갱신되는 장기 자산일 것
3. 질의 결과가 필요하면 다시 wiki에 편입될 것
4. 운영 규약이 명시되어 LLM이 세션이 바뀌어도 같은 방식으로 일할 것

## 링크 분석 핵심

### gist

- 핵심 메시지는 `RAG 대신 persistent wiki`다.
- 새 소스는 인덱싱만 하는 것이 아니라 기존 wiki 전체에 통합되어야 한다.
- schema 문서가 없으면 LLM은 일관된 maintainer로 동작하기 어렵다.
- `index.md`와 `log.md`가 moderate scale에서 중요한 운영 허브가 된다.

### X 포스트

- LLM의 용도가 코드 생성만이 아니라 지식 조작과 구조화로 이동하고 있다는 신호다.
- 제품 관점에서는 채팅창보다 `지식 컴파일러` 역할이 더 중요해진다.

## 현재 구현 범위

현재 저장소에는 다음이 준비되어 있다.

- `raw/`: 원천 자료 계층
- `wiki/`: 개요, 개념, source note, index, log
- `AGENTS.md`: 운영 스키마
- `scripts/*.ps1`: 검색, 최근 로그, 위키 검사, 새 소스 스캐폴딩

즉, 지금은 `수동 ingest + 구조화된 유지보수`가 가능한 0.1 버전이다.

## 현재 설계가 Karpathy 패턴과 맞닿는 지점

- Obsidian이 읽기/탐색 인터페이스를 맡는다.
- LLM은 `wiki/`를 직접 수정하는 maintainer 역할을 맡는다.
- raw는 불변 계층으로 분리되어 있다.
- 질의와 분석도 축적 가능한 문서로 간주한다.

## 아직 없는 것

다음 요소는 아직 수동 또는 미구현 상태다.

- raw source를 자동으로 source note로 변환하는 ingest 파이프라인
- concept/entity page 자동 갱신 규칙의 세분화
- 본문/메타데이터 수준의 검색 강화
- 주기적 lint 자동화
- PDF/이미지 같은 비텍스트 source에 대한 정형 처리

## 다음 구현 우선순위

1. ingest 프로토콜 고도화
   - raw source 유형별 템플릿을 정의한다.
   - source note 생성 규칙을 더 구체화한다.
2. 문서 타입 확장
   - entity, timeline, comparison, open-questions 문서 템플릿을 추가한다.
3. 검색 보강
   - 현재는 index + text search만 사용한다.
   - 규모가 커지면 markdown 검색 인덱스를 붙인다.
4. lint 강화
   - 깨진 링크 외에 중복 개념, 오래된 주장, 출처 미기재 문서를 점검한다.

## 운영 원칙

- 채팅은 임시 인터페이스이고, 최종 산출물은 파일이다.
- 가치 있는 분석은 `wiki/syntheses/`에 남긴다.
- 새 문서가 생기면 index와 log를 반드시 갱신한다.
- 위키 품질은 문서 수보다 연결성과 갱신성으로 평가한다.

## 연결 문서

- [[overview]]
- [[concepts/llm-wiki-pattern]]
- [[sources/karpathy-llm-wiki-links]]
- [[log]]
