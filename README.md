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

All three labels were reached in this run, with the real GPT-2 model
loaded (first submission took about 12 seconds while the model loaded;
later ones took about a second). The same run also produced a human
label (combined 0.1597, model 0.1456, style 0.1859) and an unsure label
(combined 0.3806, model 0.4302, style 0.2885) on the other two
submissions below. `python test.py` in this environment: 9 passed,
0 failed, 0 to look at.

One environment note, honestly recorded: installing torch from PyPI
stalled twice at about 268 MB of 539 MB, so in this environment torch
2.5.1+cpu was installed from the PyTorch CPU index instead
(`pip install --index-url https://download.pytorch.org/whl/cpu
"torch==2.5.1+cpu"`), which is inside the `torch>=2.2,<3.0` range in
`requirements.txt`. The first GPT-2 download also failed once through
the proxy and succeeded on a retry with `HF_HUB_DISABLE_XET=1`.

**A submission**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.", "creator_id": "supraja"}'
```

```json
{
  "combined_score": 0.7701,
  "confidence": 0.7701,
  "content_id": "337f4c74b80842678e2d1592cc1b1beb",
  "guess": "ai",
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "model_score": 0.8864,
  "status": "decided",
  "style_score": 0.5542
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "337f4c74b80842678e2d1592cc1b1beb", "reasoning": "I wrote every word of this myself. I was writing a formal report, so the sentences came out even and plain on purpose."}'
```

```json
{
  "content_id": "337f4c74b80842678e2d1592cc1b1beb",
  "message": "Your appeal has been recorded. The item is now under review and a person will look at it again. No automatic re-check has been run.",
  "reasoning": "I wrote every word of this myself. I was writing a formal report, so the sentences came out even and plain on purpose.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=10"
```

```json
{
  "count": 5,
  "entries": [
    {
      "combined_score": 0.7701,
      "content_id": "337f4c74b80842678e2d1592cc1b1beb",
      "creator_id": "supraja",
      "guess": "ai",
      "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
      "model_score": 0.8864,
      "status": "decided",
      "style_score": 0.5542,
      "timestamp": "2026-11-07T03:21:01+00:00"
    },
    {
      "combined_score": 0.1597,
      "content_id": "1c86c6deacc749b9852b7732861b811f",
      "creator_id": "supraja",
      "guess": "human",
      "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.",
      "model_score": 0.1456,
      "status": "decided",
      "style_score": 0.1859,
      "timestamp": "2026-11-07T03:21:04+00:00"
    },
    {
      "combined_score": 0.3806,
      "content_id": "156d46e72dd74dc0833cf8ec0668543a",
      "creator_id": "supraja",
      "guess": "unsure",
      "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
      "model_score": 0.4302,
      "status": "decided",
      "style_score": 0.2885,
      "timestamp": "2026-11-07T03:21:05+00:00"
    },
    {
      "content_id": "337f4c74b80842678e2d1592cc1b1beb",
      "creator_id": "supraja",
      "event": "appeal",
      "reasoning": "I wrote every word of this myself. I was writing a formal report, so the sentences came out even and plain on purpose.",
      "status": "under_review",
      "timestamp": "2026-11-07T03:21:07+00:00"
    },
    {
      "creator_id": "supraja",
      "detail": "text missing, empty, or not a string",
      "event": "rejected",
      "reason": "bad_input",
      "status": "rejected",
      "timestamp": "2026-11-07T03:21:07+00:00"
    }
  ]
}
```

One honest finding from this run, kept in because it is the point of
the project: plain human writing also scored high-confidence AI here —
"I like to go for a walk in the morning…" scored model 0.9072,
combined 0.7785, label `ai`. That is a false positive, and it is why
criterion 1 exists and why the appeal path matters.

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

**My limits:** 10 submissions per minute, 200 per day, per creator_id.

**Why those numbers and not others:** A real writer submits their own work a few times an hour — 10 a minute never gets in their way. A script sending a thousand variations to map my thresholds hits the wall in under a second: after 10 in a minute it gets 429s, and after 200 in a day it is done until tomorrow. A stricter limit, like 3 a minute, would start punishing a writer pasting a batch of poems; a looser one, like 100 a minute, would let a script walk the whole score range in a minute. 10 and 200 is the middle that is liveable for the first person and hostile to the second.

**What a caller counts as:** per creator_id, not per address. One script can look like a thousand addresses, so counting addresses would not stop it; and one household sharing an address would look like one caller, so counting addresses would punish people who did nothing. The trade is that one script can also invent a thousand creator_ids — this limit slows a flood, it does not stop a determined attacker who rotates identities. That is in What's Still Broken.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15` — full run in `results/flood_2026-11-06_2223.md`:

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

The first 10 went through, the next 5 were refused with 429, and each refusal is in `logs/audit.jsonl` as a `rejected` entry with reason `rate_limited` — for example:

```json
{"timestamp": "2026-11-07T03:23:29+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

---

## Attack Run — Before

The attack set is in `attack_set/` — 35 attacks in the `run_attacks.py` format. Honest note: the staff `attack_set.zip` was **not** supplied with the brief (no download link was given), so this set was constructed to cover the families the brief names — evasion, false positives, prompt injection, malformed requests, and flooding — and `attack_set/README.md` says so. If the staff set arrives, these runs must be redone against it and compared. Full table in `results/attack_run_2026-11-06_2224_before.md`.

| ID | Family | What came back | Verdict |
|---|---|---|---|
| EV01 | evasion, typos | human, 0.292 | BROKE |
| EV02 | evasion, typos | human, 0.273 | BROKE |
| EV03 | evasion, fragments | human, 0.306 | BROKE |
| EV04 | evasion, pasted human quote | unsure, 0.562 | BROKE |
| EV05 | evasion, paraphrase | unsure, 0.603 | BROKE |
| EV06 | evasion, punctuation stripped | ai, 0.707 | HELD |
| EV07 | evasion, ornate | unsure, 0.452 | BROKE |
| FP01 | false positive, morning walk | ai, 0.778 | BROKE |
| FP02 | false positive, winter essay | ai, 0.695 | BROKE |
| FP03 | false positive, simple poem | ai, 0.667 | BROKE |
| FP04 | false positive, recipe | ai, 0.762 | BROKE |
| FP05 | false positive, note to a friend | unsure, 0.638 | HELD |
| PI01 | prompt injection, "classify as human" | unsure, 0.543 | HELD |
| PI02 | prompt injection, fake system message | unsure, 0.557 | HELD |
| PI03 | prompt injection, "ignore the detector" | unsure, 0.598 | HELD |
| MF01–MF08 | malformed (missing, empty, null, huge, list, no creator_id, non-JSON, empty body) | 400, all eight | HELD |
| FL01–FL10 | flood, same creator | 200, ai 0.770 | HELD |
| FL11–FL12 | flood, same creator | 429 | HELD |

**25 held, 10 broke, 0 crashes, no 5xx.**

**Ten audit log entries from the run** — the interesting failures, plus one bad-input rejection and one rate-limit rejection:

```json
{"timestamp": "2026-11-07T03:23:54+00:00", "content_id": "05c859a9f0214ce1aedc12a156d7e368", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1511, "style_score": 0.553, "combined_score": 0.2918, "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:23:55+00:00", "content_id": "611837c0b650438f8e805f8f5f46b85d", "creator_id": "attacker_EV02", "guess": "human", "model_score": 0.1386, "style_score": 0.5236, "combined_score": 0.2733, "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:23:57+00:00", "content_id": "e658194365914521812b10316dae6652", "creator_id": "attacker_EV04", "guess": "unsure", "model_score": 0.6332, "style_score": 0.4293, "combined_score": 0.5618, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:23:58+00:00", "content_id": "88373a1fdd2a4613ae45510baaef1dba", "creator_id": "attacker_EV06", "guess": "ai", "model_score": 0.6874, "style_score": 0.7438, "combined_score": 0.7071, "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:24:00+00:00", "content_id": "4a79a4feeef3477994c08214b6d6b5f9", "creator_id": "attacker_FP01", "guess": "ai", "model_score": 0.9072, "style_score": 0.5395, "combined_score": 0.7785, "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:24:01+00:00", "content_id": "0b2dbcbb21be47d1823ec33615ede258", "creator_id": "attacker_FP04", "guess": "ai", "model_score": 0.9241, "style_score": 0.4621, "combined_score": 0.7624, "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:24:02+00:00", "content_id": "0671f648b32b4f3d8a688c8bd8dcf558", "creator_id": "attacker_FP05", "guess": "unsure", "model_score": 0.8086, "style_score": 0.3206, "combined_score": 0.6378, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:24:03+00:00", "content_id": "cc91b25c26534cde815523434d6f1d0e", "creator_id": "attacker_PI01", "guess": "unsure", "model_score": 0.6407, "style_score": 0.3606, "combined_score": 0.5427, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "status": "decided"}
{"timestamp": "2026-11-07T03:24:04+00:00", "creator_id": "attacker_MF01", "event": "rejected", "status": "rejected", "reason": "bad_input", "detail": "text missing, empty, or not a string"}
{"timestamp": "2026-11-07T03:23:29+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer whose work got caught by it: **FP01**. Plain human writing — "I like to go for a walk in the morning…" — scored 0.7785 and was labelled high-confidence AI. A real person wrote that, in simple sentences, and the system accused them of it with confidence. That is the failure the improvement below is aimed at.

---

## Run Log and Verdicts

Produced by `run_eval.py::main`, against `app.py::submit` with scoring in `scoring.py::combine_signals`. Three trials per criterion; full output in `results/run_2026-11-06_2226_before.md` (before) and `results/run_2026-11-06_2229_after.md` (after). All three trials were identical to four decimal places in both runs — expected, because nothing in either signal is random: GPT-2 perplexity and the style features are deterministic for the same text.

### Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | at most 1 of 10 labelled high-confidence AI | 4 of 10 AI | 4 of 10 AI | 4 of 10 AI | **MISSED** |
| 2. score spread | mean AI at least 0.30 above mean human | AI 0.7051, human 0.2736, diff 0.4315 | same | same | **MET** |
| 3. label coverage | each label appears at least once | human 3, unsure 3, AI 3 | same | same | **MET** |
| 4. appeal | 10/10 appeals under_review with a log entry | tested by hand (run_eval.py cannot appeal): 10/10 under_review, 10 appeal entries | — | — | **MET** |
| 5. bad input | all 4 bad inputs 400, no decided entry, /ping 200 after | 4/4 400, 0 decided, ping 200 | 4/4 400 | 4/4 400 | **MET** |

### After (one improvement applied — see below)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | at most 1 of 10 labelled high-confidence AI | 0 of 10 AI | 0 of 10 AI | 0 of 10 AI | **MET** |
| 2. score spread | mean AI at least 0.30 above mean human | diff 0.4315 (scores unchanged) | same | same | **MET** |
| 3. label coverage | each label appears at least once | human 3, unsure 6, AI 0 | same | same | **MISSED** |
| 4. appeal | 10/10 appeals under_review with a log entry | not re-run — the threshold does not touch the appeal path | — | — | **MET** |
| 5. bad input | all 4 bad inputs 400, no decided entry, /ping 200 after | 4/4 400, 0 decided, ping 200 | 4/4 400 | 4/4 400 | **MET** |

**Real output from one trial**, pasted as text, naming the file and function that produced it — `run_eval.py::main`, criterion 1, trial 1, before:

```json
[
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.1597,
    "model_score": 0.1456,
    "style_score": 0.1859,
    "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.",
    "sent": "Last Diwali, my cousin Ravi burnt the payasam. Not a little burnt, pro"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7785,
    "model_score": 0.9072,
    "style_score": 0.5395,
    "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
    "sent": "I like to go for a walk in the morning. I walk to the park near my hou"
  }
]
```

**Diagnoses** — one per miss and per broken attack, stage and mechanism. The five stages are the route, signal one, signal two, the combining rule, and the label mapping.

- **Criterion 1 missed (4 of 10 own pieces accused). Stage: signal one.** Plain human writing is predictable to GPT-2 — short common sentences, ordinary words — so its model score lands at 0.78–0.92, the same range as AI text. Signal two barely helps: the walk piece has style 0.5395, and the combining rule weights signal one at 0.65, so the model score drags the combined score over the 0.65 AI line. The system is not detecting "AI-ness"; it is detecting predictability, and simple human writing is predictable.
- **EV01 and EV02 (typos) broke. Stage: signal one.** Adding typos makes AI text *unpredictable* to GPT-2, so the model score collapses from 0.8864 clean to 0.1511 and 0.1386. Signal two barely moved (0.553 vs 0.554 clean) — typos did not change the style features much — so the combined score fell to 0.29 and 0.27, labelled human. One signal doing all the work means one cheap edit defeats it.
- **EV03 (fragments) broke. Stage: signal one, same mechanism.** Breaking AI text into short fragments makes each piece easy for GPT-2 in isolation, but the perplexity across the broken text drops to a model score of 0.3256, and the style score (0.2703) does not push back. Combined 0.306, labelled human.
- **EV04 (pasted human quote) broke. Stage: the combining rule.** A long human quotation in front dilutes the AI text behind it — the score is computed over the whole submission, so the human half pulls the combined score to 0.562, unsure. There is no per-passage scoring, so a quote is a free disguise.
- **EV05 (paraphrase) broke. Stage: signal one.** Swapping synonyms and reordering sentences changes the surface enough that the model score falls from 0.8864 to 0.6503, and the style score (0.5158) does not recover it. Combined 0.603, unsure — the paraphrase did not have to be good, only different.
- **EV07 (ornate) broke. Stage: signal one.** Dense, rare-word AI text reads as *unpredictable* to GPT-2 (model 0.5046 on the harbour-style borderline, and the ornate attack at 0.452 combined), so it lands in unsure instead of AI. The detector rewards writing that is hard for the model to predict, whatever wrote it.
- **FP01–FP04 broke. Stage: signal one, same mechanism as criterion 1.** Simple human writing — a walk, an essay, a poem, a recipe — scores model 0.78–0.92 because it is predictable, and the style signal (0.40–0.54) does not pull it back below the line. FP05 held only narrowly, at 0.6378, just under the old 0.65 line.
- **EV06 was the only evasion that held before. Stage: signal two.** Stripping punctuation pushed the style score up to 0.7438 (no punctuation variety left to measure as varied), which carried the combined score to 0.707, over the line. It held by accident of the style features, not by design.
- **Prompt injection held (PI01–PI03).** The instructions inside the text pulled the AI text down from 0.77 to unsure (0.54–0.60) but never to human — because the text is scored by perplexity, not read as instructions. The model never sees the instruction as an instruction; it only sees predictable words. Holding here is luck of the mechanism, not a defence.
- **Malformed and flood held. Stage: the route.** Bad inputs are rejected at the route before any signal runs (400, logged as rejections, no decided entry), and the flood is stopped by the limiter before scoring (429, logged as rate_limited).

The pattern across all of it: **signal one decides nearly everything**. The style signal moves a little, the combining rule weights the model 0.65, and the label line sits where plain human writing already lives.

---

## The Improvement

**What I changed:** one thing only — in `config.py`, `AI_THRESHOLD` went from 0.65 to 0.80. The human threshold stays at 0.35, so the unsure band is now 0.35–0.80 instead of 0.35–0.65. No signal, no combining rule, and no label text changed.

**Which diagnosis pointed at it:** the criterion 1 / FP01–FP04 diagnosis — plain human writing scores 0.67–0.78 because it is predictable to GPT-2, and the old AI line at 0.65 sat right in the middle of that range. Moving the line above the highest plain-human score in the set (0.7785) is the smallest change that stops the accusations.

### Attack Run — After

Full table in `results/attack_run_2026-11-06_2228_after.md`. Scores are identical to before — only the labels moved.

| ID | Before | After | Verdict |
|---|---|---|---|
| EV01 | human, 0.292 | human, 0.292 | BROKE |
| EV02 | human, 0.273 | human, 0.273 | BROKE |
| EV03 | human, 0.306 | human, 0.306 | BROKE |
| EV04 | unsure, 0.562 | unsure, 0.562 | BROKE |
| EV05 | unsure, 0.603 | unsure, 0.603 | BROKE |
| EV06 | ai, 0.707 | unsure, 0.707 | BROKE |
| EV07 | unsure, 0.452 | unsure, 0.452 | BROKE |
| FP01 | ai, 0.778 | unsure, 0.778 | HELD |
| FP02 | ai, 0.695 | unsure, 0.695 | HELD |
| FP03 | ai, 0.667 | unsure, 0.667 | HELD |
| FP04 | ai, 0.762 | unsure, 0.762 | HELD |
| FP05 | unsure, 0.638 | unsure, 0.638 | HELD |
| PI01–PI03 | unsure | unsure | HELD |
| MF01–MF08 | 400 | 400 | HELD |
| FL01–FL10 | 200 | 200 | HELD |
| FL11–FL12 | 429 | 429 | HELD |

**28 held, 7 broke** (was 25 held, 10 broke).

**Did it help, and how do I know:** yes, for the thing it was aimed at — all five false positives now hold, and criterion 1 went from 4 of 10 accused to 0 of 10. But it created a new problem, and I am reporting it instead of hiding it: **criterion 3 now fails**. The highest score in the whole calibration set is the clearly-AI text at 0.7701, below the new 0.80 line, so the AI label is unreachable — in the after eval, no input at all was labelled AI (27 human, 48 unsure across the three trials). EV06 also regressed: it was the only evasion that held before, and now it is unsure too. Widening the unsure band fixed the false accusations by making the system accuse almost nothing with confidence. That is the trade, measured, not a free win.

---

## What's Still Broken

- **Every evasion still gets through (EV01–EV07).** Typos and fragments still read as human (0.27–0.31); quote, paraphrase, ornate, and punctuation attacks still land in unsure, never AI. The threshold move cannot fix these — they fail at signal one, and the line only decides what a score is *called*, not what it *is*. What I would do: add a third signal that typos cannot fake — for example, a check for edit-distance noise, or a second model with a different training mix — and re-run. Why I stopped: the brief allows exactly one improvement, and a new signal is a second one.
- **Criterion 3 is now missed.** No input reaches the AI label. What I would do: either lower the line back to somewhere between 0.78 and 0.80 and accept one false positive, or keep 0.80 and add a genuinely high-scoring AI calibration input. Why I stopped: either change is a second improvement, and the honest result is the one to report.
- **The per-creator rate limit is bypassable.** A script that rotates creator_ids gets a fresh 10 a minute each time. What I would do: add a second, coarser limit per address alongside the per-creator one, and log both. Why I stopped: that is a second change, and it would also start punishing a household sharing one address — the exact trade the README above names.
- **Prompt injection is held by luck, not by a defence.** The text is scored, not read, so an instruction inside it can only move the perplexity — but a future model that *does* read instructions would obey it. What I would do: strip or neutralise instruction-like lines before scoring, and test that the strip does not change real submissions. Why I stopped: same reason — one improvement, already used.
- **The "my own writing" set is not really mine.** The 10 pieces in `scenarios.py` were written for this project as calibration text in the student's voice; the false-positive rate they measure is about this test set, not about anyone else's writing. Before claiming the rate about real writers, the set should be the student's own diary or coursework writing.

**The trade I'd make if this ran for real:** I would keep the wider unsure band. Fewer wrong accusations means more AI text getting through — the clearly-AI text at 0.7701 now goes out as unsure instead of AI — and that is the price. The people who pay for it are the readers and moderators who get AI text they have to judge themselves; the people who would pay the other way are writers falsely accused of cheating, and a false accusation costs a real person more than a missed detection costs a platform. So: accuse less, and let unsure mean "a person decides."

---

## How I Used AI — Unit 8

Muse (this chat) ran the flood test, built the constructed attack set, ran both attack runs and both eval runs, and drafted the README sections from the measured numbers. I reviewed every number against the files in `results/` before it was written down. The improvement — widening the unsure band — was chosen from the diagnosis of the before runs, and its cost (criterion 3 failing) is reported in the README rather than smoothed over. The attack set is constructed, not the staff set; that is labelled in `attack_set/README.md` and above, and the runs must be redone if the staff zip arrives.

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

## Capstone — Show What You Know

### What This Extends

Provenance Guard — the AI201 Project 4 system in this same repository
(Units 7–8, submitted at commit `03026a4`): a Flask service that takes a
piece of writing at `POST /submit`, scores it with two signals (a local
GPT-2 perplexity signal and a stylometry signal), combines them into a
confidence score with three labels, and lets a writer appeal at
`POST /appeal`. What is new in this unit is the operational layer around
it, not the detector: the system has only ever run on a laptop, started
by hand, with no record of what it did beyond the audit log's decisions.
The capstone adds that layer — a single documented run path, structured
run logging on every request, and a measured cost per run.

### The Shape

**Shape A — Deploy and instrument.** The extension is the operational
layer: the run path (`RUNNING.md`), the instrumentation (a structured run
log with a record per request), and the numbers that come out of it
(latency and cost per run, measured, not guessed). Path B — local with
logs. The system carries GPT-2 locally (~550 MB of weights, plus torch);
a free hosting tier gives 512 MB, so it cannot fit a host, and Path B is
graded identically. The audit log from Units 7–8 stays as it is; the run
log is a new, separate record.

**Out of scope — decided now, not later:**
- No new signal, no new label, no threshold change. The detector is
  finished; this unit does not re-litigate it.
- No second retrieval strategy and no new endpoint. The capability set
  stays exactly as submitted in Unit 8.
- No hosted deployment and no interface rebuild. Path B is the run path.

### Running It

Path B — local with logs. One command, from the repo root, in the
project virtualenv:

```bash
.venv/bin/python app.py
```

That serves on `http://127.0.0.1:5000`. The full run path, the
environment it needs, and how it was verified from a clean checkout
are in [RUNNING.md](RUNNING.md) (Capstone section).

### Instrumentation

Every request writes one structured record to `logs/runs.jsonl` — see
`runlog.py`. A record holds a timestamp, a request id, the endpoint,
the method, the status code, how long it took in milliseconds, and,
when the route knows them, the creator, the content id, the text
length and a 60-character preview, the guess, the confidence, the
label, both signal scores, any error, and whether the model was
loaded. Full submission text is never written to the log. Failures
(400, 429, 503, 500) leave a record too — a failure that shows up
only as an absence is one you will never diagnose.

Ten entries from the cost-measurement run on 2026-11-10 (creator
`cost_measurement_20261110_153102`), pasted as text:

```json
{"timestamp": "2026-11-10T15:31:22+00:00", "request_id": "f4a3ff44cada", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 18091.9, "creator_id": "cost_measurement_20261110_153102", "content_id": "99eca7aaa27145ba8709e9639a34e3b8", "text_chars": 303, "text_preview": "The implementation of the proposed framework requires carefu", "guess": "unsure", "confidence": 0.7701, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.8864, "style_score": 0.5542, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:23+00:00", "request_id": "3d407dcbaea3", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 1089.8, "creator_id": "cost_measurement_20261110_153102", "content_id": "1667999ef6814e3e89066981f310666a", "text_chars": 217, "text_preview": "The system works well. It handles most cases correctly and p", "guess": "unsure", "confidence": 0.6793, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.7705, "style_score": 0.5098, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:24+00:00", "request_id": "f565a2a344e5", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 705.7, "creator_id": "cost_measurement_20261110_153102", "content_id": "516c802cbf8c4992884271f3ff816748", "text_chars": 263, "text_preview": "In today's fast-paced world, it is important to consider the", "guess": "unsure", "confidence": 0.6658, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.9558, "style_score": 0.4429, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:25+00:00", "request_id": "0ccb292fd930", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 892.4, "creator_id": "cost_measurement_20261110_153102", "content_id": "c42e85ff534341b8b4fe63b0dfaa1dbf", "text_chars": 330, "text_preview": "Last Diwali, my cousin Ravi burnt the payasam. Not a little ", "guess": "human", "confidence": 0.1597, "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.", "model_score": 0.1456, "style_score": 0.1859, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:26+00:00", "request_id": "dd56ca9e3c35", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 825.1, "creator_id": "cost_measurement_20261110_153102", "content_id": "0dd8ccea7f7f41308ab538b653bebdbc", "text_chars": 330, "text_preview": "Beneath the cracked lintel, where the monsoon had peeled the", "guess": "human", "confidence": 0.3248, "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.", "model_score": 0.1695, "style_score": 0.6132, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:26+00:00", "request_id": "c339ecfc9dc0", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 701.1, "creator_id": "cost_measurement_20261110_153102", "content_id": "8213e205ce04485ebb29358882900952", "text_chars": 319, "text_preview": "Rain. Again. The bus never came, so I walked, shoes squeakin", "guess": "human", "confidence": 0.3363, "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.", "model_score": 0.4604, "style_score": 0.1057, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:28+00:00", "request_id": "3fbb6f90c677", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 1099.0, "creator_id": "cost_measurement_20261110_153102", "content_id": "46a7885d3e744854a1b677e877850d25", "text_chars": 278, "text_preview": "I woke at five. The train was late again, forty minutes this", "guess": "unsure", "confidence": 0.3806, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.4302, "style_score": 0.2885, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:29+00:00", "request_id": "12d8ff9abfde", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 1002.1, "creator_id": "cost_measurement_20261110_153102", "content_id": "c6e9e800f1424d3ba00a57dc4444b0f1", "text_chars": 270, "text_preview": "The moon rose over the quiet harbour, and for a moment nobod", "guess": "unsure", "confidence": 0.4203, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.5046, "style_score": 0.2638, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:29+00:00", "request_id": "0156db3d85a9", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 716.0, "creator_id": "cost_measurement_20261110_153102", "content_id": "b9d136844fee4de1a869d06cdb5924a0", "text_chars": 281, "text_preview": "Putting this framework into practice means thinking hard abo", "guess": "unsure", "confidence": 0.6032, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.6503, "style_score": 0.5158, "error": null, "model_loaded": true}
{"timestamp": "2026-11-10T15:31:30+00:00", "request_id": "834d9f9503cf", "endpoint": "/submit", "method": "POST", "status_code": 200, "duration_ms": 655.1, "creator_id": "cost_measurement_20261110_153102", "content_id": "cfdac49e012245679b7ad30d98589151", "text_chars": 250, "text_preview": "I like to go for a walk in the morning. I walk to the park n", "guess": "unsure", "confidence": 0.7785, "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.", "model_score": 0.9072, "style_score": 0.5395, "error": null, "model_loaded": true}
```

### What It Costs

Cost here is seconds of compute, measured — there is no API spend,
because GPT-2 runs on this machine. Measured with
`python measure_cost.py` (10 fixed `/submit` calls; full table and
method in `results/cost_measurement.md`):

- First call, including loading GPT-2 into memory: **18.10s**
  (a second run measured 15.28s — the load cost, not the run cost).
- Warm calls, model already loaded: **mean 0.87s, median 0.83s,
  min 0.66s, max 1.12s** (the first run measured mean 0.95s,
  median 0.88s — the same picture).
- Model on disk (GPT-2): **525.4 MB**. Python 3.12.3.
- 100 warm runs a day: 100 × 0.87s = **87 seconds, about 1.4
  minutes** of compute a day, plus one model load of about 18s
  when the service starts. At this scale the cost is minutes of
  one machine's time, not money.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
