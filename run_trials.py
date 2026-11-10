#!/usr/bin/env python3
"""
Run the capstone trials — CAPSTONE, Shape A, Milestone 5.

Three trials, one per criterion set, changing nothing in between.
Each trial starts the service fresh with the one command from
RUNNING.md, then checks all five committed criteria:

  C1  Every run is logged — every request in the trial appears in
      logs/runs.jsonl with timestamp, endpoint, status, duration.
  C2  The run path works — the one command starts the service and
      POST /ping answers 200.
  C3  A warm run is fast enough — mean of the warm /submit calls
      stays under 2 seconds.
  C4  The bad path is handled and logged — all 4 bad inputs return
      400 and still leave a record in the run log.
  C5  The first call, model loading included — the first /submit
      after starting finishes within 20 seconds.

What a trial sends, in order, under one fresh creator_id for the
good submits (10 calls: 1 first + 9 warm — exactly the 10/minute
limit, so a re-run never trips it) and one fresh creator_id per
bad input (each 1 call, well inside its own window):

  1. POST /ping                       (C2)
  2. POST /submit  AI_GENERIC        (C5, first call, model load)
  3. POST /submit  x9 warm texts     (C3, mean of the 9)
  4. POST /submit  x4 bad inputs     (C4, expect 400 each)

Then it reads the run log back and checks every one of those 15
requests has a record with the required fields (C1, and the
"still leave a record" half of C4).

    .venv/bin/python run_trials.py

Writes results/trials_2026-11-10.md. The server is started by the
script on port 5003 and killed when each trial ends. The audit log
and the run log keep the submissions — they are real runs, and the
logs are append-only on purpose.
"""

import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
PORT = 5003
BASE = f"http://127.0.0.1:{PORT}"

from scenarios import (  # noqa: E402
    AI_FASTPACED,
    AI_GENERIC,
    AI_SYSWORKS,
    BORDERLINE_PARAPHRASE,
    HUMAN_DIWALI,
    HUMAN_FRAGMENT,
    HUMAN_ORNATE,
    HUMAN_POEM,
    HUMAN_TRAIN,
    HUMAN_WALK,
)

# First call, then the 9 warm calls. Same 10 texts as measure_cost.py.
FIRST_TEXT = ("ai-generic", AI_GENERIC)
WARM_TEXTS = [
    ("ai-sysworks", AI_SYSWORKS),
    ("ai-fastpaced", AI_FASTPACED),
    ("human-diwali", HUMAN_DIWALI),
    ("human-ornate", HUMAN_ORNATE),
    ("human-fragment", HUMAN_FRAGMENT),
    ("human-train", HUMAN_TRAIN),
    ("human-poem", HUMAN_POEM),
    ("borderline-paraphrase", BORDERLINE_PARAPHRASE),
    ("human-walk", HUMAN_WALK),
]

# The 4 bad inputs from Unit 7, criterion 5 — same shapes as
# scenarios.py, with trial-specific creator_ids.
BAD_INPUTS = [
    ("text missing", {"creator_id": None}),  # creator filled per trial
    ("text empty", {"text": "", "creator_id": None}),
    ("text null", {"text": None, "creator_id": None}),
    ("text over 20,000 chars", {"text": "word " * 5000, "creator_id": None}),
]

REQUIRED_FIELDS = ["timestamp", "endpoint", "status_code", "duration_ms"]


def _wait_for_health(timeout_s: float = 180.0) -> bool:
    """Poll /health until the server answers, or give up."""
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        try:
            resp = requests.get(f"{BASE}/health", timeout=5)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    return False


def _run_log_entries():
    """All run-log entries, via the same module the app uses."""
    import runlog

    return runlog.read_runs()


def _check_logged(entries, endpoint, status, creator_id=None):
    """True if some entry matches this request."""
    for e in entries:
        if e.get("endpoint") != endpoint:
            continue
        if e.get("status_code") != status:
            continue
        if creator_id is not None and e.get("creator_id") != creator_id:
            continue
        return True
    return False


def _fields_ok(entries):
    """True if every entry carries the fields criterion 1 requires."""
    for e in entries:
        for f in REQUIRED_FIELDS:
            if f not in e or e.get(f) is None:
                return False
    return True


def run_trial(n: int, tag: str) -> dict:
    """One trial: fresh server, all five criteria, nothing changed."""
    creator = f"trial_{n}_{tag}"
    result = {"trial": n, "creator": creator}

    env = dict(__import__("os").environ)
    env["PORT"] = str(PORT)
    # Server output goes to a per-trial file, not DEVNULL: if a call
    # ever hangs, the server's own log is the evidence.
    server_log = open(ROOT / "logs" / f"trial_{n}_server.log", "w",
                      encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT,
        env=env,
        stdout=server_log,
        stderr=subprocess.STDOUT,
    )
    try:
        print(f"Trial {n}: starting server on port {PORT} (pid {proc.pid}) ...")
        if not _wait_for_health():
            print(f"Trial {n}: ERROR — server did not answer /health in time.")
            result["error"] = "server did not start"
            return result
        print(f"Trial {n}: server is up.")

        # Snapshot the run log BEFORE /ping, so the ping is inside
        # the trial's own entries. (An earlier version snapshotted
        # after /ping and then wrongly reported it unlogged.)
        before = len(_run_log_entries())

        # C2 — the run path works: /ping answers 200.
        started = time.perf_counter()
        ping = requests.post(
            f"{BASE}/ping", json={"message": "hello"}, timeout=10
        )
        result["ping_status"] = ping.status_code
        result["ping_seconds"] = round(time.perf_counter() - started, 2)
        print(f"  /ping -> {ping.status_code} in {result['ping_seconds']}s")

        # C5 — first call, model loading included. A timeout here is
        # recorded as a miss for this trial, not a crash of the run:
        # the server is killed and the next trial starts fresh.
        try:
            started = time.perf_counter()
            resp = requests.post(
                f"{BASE}/submit",
                json={"text": FIRST_TEXT[1], "creator_id": creator},
                timeout=180,
            )
            first_seconds = round(time.perf_counter() - started, 2)
            result["first_seconds"] = first_seconds
            result["first_status"] = resp.status_code
            result["first_guess"] = resp.json().get("guess") if resp.status_code == 200 else None
            print(f"  first /submit ({FIRST_TEXT[0]}) -> {resp.status_code} "
                  f"in {first_seconds}s  guess={result['first_guess']}")
        except requests.RequestException as exc:
            result["first_seconds"] = None
            result["first_status"] = "error"
            result["first_error"] = str(exc)
            result["warm_rows"] = []
            result["warm_mean"] = None
            result["warm_ok"] = 0
            result["bad_rows"] = []
            result["bad_400s"] = 0
            result["bad_logged"] = 0
            result["new_log_entries"] = 0
            result["fields_ok"] = False
            result["ping_logged"] = False
            result["submit_200_count"] = 0
            print(f"  first /submit ({FIRST_TEXT[0]}) -> ERROR: {exc}")
            return result

        # C3 — warm runs: the 9 remaining texts, same creator_id.
        warm_rows = []
        for name, text in WARM_TEXTS:
            started = time.perf_counter()
            try:
                resp = requests.post(
                    f"{BASE}/submit",
                    json={"text": text, "creator_id": creator},
                    timeout=180,
                )
                elapsed = round(time.perf_counter() - started, 2)
                guess = resp.json().get("guess") if resp.status_code == 200 else None
                warm_rows.append({"name": name, "status": resp.status_code,
                                  "seconds": elapsed, "guess": guess})
            except requests.RequestException as exc:
                warm_rows.append({"name": name, "status": "error",
                                  "seconds": round(time.perf_counter() - started, 2),
                                  "guess": None, "error": str(exc)})
            r = warm_rows[-1]
            print(f"  warm /submit ({name}) -> {r['status']} "
                  f"in {r['seconds']}s  guess={r['guess']}")
        result["warm_rows"] = warm_rows
        warm_times = [r["seconds"] for r in warm_rows if r["status"] == 200]
        result["warm_mean"] = round(statistics.mean(warm_times), 2) if warm_times else None
        result["warm_ok"] = sum(1 for r in warm_rows if r["status"] == 200)

        # C4 — the bad path: 4 bad inputs, each its own creator_id.
        bad_rows = []
        for i, (label, body) in enumerate(BAD_INPUTS):
            bad_creator = f"{creator}_bad_{i}"
            body = dict(body)
            body["creator_id"] = bad_creator
            started = time.perf_counter()
            try:
                resp = requests.post(f"{BASE}/submit", json=body, timeout=30)
                status = resp.status_code
            except requests.RequestException as exc:
                status = "error"
            elapsed = round(time.perf_counter() - started, 2)
            bad_rows.append({"label": label, "status": status,
                             "seconds": elapsed, "creator_id": bad_creator})
            print(f"  bad input ({label}) -> {status} in {elapsed}s")
        result["bad_rows"] = bad_rows

        # C1 — every run logged: read the log back, match each request.
        new_entries = _run_log_entries()[before:]
        result["new_log_entries"] = len(new_entries)
        result["fields_ok"] = _fields_ok(new_entries)
        result["ping_logged"] = _check_logged(new_entries, "/ping", 200)
        # Every good submit must have its own record: count the
        # /submit 200 entries for this trial's creator_id. It must be
        # exactly 10 (1 first + 9 warm). A total-count check would be
        # weak, because the /health polls are logged too.
        result["submit_200_count"] = sum(
            1 for e in new_entries
            if e.get("endpoint") == "/submit"
            and e.get("status_code") == 200
            and e.get("creator_id") == creator
        )
        result["first_logged"] = result["submit_200_count"] >= 1
        result["bad_logged"] = sum(
            1 for r in bad_rows
            if _check_logged(new_entries, "/submit", 400, r["creator_id"])
        )
        result["bad_400s"] = sum(1 for r in bad_rows if r["status"] == 400)
        print(f"  run log: {len(new_entries)} new entries, fields ok="
              f"{result['fields_ok']}, ping logged={result['ping_logged']}, "
              f"bad 400s={result['bad_400s']}/4, bad logged="
              f"{result['bad_logged']}/4")
        return result
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        server_log.close()


def _criterion_outcome(results, key):
    """How many of the 3 trials held the target for one criterion."""
    return results


def main() -> int:
    tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    trials = []
    for n in (1, 2, 3):
        trials.append(run_trial(n, tag))
        print()

    # Per-criterion outcomes across the three trials — observed facts,
    # not verdicts. Verdicts, diagnoses and the improvement are
    # Milestone 6.
    def held(t, pred):
        return pred(t)

    outcomes = {
        "C1 every run logged": [
            t.get("ping_logged") and t.get("submit_200_count") == 10
            and t.get("bad_logged") == 4 and t.get("fields_ok")
            for t in trials
        ],
        "C2 run path works": [
            t.get("ping_status") == 200 for t in trials
        ],
        "C3 warm run under 2s": [
            t.get("warm_mean") is not None and t["warm_mean"] < 2
            for t in trials
        ],
        "C4 bad path 400 + logged": [
            t.get("bad_400s") == 4 and t.get("bad_logged") == 4
            for t in trials
        ],
        "C5 first call within 20s": [
            t.get("first_seconds") is not None and t["first_seconds"] < 20
            for t in trials
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "trials_2026-11-10.md"
    lines = [
        "# Capstone trials — 3 trials per criterion",
        "",
        f"Run {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z",
        f"by `.venv/bin/python run_trials.py`. Criteria committed in",
        "`6fd70b2` (add capstone criteria) before any of these runs.",
        "Nothing was changed between trials.",
        "",
        "First attempt (before this run): trial 1's first /submit timed",
        "out after 180s and left no run-log record — the model load hung",
        "on that server start. A manual first /submit on a fresh server",
        "minutes later took 16.09s and returned 200, so the service",
        "itself was fine; the stall was not reproduced. The script was",
        "made robust (a timed-out call is recorded as a miss for that",
        "trial instead of crashing the run) and the trials were re-run.",
        "",
        "Second attempt: the three trials ran, but the checker in the",
        "script was wrong — it looked for fields named `status` and",
        "`duration`, while the run log actually records `status_code`",
        "and `duration_ms`, and it snapshotted the log after /ping and",
        "then reported /ping unlogged. So C1 and the logged half of C4",
        "were scored 0/3 by the checker, not by the service: the 400s",
        "themselves were 4/4, and the log held the entries. The checker",
        "was fixed (right field names, snapshot before /ping) and the",
        "trials were re-run from scratch. The three trials below are",
        "that clean re-run.",
        "",
        "## Method",
        "",
        "- Each trial starts the service fresh with the one command",
        "  from RUNNING.md (`.venv/bin/python app.py`, port 5003) and",
        "  kills it at the end. A fresh start per trial is what makes",
        "  the first-call criterion (C5) a real measurement each time.",
        "- Each trial sends, in order: 1x POST /ping, 1x first",
        "  /submit (AI_GENERIC, model load included), 9x warm /submit",
        "  (the other 9 texts from measure_cost.py), 4x bad inputs",
        "  (the Unit 7 shapes: text missing, empty, null, over 20,000",
        "  characters). All times are client-side wall clock.",
        "- Good submits in a trial share one fresh creator_id (10",
        "  calls = the 10/minute limit). Each bad input has its own",
        "  creator_id, so no window is ever tripped.",
        "- After the calls, the trial reads logs/runs.jsonl back and",
        "  matches every request it sent (C1).",
        "",
    ]
    for t in trials:
        lines += [
            f"## Trial {t['trial']}",
            "",
            f"- Creator: `{t.get('creator')}`",
            f"- C2 run path: /ping -> {t.get('ping_status')} "
            f"({t.get('ping_seconds')}s)",
            f"- C5 first call: {t.get('first_seconds')}s "
            f"(status {t.get('first_status')}, guess {t.get('first_guess')})",
            f"- C3 warm runs: mean {t.get('warm_mean')}s "
            f"({t.get('warm_ok')}/9 returned 200)",
            "",
            "  | text | status | seconds | guess |",
            "  |---|---|---|---|",
        ]
        for r in t.get("warm_rows", []):
            lines.append(
                f"  | {r['name']} | {r['status']} | {r['seconds']:.2f} "
                f"| {r['guess']} |"
            )
        lines += [
            "",
            f"- C4 bad inputs: {t.get('bad_400s')}/4 returned 400, "
            f"{t.get('bad_logged')}/4 left a run-log record",
            "",
            "  | bad input | status | seconds |",
            "  |---|---|---|",
        ]
        for r in t.get("bad_rows", []):
            lines.append(
                f"  | {r['label']} | {r['status']} | {r['seconds']:.2f} |"
            )
        lines += [
            "",
            f"- C1 run log: {t.get('new_log_entries')} new entries, "
            f"required fields present: {t.get('fields_ok')}, /ping "
            f"logged: {t.get('ping_logged')}, /submit 200 records for "
            f"this trial: {t.get('submit_200_count')}/10, bad-input "
            f"records: {t.get('bad_logged')}/4",
            "",
        ]
    lines += [
        "## Outcomes across the three trials",
        "",
        "Target held or not, per criterion, per trial. These are the",
        "observed results; the verdicts table, the diagnosis for any",
        "miss, and the one improvement are Milestone 6.",
        "",
        "| Criterion | Target | Trial 1 | Trial 2 | Trial 3 |",
        "|---|---|---|---|---|",
    ]
    targets = {
        "C1 every run logged": "all 15 requests logged, fields present",
        "C2 run path works": "/ping 200",
        "C3 warm run under 2s": "warm mean < 2s",
        "C4 bad path 400 + logged": "4/4 400s, 4/4 logged",
        "C5 first call within 20s": "first call < 20s",
    }
    for name, held_list in outcomes.items():
        marks = ["held" if h else "MISSED" for h in held_list]
        lines.append(
            f"| {name} | {targets[name]} | {marks[0]} | {marks[1]} | {marks[2]} |"
        )
    lines += [
        "",
        f"- Python: {sys.version.split()[0]}",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")

    print("Outcomes across the three trials:")
    for name, held_list in outcomes.items():
        print(f"  {name}: {sum(held_list)}/3 held")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
