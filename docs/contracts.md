# Normalized event contract

Provider adapters emit immutable Python events from `agent_core`. Channel adapters consume only those events and must not depend on provider SDK response objects.

The cross-language transport contract is [agent-event-v1.schema.json](../schemas/agent-event-v1.schema.json). Use `event_to_dict()` when passing an event to a framework serializer and `event_to_json()` when a JSON string is required, such as an SSE data field.

## Stream rules

1. Events retain provider emission order.
2. `StatusEvent` describes observable application work, never hidden model reasoning.
3. `TextDeltaEvent.accumulated_text` contains every text delta emitted so far.
4. Structured results remain typed through the provider and transport boundaries.
5. A successful stream emits `FinalTextEvent` before `DoneEvent(reason="completed")`.
6. A cancelled stream ends with `DoneEvent(reason="cancelled")` and does not emit final text afterward.
7. A failed stream emits one user-safe `ErrorEvent`, then `DoneEvent(reason="error")`.
8. Every stream emits exactly one `DoneEvent`, and no events follow it.

## Rendering rule

Do not call `str()` on dictionaries, provider objects, or structured results, and do not newline-join heterogeneous result items. A channel renderer must handle each known event and structured-result kind explicitly. Unknown schema versions or result kinds must produce a user-safe fallback or error rather than an object representation.

## Versioning

The event discriminator is the `type` property. Structured results also carry `kind` and `schema_version` so their payloads can evolve independently.

Additive optional fields may be introduced in a new schema revision after all consumers tolerate them. Removing fields, changing their meaning, or changing allowed values requires a new major event schema. Provider-specific fields stay inside provider adapters and are not added to the normalized contract.

## Structured results

Version 1 defines three result kinds:

- `reconciliation_summary` contains summary metrics and key-value facts.
- `table` contains ordered column definitions and rows with one string cell per column. `truncated` tells renderers that the provider omitted additional rows.
- `status_summary` contains an overall workflow state and ordered item states with optional user-safe details.

The event `kind` and payload type are correlated in Python and JSON Schema. Renderers must switch on `kind`, verify `schema_version`, and provide a text fallback when they cannot render a supported structured result.
