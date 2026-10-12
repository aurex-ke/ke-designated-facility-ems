# ADR 0001: Record architecture decisions

- Status: Accepted
- Date: 2026-10-13

## Context

The project is a reference implementation intended for open-source readers. Readers and future contributors need to know why choices were made, not only what was built. Many facts here (regulations, licences, tariffs) change over time.

## Decision

Record each significant architecture decision as a short Markdown file in `docs/adr/`, numbered in order. Each record states status, date, context, decision, consequences and open points. A decision that is replaced is marked superseded, not deleted.

## Consequences

- Decisions stay traceable and reviewable in git history.
- Each ADR adds a small writing cost. Only decisions that are hard to reverse or affect several components get one.
