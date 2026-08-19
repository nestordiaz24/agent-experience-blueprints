# Agent Experience Blueprints - Implementation Plan

## 1. Purpose

Build a public reference repository that demonstrates two complementary patterns:

1. An embeddable chat experience for an existing web application using an application-owned UI and Microsoft 365 Copilot Chat API.
2. A responsive Microsoft Foundry agent experience in Microsoft Teams using progress updates, response streaming, Teams-safe Markdown, and Adaptive Cards.

The repository must contain only synthetic examples, generic branding, placeholder tenant values, and publicly documented product behavior.

## 2. Guiding principles

- **Public by design:** no organization names, email excerpts, screenshots, internal links, tenant IDs, proprietary source code, or production data.
- **Separate execution from presentation:** orchestration emits typed events; web and Teams adapters render them.
- **Stream meaningful work:** show actual operational stages and generated answer content, never hidden model reasoning.
- **Structure before rendering:** represent rows, facts, metrics, citations, and errors with typed models rather than strings.
- **Progressive enhancement:** narrative output must remain usable if streaming or Adaptive Cards are unavailable.
- **Secure defaults:** delegated identity, least privilege, server-side tokens, protected telemetry, and no secrets in the repository.
- **Preview-aware:** isolate preview APIs behind adapters and document version, licensing, and availability assumptions.

## 3. Target architecture

### 3.1 Shared agent core

Create a Python package that defines:

- Provider interfaces for Microsoft 365 Copilot and Microsoft Foundry.
- Conversation and response identifiers.
- A normalized asynchronous event stream.
- Typed narrative, citation, structured-result, and error models.
- Cancellation and timeout contracts.
- Correlation and telemetry helpers.

Proposed event types:

```python
StatusEvent(stage, message, timestamp)
TextDeltaEvent(delta, accumulated_text)
CitationEvent(title, url, source_type)
StructuredResultEvent(kind, schema_version, data)
FinalTextEvent(text)
ErrorEvent(code, message, retryable, correlation_id)
DoneEvent(reason)
```

`StatusEvent` messages describe observable operations such as reading inputs or preparing a report. They must not contain private chain-of-thought.

### 3.2 Web channel

- React and TypeScript flyout component.
- Fluent UI controls, themes, focus management, and accessibility.
- FastAPI backend-for-frontend.
- Microsoft Entra ID authentication with MSAL.
- SSE endpoint for status and response events.
- Microsoft 365 Copilot Chat API adapter.
- Optional Foundry adapter using the same frontend contract.

### 3.3 Teams channel

- Python Teams SDK application in personal scope.
- Informative streaming updates for real operational stages.
- Cumulative response streaming at a controlled cadence.
- Final message delivery with narrative text, citations, and optional Adaptive Card.
- Deterministic Markdown sanitizer.
- Adaptive Card renderer for typed structured results.

## 4. Delivery milestones

## Milestone 0 - Public repository foundation

### Work items

- Create the repository with the proposed name `agent-experience-blueprints`.
- Add `README.md`, this implementation plan, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.
- Add `.gitignore`, `.editorconfig`, formatting configuration, and pull-request templates.
- Add a public-content checklist to the pull-request template.
- Add secret scanning, dependency scanning, and code scanning.
- Establish supported Python and Node.js versions in the repository documentation.
- Add a decision log under `docs/decisions/`.

### Acceptance criteria

- Repository contains no account names, organization-specific screenshots, internal URLs, email content, tenant identifiers, or proprietary code.
- Secret scanning passes.
- A new contributor can identify the purpose, architecture, prerequisites, and preview dependencies from the README.
- The license and contribution model are explicitly selected before the first public release.

## Milestone 1 - Shared contracts and synthetic scenario

### Work items

- Define the event models and provider protocol in `packages/agent_core`.
- Define typed output models for narrative answers, citations, metrics, key-value facts, tables, status summaries, and errors.
- Create a synthetic `record reconciliation` scenario to exercise multi-stage progress and structured reporting.
- Add a fake provider that produces deterministic status events, text deltas, citations, and structured results.
- Add JSON schemas where cross-language validation is useful.
- Document the rule prohibiting raw `str(dict)` rendering and newline-joining of heterogeneous results.

### Acceptance criteria

- Web and Teams adapters can consume the same event sequence.
- Contract tests verify event ordering, schema validation, cancellation, terminal events, and error behavior.
- Synthetic fixtures contain no copied business data or organization terminology.

## Milestone 2 - Embedded web chat shell

### Work items

- Scaffold the React application and reusable `ChatFlyout` component.
- Implement open, close, resize, theme, and responsive behavior.
- Implement message history, composer, send, cancel, retry, copy, and new-conversation actions.
- Add accessible live regions for status and streamed content.
- Build an SSE client with reconnect and explicit cancellation behavior.
- Provide host integration examples for a plain HTML page and a React host application.
- Use the fake provider first so the UI can be developed without cloud dependencies.

### Acceptance criteria

- The chat panel can be mounted without taking over the host application's routing or global styles.
- Keyboard users can open, operate, and close the panel.
- Status appears immediately after submission.
- Text is rendered progressively.
- Cancellation stops the local stream and returns the composer to a usable state.
- Component tests and Playwright tests cover desktop and narrow layouts.

## Milestone 3 - Microsoft 365 Copilot Chat API adapter

### Work items

- Register a sample Microsoft Entra application and document placeholder configuration.
- Implement delegated authentication in the web client and token validation in the API.
- Implement server-side conversation creation and continuation.
- Implement the streamed endpoint and translate SSE provider events into the shared event contract.
- Capture citations or source metadata supported by the API response contract.
- Add configuration to control web grounding per turn where supported.
- Add user-safe handling for licensing, consent, throttling, timeout, and preview-service errors.
- Document current Chat API limitations, including text-only output and unsupported long-running actions.

### Acceptance criteria

- An appropriately licensed test user can complete a multi-turn conversation from the embedded panel.
- Browser code never receives a client secret or service credential.
- The first streamed content is rendered without waiting for the completed answer.
- Unauthorized and unlicensed states display actionable, non-sensitive errors.
- Provider-specific objects do not escape the adapter boundary.

## Milestone 4 - Foundry asynchronous orchestration

### Work items

- Implement the Foundry provider using agents, conversations, and responses.
- Replace the blocking orchestration path with an async iterator or `run_stream` interface.
- Emit `StatusEvent` at the start and completion of real workflow stages.
- Emit `TextDeltaEvent` as narrative response content becomes available.
- Preserve tool-call and structured-output items for later rendering.
- Add cancellation propagation from web or Teams to the active response where supported.
- Add timeout and retry policies appropriate to idempotent operations.
- Add background-mode guidance for work that cannot complete within an interactive stream.

### Acceptance criteria

- No interactive route calls the blocking workflow execution method.
- A three-stage synthetic workflow surfaces at least three meaningful progress updates before completion.
- Status labels are based on explicit workflow events, not invented model reasoning.
- Cancellation and disconnect tests prove resources are released.
- Structured output remains typed from agent execution through channel delivery.

## Milestone 5 - Teams streaming experience

### Work items

- Create a personal-scope Teams app using the Python Teams SDK.
- Map `StatusEvent` to informative streaming updates.
- Map `TextDeltaEvent` to cumulative response streaming.
- Buffer model deltas and send updates at a stable cadence consistent with Microsoft guidance.
- Guarantee sequential stream updates and one active stream per conversation.
- Handle stop, cancellation, expiration, throttling, and out-of-order failures.
- Send the final activity with the completed content and supported final-only metadata.
- Document the one-on-one chat limitation and concurrent-stream constraint.

### Acceptance criteria

- A user sees an informative update promptly after sending a message.
- Streamed response text is cumulative and never rewrites previously streamed content.
- Updates remain within documented cadence, size, sequence, and duration constraints.
- The final activity completes the stream correctly.
- Stop behavior ends generation or safely discards later output.
- Automated tests cover normal completion, user stop, throttling, timeout, and provider error.

## Milestone 6 - Teams-safe Markdown renderer

### Work items

- Define an allowlist for bold, italic, ordered lists, unordered lists, and links.
- Convert headings to bold paragraphs.
- Convert Markdown tables to typed table models or readable lists.
- Remove inline images, blockquotes, and unsupported preformatted constructs.
- Normalize whitespace and list newlines.
- Add reporting-agent instructions that prefer concise Teams-compatible narrative output.
- Keep the sanitizer authoritative even when model instructions are followed.

### Acceptance criteria

- Test fixtures containing unsupported Markdown render as readable Teams-safe text.
- No raw dictionaries, Python representations, or unsupported tables reach the Teams text field.
- Snapshot tests cover nested lists, links, headings, code-like content, long answers, and malformed Markdown.
- Rendering is manually reviewed on Teams web, desktop, iOS, and Android before release.

## Milestone 7 - Adaptive Cards for structured results

### Work items

- Build card templates for summary metrics, key-value facts, status, errors, and row collections.
- Implement a renderer from typed result models to Adaptive Card JSON.
- Add compact layouts for narrow clients and expanded layouts for wider clients.
- Add optional actions only when they are supported and secure.
- Validate card schema, payload size, text length, and links.
- Attach cards only to the final message, not intermediate streaming updates.
- Provide synthetic screenshots and sample payloads.

### Acceptance criteria

- Structured results are rendered as cards without parsing prose.
- Card validation runs in continuous integration.
- Large result sets are summarized, paginated, or linked rather than exceeding channel limits.
- Cards remain readable in narrow and wide Teams layouts.
- A text fallback is available when a card cannot be rendered.

## Milestone 8 - Security, telemetry, and reliability

### Work items

- Add OpenTelemetry tracing across browser request, API, provider call, and Teams delivery.
- Record acknowledgement latency, first-content latency, completion latency, cancellation rate, provider errors, and rendering errors.
- Redact prompts, retrieved content, access tokens, tenant identifiers, and personal data from default logs.
- Add rate limiting, request-size limits, allowed-origin configuration, and secure headers.
- Add dependency pinning and automated update policy.
- Create a threat model covering token handling, prompt injection, data leakage, card links, telemetry, and preview APIs.
- Add a responsible disclosure process in `SECURITY.md`.

### Acceptance criteria

- Logs are useful for diagnosis without containing message bodies or credentials by default.
- Each user-visible error has a correlation ID.
- Security scans pass at release time.
- Threat-model mitigations are either implemented or tracked as explicit release blockers.

## Milestone 9 - Deployment samples and documentation chapters

### Work items

- Add Bicep for the sample API, managed identity where applicable, telemetry, and configuration.
- Add local-development instructions with fake-provider mode.
- Add cloud setup instructions with placeholder values only.
- Add Teams packaging and sideload instructions.
- Write the nine chapters listed in the README.
- Add architecture and sequence diagrams using repository-owned source files.
- Add a troubleshooting guide and compatibility matrix.
- Document how to substitute a different agent provider without changing channel code.

### Acceptance criteria

- A contributor can run the full synthetic experience locally without cloud credentials.
- A licensed tester can follow the documented steps to connect the Microsoft 365 Copilot provider.
- A Foundry tester can deploy and run the Teams sample.
- All documentation links are public and no internal resources are referenced.

## Milestone 10 - Public preview release

### Work items

- Complete legal, trademark, security, privacy, and accessibility reviews.
- Verify preview terminology and product names against current Microsoft documentation.
- Run a full repository scan for names, domains, email addresses, GUIDs, subscription IDs, screenshots, and secrets.
- Publish release notes, known limitations, and support boundaries.
- Tag `v0.1.0` as a reference preview.

### Acceptance criteria

- All continuous-integration checks pass.
- Public-content review passes with no organization-specific information.
- Known limitations clearly identify preview APIs and Teams streaming constraints.
- Every sample uses synthetic data and generic branding.

## 5. Testing strategy

### Unit tests

- Event model validation.
- Provider event translation.
- Markdown sanitization.
- Adaptive Card rendering.
- Cancellation and timeout helpers.
- Redaction and correlation behavior.

### Contract tests

- Fake, Microsoft 365 Copilot, and Foundry providers emit compatible normalized events.
- Every stream contains one terminal outcome.
- Status and text events preserve ordering.
- Structured result schema versions are supported.

### Integration tests

- FastAPI SSE endpoint with disconnect and reconnect cases.
- Authentication and authorization failures.
- Provider throttling and timeout translation.
- Teams streaming sequence and cumulative-content rules.

### End-to-end tests

- Embedded web chat happy path.
- Multi-turn conversation.
- Cancel and retry.
- Teams informative updates followed by response streaming.
- Structured result delivered as an Adaptive Card.
- Text fallback when a card is rejected.

### Manual compatibility tests

- Current Chrome and Edge.
- Keyboard-only and screen-reader flows.
- Teams web and desktop.
- Teams iOS and Android for formatting and card layout.

## 6. Continuous integration

Recommended pull-request checks:

1. Python formatting, linting, type checking, and tests.
2. TypeScript formatting, linting, type checking, and tests.
3. Playwright smoke tests using the fake provider.
4. Adaptive Card schema and snapshot validation.
5. Markdown renderer snapshots.
6. Secret, dependency, and code scanning.
7. Public-content scan for disallowed domains, email addresses, tenant identifiers, and organization-specific terms.
8. Link checking for public documentation.

Cloud integration tests should run only in a protected environment with short-lived credentials and must not expose response content in public logs.

## 7. Key risks and mitigations

| Risk | Mitigation |
|---|---|
| Microsoft 365 Copilot Chat API changes during preview | Isolate it behind an adapter, pin versions, add contract tests, and publish a compatibility matrix. |
| Licensing or tenant readiness blocks the web sample | Provide fake-provider mode and explicit prerequisites; fail with a clear user-safe message. |
| Teams streaming is used outside supported scope | Validate personal scope and fall back to a non-streaming final message where appropriate. |
| Streaming updates are throttled or arrive out of order | Buffer deltas, serialize sends, use monotonic sequence values, and add retry rules only where safe. |
| Model output contains unsupported Markdown | Use a deterministic allowlist renderer and Adaptive Cards for structured data. |
| Structured output is accidentally flattened | Enforce typed output models and prohibit generic object-to-string rendering in code review and tests. |
| Sensitive content enters logs or examples | Default redaction, synthetic fixtures, public-content scanning, and mandatory review checklist. |
| Cards render differently across clients | Use responsive layouts, narrow-client tests, text fallbacks, and manual mobile validation. |
| Long operations exceed interactive limits | Break work into observable stages, use background mode where supported, or return a resumable operation pattern. |

## 8. Public repository content policy

Do not commit:

- Organization, account, or individual names from real engagements.
- Email subjects, bodies, screenshots, signatures, or attachments.
- Internal or local-machine URLs and file paths.
- Tenant IDs, subscription IDs, resource names, conversation IDs, or access tokens.
- Production prompts, retrieved documents, transcripts, logs, or telemetry exports.
- Proprietary source code or copied implementation details from an existing project.
- Logos or branding without explicit public-use rights.

Use instead:

- `Contoso` only where Microsoft documentation conventions make a fictional organization useful, or use neutral labels such as `Example Organization`.
- Reserved domains such as `example.com`.
- Generated GUID placeholders such as `<tenant-id>` rather than realistic values.
- Synthetic reconciliation records and generated screenshots.
- Links only to public Microsoft Learn, Adaptive Cards, or repository documentation.

## 9. Definition of done

The first public preview is done when:

- The embedded web chat works with fake and Microsoft 365 Copilot providers.
- The Foundry sample streams explicit workflow progress and answer content.
- Teams delivery uses informative updates, cumulative streaming, and a correct final activity.
- Narrative output is Teams-safe.
- Structured results use validated Adaptive Cards with text fallback.
- Authentication, cancellation, error, accessibility, and telemetry paths are tested.
- Deployment and local-development instructions are reproducible.
- Security, public-content, and documentation reviews pass.
- The repository contains no real engagement information.

## 10. Recommended initial issue backlog

1. Establish repository governance and public-content checks.
2. Define normalized agent event schemas.
3. Add deterministic fake provider and synthetic workflow.
4. Build accessible React chat flyout.
5. Implement FastAPI SSE endpoint.
6. Add Microsoft Entra authentication sample.
7. Implement Microsoft 365 Copilot Chat API provider.
8. Implement Foundry response streaming provider.
9. Build Teams personal-scope sample.
10. Add informative and cumulative Teams streaming.
11. Add Teams-safe Markdown renderer.
12. Add typed Adaptive Card renderers.
13. Add cross-channel contract tests.
14. Add security, telemetry, and redaction.
15. Add deployment templates and tutorial chapters.
16. Complete public preview review and release.

## 11. Source guidance

This plan is based on Microsoft Learn documentation reviewed August 19, 2026:

- [Microsoft 365 Copilot Chat API overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/chat/overview)
- [Foundry Agent Service runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components)
- [Stream agent messages in Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/streaming-ux)
- [Format cards in Teams](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format)
- [Adaptive Cards documentation](https://adaptivecards.microsoft.com/)
