# Capstone trials — 3 trials per criterion

Run 2026-11-10T17:58:55+00:00Z
by `.venv/bin/python run_trials.py`. Criteria committed in
`6fd70b2` (add capstone criteria) before any of these runs.
Nothing was changed between trials.

First attempt (before this run): trial 1's first /submit timed
out after 180s and left no run-log record — the model load hung
on that server start. A manual first /submit on a fresh server
minutes later took 16.09s and returned 200, so the service
itself was fine; the stall was not reproduced. The script was
made robust (a timed-out call is recorded as a miss for that
trial instead of crashing the run) and the trials were re-run.

Second attempt: the three trials ran, but the checker in the
script was wrong — it looked for fields named `status` and
`duration`, while the run log actually records `status_code`
and `duration_ms`, and it snapshotted the log after /ping and
then reported /ping unlogged. So C1 and the logged half of C4
were scored 0/3 by the checker, not by the service: the 400s
themselves were 4/4, and the log held the entries. The checker
was fixed (right field names, snapshot before /ping) and the
trials were re-run from scratch.

That clean re-run is the BEFORE set, saved as
results/trials_2026-11-10_before.md: all five criteria held
3/3 (first calls 10.83s / 12.36s / 10.25s, warm means 0.75s /
0.75s / 0.58s). THIS file is the AFTER set, run after the
Milestone 6 improvement (the model is preloaded at startup,
so the first submission is warm). Nothing else changed.

## Method

- Each trial starts the service fresh with the one command
  from RUNNING.md (`.venv/bin/python app.py`, port 5003) and
  kills it at the end. A fresh start per trial is what makes
  the first-call criterion (C5) a real measurement each time.
- Each trial sends, in order: 1x POST /ping, 1x first
  /submit (AI_GENERIC, model load included), 9x warm /submit
  (the other 9 texts from measure_cost.py), 4x bad inputs
  (the Unit 7 shapes: text missing, empty, null, over 20,000
  characters). All times are client-side wall clock.
- Good submits in a trial share one fresh creator_id (10
  calls = the 10/minute limit). Each bad input has its own
  creator_id, so no window is ever tripped.
- After the calls, the trial reads logs/runs.jsonl back and
  matches every request it sent (C1).

## Trial 1

- Creator: `trial_1_20261110_175815`
- Startup: /health answered after 9.3s
- C2 run path: /ping -> 200 (0.0s)
- C5 first call: 1.03s (status 200, guess unsure)
- C3 warm runs: mean 0.43s (9/9 returned 200)

  | text | status | seconds | guess |
  |---|---|---|---|
  | ai-sysworks | 200 | 0.73 | unsure |
  | ai-fastpaced | 200 | 0.59 | unsure |
  | human-diwali | 200 | 0.44 | human |
  | human-ornate | 200 | 0.38 | human |
  | human-fragment | 200 | 0.39 | human |
  | human-train | 200 | 0.32 | unsure |
  | human-poem | 200 | 0.37 | unsure |
  | borderline-paraphrase | 200 | 0.30 | unsure |
  | human-walk | 200 | 0.39 | unsure |

- C4 bad inputs: 4/4 returned 400, 4/4 left a run-log record

  | bad input | status | seconds |
  |---|---|---|
  | text missing | 400 | 0.01 |
  | text empty | 400 | 0.00 |
  | text null | 400 | 0.00 |
  | text over 20,000 chars | 400 | 0.00 |

- C1 run log: 15 new entries, required fields present: True, /ping logged: True, /submit 200 records for this trial: 10/10, bad-input records: 4/4

## Trial 2

- Creator: `trial_2_20261110_175815`
- Startup: /health answered after 11.61s
- C2 run path: /ping -> 200 (0.0s)
- C5 first call: 0.45s (status 200, guess unsure)
- C3 warm runs: mean 0.35s (9/9 returned 200)

  | text | status | seconds | guess |
  |---|---|---|---|
  | ai-sysworks | 200 | 0.22 | unsure |
  | ai-fastpaced | 200 | 0.31 | unsure |
  | human-diwali | 200 | 0.41 | human |
  | human-ornate | 200 | 0.39 | human |
  | human-fragment | 200 | 0.48 | human |
  | human-train | 200 | 0.32 | unsure |
  | human-poem | 200 | 0.31 | unsure |
  | borderline-paraphrase | 200 | 0.34 | unsure |
  | human-walk | 200 | 0.33 | unsure |

- C4 bad inputs: 4/4 returned 400, 4/4 left a run-log record

  | bad input | status | seconds |
  |---|---|---|
  | text missing | 400 | 0.00 |
  | text empty | 400 | 0.00 |
  | text null | 400 | 0.00 |
  | text over 20,000 chars | 400 | 0.00 |

- C1 run log: 15 new entries, required fields present: True, /ping logged: True, /submit 200 records for this trial: 10/10, bad-input records: 4/4

## Trial 3

- Creator: `trial_3_20261110_175815`
- Startup: /health answered after 6.19s
- C2 run path: /ping -> 200 (0.0s)
- C5 first call: 0.37s (status 200, guess unsure)
- C3 warm runs: mean 0.34s (9/9 returned 200)

  | text | status | seconds | guess |
  |---|---|---|---|
  | ai-sysworks | 200 | 0.22 | unsure |
  | ai-fastpaced | 200 | 0.31 | unsure |
  | human-diwali | 200 | 0.48 | human |
  | human-ornate | 200 | 0.38 | human |
  | human-fragment | 200 | 0.40 | human |
  | human-train | 200 | 0.32 | unsure |
  | human-poem | 200 | 0.30 | unsure |
  | borderline-paraphrase | 200 | 0.30 | unsure |
  | human-walk | 200 | 0.33 | unsure |

- C4 bad inputs: 4/4 returned 400, 4/4 left a run-log record

  | bad input | status | seconds |
  |---|---|---|
  | text missing | 400 | 0.05 |
  | text empty | 400 | 0.00 |
  | text null | 400 | 0.00 |
  | text over 20,000 chars | 400 | 0.00 |

- C1 run log: 15 new entries, required fields present: True, /ping logged: True, /submit 200 records for this trial: 10/10, bad-input records: 4/4

## Outcomes across the three trials

Target held or not, per criterion, per trial. These are the
observed results; the verdicts table, the diagnosis for any
miss, and the one improvement are Milestone 6.

| Criterion | Target | Trial 1 | Trial 2 | Trial 3 |
|---|---|---|---|---|
| C1 every run logged | all 15 requests logged, fields present | held | held | held |
| C2 run path works | /ping 200 | held | held | held |
| C3 warm run under 2s | warm mean < 2s | held | held | held |
| C4 bad path 400 + logged | 4/4 400s, 4/4 logged | held | held | held |
| C5 first call within 20s | first call < 20s | held | held | held |

- Python: 3.12.3
