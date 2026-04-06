---
title: Process Diagrams
type: synthesis
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
  - process
  - mermaid
sources:
  - karpathy-llm-wiki-links
---

# Process Diagrams

## 요약

이 문서는 현재 저장소의 처리과정을 `ingest`, `query`, `lint` 세 루프로 나누어 시퀀스 다이어그램으로 정리한다. 개요도보다 더 중요한 점은, 각 단계에서 어떤 파일이 갱신되고 어떤 판단이 필요한지를 명확히 고정하는 것이다.

## Ingest Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as "사용자"
    participant Raw as "raw/"
    participant Agent as "LLM Agent"
    participant Rules as "AGENTS.md"
    participant Source as "wiki/sources/"
    participant Concept as "wiki/concepts/"
    participant Entity as "wiki/entities/"
    participant Index as "wiki/index.md"
    participant Log as "wiki/log.md"

    User->>Raw: 새 원천 자료 추가
    User->>Agent: ingest 요청
    Agent->>Rules: 문서 규약/명명 규칙 확인
    Agent->>Raw: 원문 읽기
    Agent->>Source: source note 생성 또는 갱신
    Agent->>Concept: 관련 개념 문서 생성 또는 갱신
    Agent->>Entity: 관련 엔터티 문서 생성 또는 갱신
    Agent->>Index: 새 문서 등록 및 설명 갱신
    Agent->>Log: 작업 이력 append
```

### Ingest 판단 기준

- 새 source note가 필요한가, 기존 source note를 확장하면 되는가
- 이번 자료가 새 concept/entity 문서를 만들 정도로 독립적인가
- 기존 주장과 충돌하는 내용이 있는가
- index에 어떤 설명으로 노출해야 재검색 비용이 줄어드는가

## Query Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as "사용자"
    participant Agent as "LLM Agent"
    participant Rules as "AGENTS.md"
    participant Index as "wiki/index.md"
    participant Wiki as "wiki/*"
    participant Synth as "wiki/syntheses/"
    participant Log as "wiki/log.md"

    User->>Agent: 질문
    Agent->>Rules: query 원칙 확인
    Agent->>Index: 관련 문서 후보 찾기
    Agent->>Wiki: 필요한 페이지만 읽기
    Agent-->>User: 위키 기반 답변
    alt 장기 보존 가치가 높음
        Agent->>Synth: 분석/Q&A 문서 저장
        Agent->>Index: 새 synthesis 등록
        Agent->>Log: query 결과 저장 이력 append
    else 일회성 답변
        Agent->>Log: 필요 시 질의 처리만 기록
    end
```

### Query 판단 기준

- raw를 다시 읽어야 하는지, 현재 wiki만으로 충분한지
- 답변이 일회성인지, 재사용 가치가 높은 synthesis인지
- 새 synthesis가 기존 문서를 대체하는지, 보완하는지

## Lint Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as "사용자"
    participant Script as "scripts/Test-Wiki.ps1"
    participant Wiki as "wiki/*"
    participant Index as "wiki/index.md"
    participant Agent as "LLM Agent"
    participant Log as "wiki/log.md"

    User->>Script: lint 실행
    Script->>Wiki: markdown 파일 수집
    Script->>Wiki: wikilink 스캔
    Script->>Index: index 수록 여부 확인
    Script-->>User: broken link / index 누락 / orphan page 보고
    alt 수정 필요
        User->>Agent: lint 결과 수정 요청
        Agent->>Wiki: 링크/문서 구조 수정
        Agent->>Index: 인덱스 보정
        Agent->>Log: lint 수정 이력 append
    else 이상 없음
        Script-->>User: clean 상태 보고
    end
```

### Lint 판단 기준

- 문서가 존재하지만 index에서 빠져 있는가
- 어느 페이지도 가리키지 않는 orphan 문서가 있는가
- 깨진 링크가 실제 오타인지, 아직 만들 페이지인지
- 구조상 concept/entity/source/synthesis 배치가 적절한가

## 전체 운영 의미

- ingest는 `새 지식을 위키에 편입`하는 단계다.
- query는 `축적된 위키를 사용`하는 단계다.
- lint는 `위키를 계속 읽기 좋은 상태로 유지`하는 단계다.

세 루프가 모두 돌아야 이 프로젝트는 단순 노트 저장소가 아니라 `LLM이 유지하는 지식 시스템`이 된다.

## 연결 문서

- [[overview]]
- [[concepts/llm-wiki-pattern]]
- [[syntheses/implementation-blueprint]]
- [[log]]
