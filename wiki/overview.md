---
title: Obsidian LLM Wiki Overview
type: overview
status: active
created: 2026-04-06
updated: 2026-04-06
tags:
  - llm-wiki
  - obsidian
sources:
  - karpathy-llm-wiki-links
---

# Obsidian LLM Wiki Overview

## 요약

이 저장소는 Obsidian을 브라우저/IDE로 사용하고, LLM이 markdown wiki 자체를 관리하는 구조를 목표로 한다. 질문 시점에만 원문을 검색하는 RAG 중심 흐름이 아니라, `raw/` 자료를 읽은 뒤 `wiki/`에 구조화된 지식을 축적하고 유지하는 흐름이 중심이다.

## 핵심 원칙

1. 원천 자료와 파생 지식을 분리한다.
2. 위키는 지속적으로 갱신되는 장기 자산으로 다룬다.
3. 답변도 필요하면 문서로 남겨 축적한다.
4. 링크, 상충 정보, 고립 페이지를 정기적으로 점검한다.

## 현재 seed knowledge

- [[sources/karpathy-llm-wiki-links]]
- [[concepts/llm-wiki-pattern]]

## 구현 방향

- 초기 단계에서는 `index.md` 기반 탐색과 PowerShell 보조 스크립트로 충분히 운영한다.
- 위키가 커지면 로컬 검색 또는 hybrid search 도구를 추가할 수 있다.
- 쿼리 결과 중 재사용 가치가 높은 내용은 `wiki/syntheses/`에 저장한다.

## 다음 단계

- 실제 연구 주제나 업무 도메인별 raw source를 추가한다.
- source note와 concept/entity page를 점진적으로 확장한다.
- lint 루프를 통해 링크 일관성과 문서 구조를 관리한다.
