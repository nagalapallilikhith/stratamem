# STRATAMEM

STRATAMEM helps a product or strategy team answer: **What do our competitor's changes mean together, and did our interpretation hold up?**

The application connects dated evidence, records a testable hypothesis, evaluates later evidence, and retains a lesson for subsequent analysis. It is a working single-team MVP with SQLite persistence and a real Hindsight Cloud adapter. The dataset is intentionally small; the example company and its events are fictional.

## Start on Windows

1. Extract the whole ZIP.
2. Double-click `START_WINDOWS.cmd`. Python 3.11+ must be installed. The first run installs the official Hindsight client from PyPI.
3. Open **http://127.0.0.1:8000**. Keep the command window open.
4. Open **Hindsight connection**, paste your Cloud API key, and select **Save & test connection**.
5. Open **Guided demo** and work through the five steps. Select **Hindsight · live memory + AI** for live assessments.

The local server is already sufficient to run the frontend and database. Without Hindsight, `python app.py` provides an explicitly labeled rule-based engine, not an AI model.

## What is implemented

- Separate competitor workspaces and isolated Hindsight bank IDs.
- Evidence entry with date, category, source validation, and synthetic-data disclosure.
- Persistent SQLite events, memory documents, analyses, hypotheses, lessons, and activity.
- Hindsight Retain with stable document IDs and timestamps; retryable queued records.
- Hindsight Recall with the returned memory text exposed in the interface.
- Hindsight Reflect output shown directly; errors never become simulated successful answers.
- Analyst-reviewed hypotheses with selected source evidence and expected future signals.
- Outcome review against a later event; supported, weakened, and rejected states.
- Persistent outcome lessons included in future local runs and synced before live runs.
- Guided positive or contradictory example, fresh isolated replays, evidence search/filter, and Markdown brief export.
- Responsive frontend, busy/error/empty states, and Hindsight links.

## How the live flow works

The browser sends actions to the Python backend. SQLite holds application state. Before a live analysis, the backend sends unsynced event, hypothesis, and lesson documents to the competitor's Hindsight bank. It calls Recall and then Reflect. The application stores and displays the returned assessment and recalled memories.

Saving evidence does not automatically transmit it externally. Selecting **Sync pending records** or running a Hindsight assessment does. The UI reports local records and Hindsight-synced records separately. A document may produce multiple Hindsight facts, so document counts are not claimed to be fact counts.

Hypothesis and outcome review are deliberately human decisions. The AI assessment informs the analyst; it does not silently declare itself correct. The local engine supports only a narrow enterprise-expansion pattern and is labeled accordingly. No custom model training has been performed; the memory loop uses a pretrained reasoning model through Hindsight.

## Data and secrets

Runtime files live in `data/`, which is excluded from Git and the distribution ZIP. SQLite preserves work after restart. A locally entered Cloud key is stored in `data/connection.json`; never publish this folder. Server environment variables `HINDSIGHT_API_KEY` and `HINDSIGHT_BASE_URL` override that file. Keys are never returned in state responses or brief exports.

Fresh examples preserve previous work and use a new bank, avoiding future-outcome leakage. Existing Hindsight banks are not deleted automatically. Remove obsolete demo banks yourself in Hindsight Cloud when no longer needed.

## Run with a terminal

```sh
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
# macOS/Linux:
# .venv/bin/python -m pip install -r requirements.txt
# .venv/bin/python app.py
```

## Deploy as a private team demo

The included Dockerfile installs the verified client version. Use a persistent volume for `/data`:

```sh
docker build -t stratamem .
docker run --env-file deploy.env -p 8000:8000 -v stratamem-data:/data stratamem
```

Create `deploy.env` locally with `APP_PASSWORD=your-long-random-team-password` and optionally `HINDSIGHT_API_KEY=your-key`. Do not commit it. Login username is `team`. Host behind an HTTPS reverse proxy before sharing outside your own computer. The server refuses an external bind without APP_PASSWORD. This is a single-team demo service, not a multi-tenant production SaaS.

## Verification

```sh
python -m unittest discover -s tests -v
```

Tests cover persistence, history-dependent local analysis, contradictory outcomes, lesson reuse, temporal checks, workspace isolation, sync behavior, and explicit Hindsight failure. Transport tests use a fake client and do not prove live credentials. A live smoke test requires your own key in the Connection screen.

## Architecture and demo

- [Architecture and API](docs/ARCHITECTURE.md)
- [Three-minute walkthrough](docs/DEMO.md)
- [Verification record](docs/VERIFICATION.md)

## Hindsight references

- https://hindsight.vectorize.io/sdks/python
- https://hindsight.vectorize.io/developer/api/retain
- https://hindsight.vectorize.io/developer/api/recall
- https://hindsight.vectorize.io/developer/api/reflect
- https://github.com/vectorize-io/hindsight

## Boundaries

This release does not include crawling, custom training, multi-user permissions, high-scale hosting, or automated factual verification of submitted sources. These are outside the focused application workflow. The displayed model output remains uncertain strategic interpretation. Qualification and judging outcomes cannot be guaranteed.
