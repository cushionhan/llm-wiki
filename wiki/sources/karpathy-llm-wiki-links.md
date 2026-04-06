---
title: Karpathy LLM Wiki Links
type: source
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
  - karpathy
sources:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - https://x.com/karpathy/status/2039805659525644595
---

# Karpathy LLM Wiki Links

## 요약

Karpathy의 gist는 `개인용 또는 팀용 지식베이스를 LLM이 직접 유지하는 markdown wiki` 패턴을 설명한다. X 포스트는 이 접근을 최근 매우 유용하게 쓰고 있으며, 토큰 사용의 큰 비중이 코드 조작에서 지식 조작으로 이동하고 있다는 문제의식을 공유한다.

## 핵심 주장

- 대부분의 문서 활용 경험은 RAG처럼 동작하지만, 그 방식은 질문할 때마다 지식을 다시 조립한다.
- 더 나은 방식은 `raw source`와 `질문 사이`에 구조화된 wiki 층을 두는 것이다.
- LLM은 새 소스가 들어올 때 인덱싱만 하는 것이 아니라 wiki 전체를 갱신해야 한다.
- 위키는 누적 자산이므로, 질문과 분석 결과도 다시 문서로 편입할 가치가 있다.

## gist에서 중요한 설계 포인트

- 3계층: raw sources, wiki, schema.
- 운영 루프: ingest, query, lint.
- 특별 파일: `index.md`, `log.md`.
- Obsidian은 browsing/graph view/IDE 역할을 한다.
- moderate scale에서는 인덱스 기반 탐색만으로도 상당히 잘 동작할 수 있다.

## X 포스트에서 읽히는 신호

- LLM 활용의 중심이 코드 생성에서 지식 구조화로 확장되고 있다.
- 이 패턴은 단순 요약이 아니라 `지속적으로 유지되는 개인 연구 환경`에 가깝다.
- 제품 관점으로 보면, 대화형 챗봇보다 `지식 컴파일러 + 유지보수자`에 더 가깝다.

## 이 저장소에 대한 적용

- 이 저장소는 Karpathy의 추상적 패턴을 실제 파일 구조로 고정한다.
- `AGENTS.md`는 schema 역할을 담당한다.
- `wiki/`는 장기 기억층이고, 채팅은 그 편집 인터페이스다.

## 참고 소스

- Gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- X: https://x.com/karpathy/status/2039805659525644595

## 연결 문서

- [[concepts/llm-wiki-pattern]]
- [[overview]]
