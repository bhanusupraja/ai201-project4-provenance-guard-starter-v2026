# Acceptance criteria — Capstone (Provenance Guard, Shape A)

Five criteria that say what "working" means for this capstone, written
before any test runs, so the standard was set before any results were
seen. Each names a number or something plainly observable, and each has
its reason underneath.

> Missing my own targets costs me nothing. Setting a target so easy I
> can't miss it does.

---

## 1. Every run is logged

In each of three trials, every run appears in `logs/runs.jsonl`, each
with a timestamp, endpoint, status, and duration.

**Why this target:** If a run leaves no record, a failure or an
attack shows up only as an absence, and I can never find it.

---

## 2. The run path works

In each of three trials, the one command starts the service and
`POST /ping` answers 200.

**Why this target:** If the one command does not start the service,
nothing in this unit can be tested at all.

---

## 3. A warm run is fast enough

In each of three trials, the mean time of the warm runs stays under
2 seconds.

**Why this target:** If a warm run is slow, the service feels broken
even when the answer is right, so the bar has to stay tight.

---

## 4. The bad path is handled and logged

In each of three trials, all 4 bad inputs — text missing, text empty,
text null, text over 20,000 characters — return 400 and still leave a
record in the run log.

**Why this target:** The 400 is only half the job — the record is
what proves the service saw the bad input and handled it instead of
crashing.

---

## 5. The first call, model loading included

In each of three trials, the first submission after starting the
service — model loading included — finishes within 20 seconds.

**Why this target:** 20 seconds bounds the worst case — a user
starting the service knows the longest they will ever wait for a
first answer.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     REVISIONS — read this before you change anything above, once this
     file is committed.

     If a criterion turns out to be BROKEN rather than merely unmet, it
     can be revised, and that earns credit. But never delete or edit the
     original line. Add the revision underneath, like this:

         ## 2. The run path works

         In each of three trials, the one command starts the service
         and `POST /ping` answers 200.

         **Why this target:** ...

         > **Revised:** ...
         >
         > **Why revised:** ...

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it
     costs you the point. A number you missed stays where it is, gets
     diagnosed, and gets a fix attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
