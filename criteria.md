# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** the service was built, so the standard was set before any results
were seen. Each names a number or something plainly observable, and each has
its reason underneath.

> Missing my own targets next unit costs me nothing. Setting a target so easy
> I can't miss it does.

---

## 1. At most 1 of my own 10 pieces is labelled high-confidence AI

Of 10 pieces of writing I wrote myself, at most 1 is labelled
high-confidence AI, in each of three trials.

**Why this target:** A wrong accusation costs a real writer far more than a
missed detection costs the site. One in ten is already a high price for a
person to pay for someone else's guess; more than that would mean the service
cannot be trusted on ordinary human writing, including plain writing by
second-language writers.

---

## 2. Clearly-AI and clearly-human text score at least 0.30 apart

The mean combined score of 3 pieces I am confident are AI-generated is at
least 0.30 higher than the mean combined score of 3 pieces I am confident are
human-written, in each of three trials.

**Why this target:** If the two groups do not separate by at least 0.30 on a
0–1 scale, the score is mostly noise and the labels built on it are not
saying anything. 0.30 is large enough to matter and small enough to be
honest about a detector that is known to be imperfect.

---

## 3. All three labels are reachable

Across 9 calibration inputs (3 clearly AI, 3 clearly human, 3 borderline),
each of the three labels — high-confidence human, unsure, high-confidence AI —
appears at least once.

**Why this target:** A label nobody can ever receive is not a safety valve,
it is decoration. The unsure label only protects writers if real borderline
text can actually land in it, and the human label only protects writers if
real human text can actually reach it.

---

## 4. Every appeal changes the status and is recorded

In 10 out of 10 appeal attempts on real content IDs, the item's status
becomes `under_review` and an appeal entry appears in the audit log next to
the original decision.

**Why this target:** The appeal is the only thing standing between a wrong
accusation and nothing at all. If it works only sometimes, a writer cannot
rely on it, and a 9-out-of-10 pass rate would still mean one writer in ten
had no way to push back.

---

## 5. Bad input never crashes the service and never becomes a decision

All 4 of these bad inputs — text missing, text empty, text null, text over
20,000 characters — return a 400 error, write no `decided` entry to the audit
log, and the service still answers `POST /ping` with 200 afterwards.

**Why this target:** A writing site will receive malformed input, and a
crash or a silent wrong decision on it is a real failure, not an edge case.
The 20,000-character limit is the line I chose: long enough for a poem or an
essay, short enough that one submission cannot stall the service for
everyone else.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, it can
     be revised, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
