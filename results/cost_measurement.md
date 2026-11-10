# Cost measurement — one run of Provenance Guard

Measured 2026-11-10T15:31:30+00:00Z
by `python measure_cost.py` (10 fixed /submit calls, creator `cost_measurement_20261110_153102`).

## Method

- Cost here is **seconds of compute**, measured wall-clock
  from the client side. There is no API spend: GPT-2 runs on
  this machine, so a run costs time, not money.
- The first call includes loading GPT-2 into memory and is
  reported on its own. Calls 2–10 are warm: the model is
  already loaded, which is the state the service is in
  whenever it is actually serving.
- The server was started by the script itself on port 5001
  and killed when the script ended.

## Per-call results

| # | text | status | seconds | guess |
|---|---|---|---|---|
| 1 | ai-generic | 200 | 18.10 | unsure |
| 2 | ai-sysworks | 200 | 1.12 | unsure |
| 3 | ai-fastpaced | 200 | 0.71 | unsure |
| 4 | human-diwali | 200 | 0.90 | human |
| 5 | human-ornate | 200 | 0.83 | human |
| 6 | human-fragment | 200 | 0.76 | human |
| 7 | human-train | 200 | 1.11 | unsure |
| 8 | human-poem | 200 | 1.01 | unsure |
| 9 | borderline-paraphrase | 200 | 0.72 | unsure |
| 10 | human-walk | 200 | 0.66 | unsure |

## Summary

- Calls that returned 200: 10 of 10
- First call (includes model load): 18.10s
- Warm calls (2–10): mean 0.87s, median 0.83s, min 0.66s, max 1.12s
- Run-log check: 10 of 10 calls appear in `logs/runs.jsonl` for this creator_id
- Model on disk (GPT-2): 525.4 MB
- Python: 3.12.3

## What 100 runs a day would cost

100 warm runs x 0.87s = 87.0s (about 1.4 minutes) of compute a day, plus one model load of about 18.1s when the service starts. At this scale the cost is minutes of one machine's time, not money.
