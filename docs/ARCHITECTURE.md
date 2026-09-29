# Architecture

```text
Browser UI
  | JSON, same origin
Python HTTP application
  |-- SQLite: workspaces, dated events, analyses, hypotheses, lessons, activity
  |-- Local rule engine (explicitly labeled, enterprise pattern only)
  `-- Hindsight Cloud (official Python client)
        Retain dated documents with stable IDs
        Recall actual relevant memories
        Reflect using persistent evidence and lessons
```

Each competitor workspace has a unique Hindsight bank. A new guided example creates a new workspace and bank, preserving old evidence. There is no browser-only source of truth and no hardcoded success counters.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Health probe |
| GET | /api/state?workspace=ID | Workspace data and non-secret connection status |
| POST | /api/workspaces | Create a named competitor workspace |
| POST | /api/events | Validate and persist evidence plus a queued memory document |
| POST | /api/analyze | Run local rules or live Hindsight, persist result |
| POST | /api/hypotheses | Save analyst-reviewed hypothesis with event IDs |
| POST | /api/evaluate | Evaluate against a later event and retain a lesson |
| POST | /api/connection | Save key on backend and test Hindsight authentication |
| POST | /api/sync | Retain queued documents, mark successes individually |
| POST | /api/demo | Create a fresh isolated synthetic workspace |
| POST | /api/demo-step | Add one of three example history events, idempotently |
| POST | /api/demo-outcome | Add a supportive or contradictory later event |

All mutations require JSON and reject mismatched Origin headers. The default bind is loopback. Public demo deployment needs APP_PASSWORD and an HTTPS proxy. Secrets are restricted to server data or environment variables; static serving uses an exact allowlist. User and model text is escaped before insertion into the UI.

## Reasoning and evidence

The live assessment is the actual Reflect response, not a canned title or numerical confidence. Recall results are shown with the returned fact IDs. The analyst selects event evidence when saving a hypothesis. The outcome must have a later event date than every originally selected event. Evaluation writes a clearly attributed analyst lesson rather than asserting a universally learned law.

The latest-event baseline uses the local rule engine, explicitly labeled; it is not an equal-model experimental benchmark. To compare live model behavior, run Hindsight after one event, add history, run again, evaluate an outcome, and run again. Each analysis is saved in SQLite.

## Recovery

Failed retain calls leave documents queued. Stable document IDs make a retry replace the same document rather than intentionally duplicate it. Completed documents are marked synced individually. Failed live reasoning does not overwrite the prior analysis. Hindsight failures are logged without API keys. SQLite transactions protect individual record writes; the server serializes mutations for this single-team MVP.
