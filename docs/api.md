# Local streaming API

The FastAPI sample exposes the normalized event contract through named Server-Sent Events. It uses the deterministic fake provider by default and requires no cloud credentials.

## Run locally

Install the project with its development dependencies and start Uvicorn:

```powershell
python -m pip install -e ".[dev]"
python -m uvicorn agent_api.main:app --reload
```

This repository uses standard PEP 621 metadata and setuptools. Poetry is not required or configured.

## Endpoints

`GET /healthz` returns `{ "status": "ok" }` when the process is ready to accept requests.

`POST /v1/chat/stream` accepts:

```json
{
  "message": "Reconcile the sample records",
  "conversation_id": null,
  "response_id": null
}
```

`message` is required, cannot be blank, and is limited to 16,000 characters. Conversation and response identifiers are optional opaque strings limited to 256 characters.

The response uses `text/event-stream`. Every frame includes a monotonically increasing stream-local `id`, a normalized event name, and one JSON payload:

```text
id: 1
event: status
data: {"type":"status","stage":"ingesting","message":"Reading synthetic records","timestamp":"<utc-timestamp>"}
```

The endpoint sends anti-buffering response headers. If the client disconnects or closes the response generator, the adapter signals cooperative cancellation to the active provider. Unexpected provider exceptions are converted to a user-safe `error` event followed by `done` with reason `error`; exception details are not sent to the client.

The local endpoint is intentionally unauthenticated. Do not expose it to an untrusted network. The Microsoft Entra authentication boundary belongs to the cloud-provider integration milestone.