#!/usr/bin/env python3
"""
Measure what one run of Provenance Guard costs — CAPSTONE, Shape A.

Cost here is seconds of compute, measured, not estimated from a pricing
page. There is no API spend: the model runs on this machine, so the
only thing a run consumes is time on this CPU (and the disk the model
already sits on).

What it does:

1. Starts the service itself on port 5001, as a subprocess, and waits
   for /health. Nothing about your terminal or an already-running
   server matters — the measurement owns its own server and kills it
   at the end.
2. Sends 10 real /submit calls — the 9 label-coverage texts from
   scenarios.py plus one plain human paragraph — under one fresh
   creator_id per run, so a re-run never trips the previous run's
   rate-limit window.
3. Times each call from the client side, wall clock, with
   time.perf_counter. The first call includes loading GPT-2 into
   memory (10–20 seconds); calls 2–10 are warm. The two are reported
   separately, because averaging them together would answer a
   question nobody asked: a service that is already up never pays
   the load cost again.
4. Reads the run log back and checks the 10 calls are in it — the
   measurement also proves the instrumentation works.
5. Writes results/cost_measurement.md: the per-call table, the warm
   mean/median/min/max, the first-call load time, the environment
   (Python version, model size on disk), and the arithmetic for 100
   runs a day.

    python measure_cost.py

The server it starts is killed when the script ends. The audit log and
the run log keep the 10 submissions — they are real runs, and the logs
are append-only on purpose.
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
PORT = 5001
BASE = f"http://127.0.0.1:{PORT}"

# The 9 label-coverage texts from scenarios.py, plus one plain human
# paragraph. Fixed, so a re-run measures the same work.
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

TEXTS = [
    ("ai-generic", AI_GENERIC),
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


def _model_size_mb() -> float | None:
    """GPT-2 weights on disk, in MB, from the Hugging Face cache.

    Only the ``blobs`` directory is counted: ``snapshots`` holds
    symlinks to the same files, and counting both would double it.
    """
    cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--gpt2"
    blobs = cache / "blobs"
    if not blobs.exists():
        return None
    total = sum(p.stat().st_size for p in blobs.rglob("*") if p.is_file())
    return round(total / (1024 * 1024), 1)


def main() -> int:
    run_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    creator_id = f"cost_measurement_{run_tag}"

    env = dict(__import__("os").environ)
    env["PORT"] = str(PORT)
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        print(f"Starting server on port {PORT} (pid {proc.pid}) ...")
        if not _wait_for_health():
            print("ERROR: server did not answer /health in time.")
            return 1
        print("Server is up. Sending 10 /submit calls ...")

        rows = []
        for name, text in TEXTS:
            started = time.perf_counter()
            try:
                resp = requests.post(
                    f"{BASE}/submit",
                    json={"text": text, "creator_id": creator_id},
                    timeout=180,
                )
                elapsed = time.perf_counter() - started
                body = resp.json()
                rows.append({
                    "name": name,
                    "status": resp.status_code,
                    "seconds": round(elapsed, 2),
                    # `guess` is the short verdict (ai/human/unsure).
                    # `label` is the same verdict as a full sentence
                    # and would make the table unreadable.
                    "label": body.get("guess"),
                    "chars": len(text),
                })
            except requests.RequestException as exc:
                rows.append({
                    "name": name,
                    "status": "error",
                    "seconds": round(time.perf_counter() - started, 2),
                    "label": None,
                    "chars": len(text),
                    "error": str(exc),
                })
            print(f"  {name:22s} {rows[-1]['status']}  {rows[-1]['seconds']:>7.2f}s"
                  f"  {rows[-1]['label']}")

        warm = [r["seconds"] for r in rows[1:] if r["status"] == 200]
        first = rows[0]["seconds"] if rows else None
        ok = sum(1 for r in rows if r["status"] == 200)

        # Did the run log see them? The measurement also proves the
        # instrumentation works — a cost number from a system that
        # didn't record its own runs would be a guess.
        import runlog

        logged = [
            e for e in runlog.read_runs()
            if e.get("creator_id") == creator_id
        ]

        model_mb = _model_size_mb()
        warm_mean = round(statistics.mean(warm), 2) if warm else None
        warm_median = round(statistics.median(warm), 2) if warm else None
        warm_min = min(warm) if warm else None
        warm_max = max(warm) if warm else None

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = RESULTS_DIR / "cost_measurement.md"
        lines = [
            "# Cost measurement — one run of Provenance Guard",
            "",
            f"Measured {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z",
            f"by `python measure_cost.py` (10 fixed /submit calls, creator "
            f"`{creator_id}`).",
            "",
            "## Method",
            "",
            "- Cost here is **seconds of compute**, measured wall-clock",
            "  from the client side. There is no API spend: GPT-2 runs on",
            "  this machine, so a run costs time, not money.",
            "- The first call includes loading GPT-2 into memory and is",
            "  reported on its own. Calls 2–10 are warm: the model is",
            "  already loaded, which is the state the service is in",
            "  whenever it is actually serving.",
            "- The server was started by the script itself on port 5001",
            "  and killed when the script ended.",
            "",
            "## Per-call results",
            "",
            "| # | text | status | seconds | guess |",
            "|---|---|---|---|---|",
        ]
        for i, r in enumerate(rows, 1):
            lines.append(
                f"| {i} | {r['name']} | {r['status']} | {r['seconds']:.2f} "
                f"| {r['label']} |"
            )
        lines += [
            "",
            "## Summary",
            "",
            f"- Calls that returned 200: {ok} of 10",
            f"- First call (includes model load): {first:.2f}s" if first is not None else "- First call: n/a",
            f"- Warm calls (2–10): mean {warm_mean}s, median {warm_median}s, "
            f"min {warm_min}s, max {warm_max}s" if warm else "- Warm calls: n/a",
            f"- Run-log check: {len(logged)} of 10 calls appear in "
            f"`logs/runs.jsonl` for this creator_id",
            f"- Model on disk (GPT-2): {model_mb} MB" if model_mb else "- Model on disk: not found in the Hugging Face cache",
            f"- Python: {sys.version.split()[0]}",
            "",
            "## What 100 runs a day would cost",
            "",
        ]
        if warm_mean:
            lines.append(
                f"100 warm runs x {warm_mean}s = {round(100 * warm_mean, 1)}s "
                f"(about {round(100 * warm_mean / 60, 1)} minutes) of compute "
                f"a day, plus one model load of about {first}s when the "
                f"service starts. At this scale the cost is minutes of one "
                f"machine's time, not money."
            )
        else:
            lines.append("Not computed — no warm calls returned 200.")
        lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")

        print()
        print(f"200s: {ok}/10   first call: {first}s (model load)"
              f"   warm mean: {warm_mean}s  median: {warm_median}s"
              f"   min: {warm_min}s  max: {warm_max}s")
        print(f"Run log holds {len(logged)}/10 of these calls.")
        print(f"Wrote {out_path}")
        return 0 if ok == 10 else 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
