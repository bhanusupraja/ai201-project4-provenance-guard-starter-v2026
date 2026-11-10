"""
The structured run log — CAPSTONE, Shape A (deploy and instrument).

Every HTTP request the service handles gets one record here, as one JSON
object per line in ``logs/runs.jsonl``. Not ``print()`` — a file you can
read back, filter, and count.

This is a different record from the audit log, and the difference is the
point:

- ``audit.jsonl`` records DECISIONS: what the service judged, about
  whose writing, with what scores. It is the evidence trail for the
  judgement itself.
- ``runs.jsonl`` records RUNS: what came in, what went out, and how long
  it took. It is the evidence trail for the service as a running system.

One record holds, at minimum:

    timestamp, request_id, endpoint, method, status_code, duration_ms

plus, when the route knows them:

    creator_id, content_id, text_chars, text_preview,
    guess, confidence, label, model_score, style_score,
    error, model_loaded

Rules this module keeps:

- Failures leave a record too. A 400, a 429, a 503, a 500 — the run
  log is where you find them. A failure that shows up only as an
  absence is one you will never diagnose.
- Full submission text is NEVER written here. ``text_preview`` holds
  the first 60 characters so a later reader can tell runs apart; the
  full text stays out of the log on purpose.
- A logging failure never breaks a response. Callers wrap ``log_run``
  in try/except; a log that can't be written must not turn a good
  answer into a 500.

    from runlog import log_run, read_runs

    log_run({"endpoint": "/submit", "status_code": 200, ...})
    runs = read_runs(limit=50)
"""

import json
import threading
from datetime import datetime, timezone

import config

RUN_LOG = config.LOG_DIR / "runs.jsonl"

_lock = threading.Lock()

# Full text never goes in the log. 60 characters is enough to tell runs
# apart and short enough that a poem does not end up in a log file.
PREVIEW_CHARS = 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_run(record: dict) -> dict:
    """
    Write one run record to the run log.

    The caller builds the record; this function only guarantees the
    shape: ``timestamp`` is always present, every field is always
    present (as ``null`` when the route could not fill it), and the
    write is atomic per line under a lock. A record you cannot count
    on having the same fields is a record you cannot measure from.
    """
    entry = {
        "timestamp": _now(),
        "request_id": record.get("request_id"),
        "endpoint": record.get("endpoint"),
        "method": record.get("method"),
        "status_code": record.get("status_code"),
        "duration_ms": record.get("duration_ms"),
        "creator_id": record.get("creator_id"),
        "content_id": record.get("content_id"),
        "text_chars": record.get("text_chars"),
        "text_preview": record.get("text_preview"),
        "guess": record.get("guess"),
        "confidence": record.get("confidence"),
        "label": record.get("label"),
        "model_score": record.get("model_score"),
        "style_score": record.get("style_score"),
        "error": record.get("error"),
        "model_loaded": record.get("model_loaded"),
    }
    # Anything extra the caller passes gets written too, after the
    # standard fields — the same pattern audit.py uses.
    for key, value in record.items():
        if key not in entry:
            entry[key] = value
    return _append(entry)


def _append(entry: dict) -> dict:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False)
    with _lock:
        with RUN_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return entry


def read_runs(limit: int | None = None) -> list[dict]:
    """
    Read the run log back, oldest first. `limit` keeps the most recent N.

    A malformed line is skipped rather than raising — a log that can't be
    read because of one bad row is worse than a log with a gap.
    """
    if not RUN_LOG.exists():
        return []

    entries = []
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return entries[-limit:] if limit else entries


def preview(text: str | None) -> str | None:
    """First PREVIEW_CHARS characters of a submission, or None."""
    if not isinstance(text, str) or not text:
        return None
    return text[:PREVIEW_CHARS]
