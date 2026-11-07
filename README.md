# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

Provenance Guard is a small backend service a writing site could plug in.
Text comes in, and what comes back is a guess, a confidence score, the exact
words a reader would see, and a way for the writer to push back.

The path a submission takes, from arriving to the label a reader sees:

1. **It arrives** — `POST /submit` receives JSON with `text` and
   `creator_id`. If the text is missing, empty, not a string, under 20
   characters, or over 20,000 characters, the service answers 400 and
   logs a rejection. It never becomes a decision.
2. **Signal one reads it** — `detector.model_signal` runs a local GPT-2
   model and asks how predictable the text is (perplexity, squashed to
   0–1). Predictable text scores high, surprising text scores low.
3. **Signal two measures it as text** — `stylometry.style_signal`
   measures sentence-length spread, word variety, and punctuation
   density, and combines them into a second 0–1 score. It never reads
   what the text means.
4. **The two scores become one** — `scoring.combine_signals` takes a
   weighted average (model 0.65, style 0.35) and, when the two signals
   disagree by 0.50 or more, pulls the result back toward unsure.
5. **The score becomes words** — `scoring.score_to_label` turns the
   combined score into one of three full-sentence labels a reader can
   understand, with no mention of thresholds or confidence numbers.
6. **The decision is written down** — `audit.log_decision` appends one
   JSON line to `logs/audit.jsonl` with the timestamp, content ID,
   creator ID, guess, all three scores, the label, and the status
   `decided`. The log is append-only; nothing is ever overwritten.
7. **The writer can push back** — `POST /appeal` takes a `content_id`
   and the writer's reasoning, records the appeal in the log next to the
   original decision, moves the item to `under_review`, and confirms.
   No automatic re-checking happens.

**Stretch added in this unit:** `GET /content/<id>` returns one item's
current status (`decided` or `under_review`), its guess, combined score,
and label, without reading the whole log.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model
(GPT-2, run locally). It is measured as perplexity: low perplexity means
the model could have guessed the next words easily, high perplexity means
the text surprised it. The score is squashed to 0–1, higher meaning more
likely AI.

**Why that might differ between human and AI writing:** A language model
writes by repeatedly picking a likely next word, so text a model produced
tends to be text a model finds easy to predict. Human writing wanders
more — odd word choices, abrupt turns, the specific rather than the
typical.

**What it can't see:** Authorship. Predictability is not the same thing
as who wrote something. It rewards common words in short, ordinary
sentences, so a second-language writer sticking to vocabulary they are
sure of, a younger writer, or anyone writing plainly on purpose scores
about as machine-like as machine writing does. Dense, ornate prose often
goes the other way and reads as human, because rare words are what a
language model fails to predict. The writers this signal is most likely
to accuse are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text, without understanding a
word of it: sentence-length spread (the coefficient of variation of
sentence lengths in words), type-token ratio (unique words over total
words), and punctuation density (punctuation characters over total
characters, with semicolons, colons, dashes and brackets counting
double). Each is mapped onto an AI-like component and combined
0.40 / 0.35 / 0.25 into one 0–1 score, higher meaning more likely AI.

**Why that might differ between human and AI writing:** Generated prose
tends toward even, mid-length sentences and a narrower band of
vocabulary, because that is what "most likely next word" produces on
average. Human writing is lumpier — a three-word sentence next to a
forty-word one, a wider vocabulary, more varied punctuation.

**What it can't see:** Meaning. It has no idea what the text says.
Anything that changes the shape without changing the substance moves
it — typos, broken-up sentences, a pasted quotation. That is very cheap
to do on purpose. It also falls as text gets longer (common words
repeat), so two texts of very different lengths are not directly
comparable on word variety alone.

### The combining rule

**The rule:** A weighted average, then a disagreement rule. The model
signal counts more because it reads the text; the style signal counts
less because it only measures shape, which is cheap to change on
purpose. When the two signals disagree by 0.50 or more, the honest
answer is uncertainty, not whichever signal happened to win, so the
combined score is pulled 40% of the way back toward 0.50 (unsure).

**The numbers:** model 0.65, style 0.35. Disagreement threshold 0.50,
pull toward 0.50 of 0.40. Thresholds: human at 0.35 and below, AI at
0.65 and above, unsure in between. All weights and thresholds live in
`config.py` (`WEIGHT_MODEL_SIGNAL`, `WEIGHT_STYLE_SIGNAL`,
`HUMAN_THRESHOLD`, `AI_THRESHOLD`).

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**
In a route test with a stubbed model signal, generic even-sentence
text scored model 0.92 against style 0.51 — a split of 0.41, just
under the disagreement threshold, so the weighted average stood and
the combined score was 0.78, high-confidence AI. The rule only bites
on a wider split: model 0.90 against style 0.10 is pulled from 0.62
to 0.57, landing in unsure rather than almost-AI. The limit this
shows is real — when the model signal is confident about plain,
predictable writing, weighting alone cannot save a human writer, which
is why the unsure band and the appeal path have to do the protecting
instead.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again. |
| unsure | 0.35 – 0.65 | We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again. |
| high-confidence AI | 0.65 – 1.00 | We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again. |

**Why I worded the "unsure" one this way:**
It has to admit uncertainty without sounding like an accusation, because
the person reading it may well have written every word themselves. So
it says plainly that nothing has been decided against them, and it
gives them something to do next — appeal and tell us more — instead of
leaving them with a vague verdict and no way forward. Every label ends
with the appeal path for the same reason: a guess is not a verdict, and
the reader should always know how to challenge it.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "creator_id": "..."}'
```

```json

```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json

```

---

## How I Used AI

I used Muse (the AI assistant) to build this project end to end from the
starter repo and the brief, and I reviewed the code and the numbers it
produced before submitting. Two specific moments:

**Moment 1**

- *What I asked for:* "Check each of my five criteria: could someone
  else check it without asking me what I meant?"
- *What came back:* Criterion 2 said the two groups should score
  "noticeably apart", and criterion 3 said every label should be
  "reachable in principle" — neither of which a stranger could check.
- *What I changed:* Criterion 2 became "at least 0.30 apart on the mean
  combined score", and criterion 3 became "each label appears at least
  once across 9 calibration inputs". The criteria themselves are mine;
  the AI only tested whether they were checkable.

**Moment 2**

- *What I asked for:* "What happens to a 0.9 / 0.1 split under a plain
  weighted average?"
- *What came back:* With model 0.65 / style 0.35, a 0.9 model score
  against a 0.1 style score lands at 0.62 — just under high-confidence
  AI, decided almost entirely by one signal disagreeing with the other.
- *What I changed:* I added the disagreement rule in
  `scoring.py::combine_signals`: a split of 0.50 or more is pulled 40%
  of the way back toward 0.50, so that same split now lands at 0.57,
  in unsure, instead of almost-AI.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
