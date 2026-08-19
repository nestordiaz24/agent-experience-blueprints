# ADR 0001: Use a normalized asynchronous event stream

- Status: Accepted
- Date: 2026-08-19

## Context

Provider SDKs expose different response, streaming, citation, and structured-output shapes. Passing those objects directly into web or Teams delivery code couples presentation to a provider and encourages untyped string rendering.

## Decision

Providers implement one asynchronous stream contract and emit immutable channel-independent events. Events distinguish operational status, cumulative text state, citations, structured results, final text, user-safe errors, and completion.

Operational statuses describe observable application work only. They never expose or imitate hidden model reasoning. Every stream ends with exactly one `DoneEvent`, including cancellation and error paths.

## Consequences

- Web and Teams adapters can consume the same provider stream.
- Provider-specific objects remain inside adapters.
- Structured results remain typed until a channel renderer converts them.
- Contract tests are required for event ordering, cancellation, errors, and terminal behavior.
