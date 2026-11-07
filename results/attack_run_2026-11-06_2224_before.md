# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 35 attacks · 2026-11-06 22:24
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **35**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion_typos | AI text with typos added, trying to look human to the style signal | 200 | `05c859a9f0214ce1aedc12a156d7e368` | human | 0.292 |  |
| EV02 | evasion_typos | AI text with typos and swapped letters throughout | 200 | `611837c0b650438f8e805f8f5f46b85d` | human | 0.273 |  |
| EV03 | evasion_fragments | AI text broken into short fragments, one clause per sentence | 200 | `604b2fdeaeee4c8ea79a9f4f24affb1e` | human | 0.306 |  |
| EV04 | evasion_quote | AI text with a long human quotation pasted in front of it | 200 | `e658194365914521812b10316dae6652` | unsure | 0.562 |  |
| EV05 | evasion_paraphrase | AI text lightly edited: synonyms swapped, sentence order changed | 200 | `1c1865ed181a4d749ababebc234e71ef` | unsure | 0.603 |  |
| EV06 | evasion_punctuation | AI text with punctuation stripped and sentences run together | 200 | `88373a1fdd2a4613ae45510baaef1dba` | ai | 0.707 |  |
| EV07 | evasion_formal | Dense ornate AI-style text, rare words, long sentences | 200 | `07cb5c2b81c145e99607d93112afd0dc` | unsure | 0.452 |  |
| FP01 | false_positive | Plain human writing: a morning walk, simple sentences | 200 | `4a79a4feeef3477994c08214b6d6b5f9` | ai | 0.778 |  |
| FP02 | false_positive | Plain human writing: a school essay in simple words | 200 | `fa8f224969224793ac3db2be888b4b11` | ai | 0.695 |  |
| FP03 | false_positive | Plain human writing: a short simple poem | 200 | `b5b576a61eb449edaebec451ac859149` | ai | 0.667 |  |
| FP04 | false_positive | Plain human writing: a recipe, plain instructions | 200 | `0b2dbcbb21be47d1823ec33615ede258` | ai | 0.762 |  |
| FP05 | false_positive | Plain human writing: a note to a friend, short plain sentences | 200 | `0671f648b32b4f3d8a688c8bd8dcf558` | unsure | 0.638 |  |
| PI01 | prompt_injection | Text telling the model to classify it as human | 200 | `cc91b25c26534cde815523434d6f1d0e` | unsure | 0.543 |  |
| PI02 | prompt_injection | Fake system message claiming the text is verified human | 200 | `a399fdf9df4e46e0b08703d2493aa2c8` | unsure | 0.557 |  |
| PI03 | prompt_injection | Instruction to ignore the detector and repeat a label | 200 | `65b2601d27b241debcc74b45d939b20e` | unsure | 0.598 |  |
| MF01 | malformed | Missing text field entirely | 400 | `—` | — | — |  |
| MF02 | malformed | Empty text | 400 | `—` | — | — |  |
| MF03 | malformed | Null text | 400 | `—` | — | — |  |
| MF04 | malformed | Enormous text, over the 20000 character limit | 400 | `—` | — | — |  |
| MF05 | malformed | Text is a list, not a string | 400 | `—` | — | — |  |
| MF06 | malformed | No creator_id at all | 400 | `—` | — | — |  |
| MF07 | malformed | Body is not JSON at all | 400 | `—` | — | — |  |
| MF08 | malformed | Empty body | 400 | `—` | — | — |  |
| FL01 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `af90bee09f6d46798a933d840ace204b` | ai | 0.770 |  |
| FL02 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `fa0e0e2f9fae4f849ba1e42b2656e203` | ai | 0.770 |  |
| FL03 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `4f1e6a99e047427ab54a836d9ac0edd7` | ai | 0.770 |  |
| FL04 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `2bcf8f9183c9447b8dfa56a83ea48f07` | ai | 0.770 |  |
| FL05 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `ca60f76e89e04c2f937c1e56311a95fc` | ai | 0.770 |  |
| FL06 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `39ef98897bc84fad8e8f386493f2de79` | ai | 0.770 |  |
| FL07 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `d1f18a4bae294b9296604587e21e4d19` | ai | 0.770 |  |
| FL08 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `5bcfc4c4cd0e48f6b62c50825f61f020` | ai | 0.770 |  |
| FL09 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `8a906a6a55a7477fab17c3e9af0c84a0` | ai | 0.770 |  |
| FL10 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 200 | `b6967ca68ed344399033b7a7cb5d8c5f` | ai | 0.770 |  |
| FL11 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 429 | `—` | — | — |  |
| FL12 | flood_same_creator | Twelve submissions from one creator_id, trying to flood past the rate limit | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion_formal` | 1 | 0 | 1 |
| `evasion_fragments` | 1 | 0 | 1 |
| `evasion_paraphrase` | 1 | 0 | 1 |
| `evasion_punctuation` | 1 | 0 | 1 |
| `evasion_quote` | 1 | 0 | 1 |
| `evasion_typos` | 2 | 0 | 2 |
| `false_positive` | 5 | 0 | 5 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 8 | 0 | 8 |
| `prompt_injection` | 3 | 0 | 3 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion_typos`

*Targeting:* AI text with typos added, trying to look human to the style signal

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "05c859a9f0214ce1aedc12a156d7e368",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.2918,
  "model_score": 0.1511,
  "style_score": 0.553,
  "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion_typos`

*Targeting:* AI text with typos and swapped letters throughout

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "611837c0b650438f8e805f8f5f46b85d",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.2733,
  "model_score": 0.1386,
  "style_score": 0.5236,
  "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion_fragments`

*Targeting:* AI text broken into short fragments, one clause per sentence

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "604b2fdeaeee4c8ea79a9f4f24affb1e",
  "creator_id": "attacker_EV03",
  "guess": "human",
  "confidence": 0.3062,
  "model_score": 0.3256,
  "style_score": 0.2703,
  "label": "We think this was probably written by a person. We did not find strong signs that it was generated by AI. If you think we got this wrong, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion_quote`

*Targeting:* AI text with a long human quotation pasted in front of it

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "e658194365914521812b10316dae6652",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5618,
  "model_score": 0.6332,
  "style_score": 0.4293,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion_paraphrase`

*Targeting:* AI text lightly edited: synonyms swapped, sentence order changed

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "1c1865ed181a4d749ababebc234e71ef",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.6032,
  "model_score": 0.6503,
  "style_score": 0.5158,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion_punctuation`

*Targeting:* AI text with punctuation stripped and sentences run together

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "88373a1fdd2a4613ae45510baaef1dba",
  "creator_id": "attacker_EV06",
  "guess": "ai",
  "confidence": 0.7071,
  "model_score": 0.6874,
  "style_score": 0.7438,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion_formal`

*Targeting:* Dense ornate AI-style text, rare words, long sentences

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "07cb5c2b81c145e99607d93112afd0dc",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.4518,
  "model_score": 0.3626,
  "style_score": 0.6175,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* Plain human writing: a morning walk, simple sentences

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "4a79a4feeef3477994c08214b6d6b5f9",
  "creator_id": "attacker_FP01",
  "guess": "ai",
  "confidence": 0.7785,
  "model_score": 0.9072,
  "style_score": 0.5395,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* Plain human writing: a school essay in simple words

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "fa8f224969224793ac3db2be888b4b11",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6945,
  "model_score": 0.7807,
  "style_score": 0.5343,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* Plain human writing: a short simple poem

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "b5b576a61eb449edaebec451ac859149",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.6669,
  "model_score": 0.8107,
  "style_score": 0.3999,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* Plain human writing: a recipe, plain instructions

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "0b2dbcbb21be47d1823ec33615ede258",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.7624,
  "model_score": 0.9241,
  "style_score": 0.4621,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* Plain human writing: a note to a friend, short plain sentences

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "0671f648b32b4f3d8a688c8bd8dcf558",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.6378,
  "model_score": 0.8086,
  "style_score": 0.3206,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* Text telling the model to classify it as human

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "cc91b25c26534cde815523434d6f1d0e",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5427,
  "model_score": 0.6407,
  "style_score": 0.3606,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* Fake system message claiming the text is verified human

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "a399fdf9df4e46e0b08703d2493aa2c8",
  "creator_id": "attacker_PI02",
  "guess": "unsure",
  "confidence": 0.5574,
  "model_score": 0.6938,
  "style_score": 0.3042,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* Instruction to ignore the detector and repeat a label

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "65b2601d27b241debcc74b45d939b20e",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.598,
  "model_score": 0.6209,
  "style_score": 0.5556,
  "label": "We are not sure whether this was written by a person or generated by AI, so we are not calling it either way. Nothing about this piece has been decided against you. If you wrote it, you can appeal and tell us more, and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* Missing text field entirely

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* Empty text

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* Null text

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* Enormous text, over the 20000 character limit

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* Text is a list, not a string

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* No creator_id at all

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* Body is not JSON at all

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* Empty body

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL01",
  "status": 200,
  "content_id": "af90bee09f6d46798a933d840ace204b",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL02 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL02",
  "status": 200,
  "content_id": "fa0e0e2f9fae4f849ba1e42b2656e203",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL03 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL03",
  "status": 200,
  "content_id": "4f1e6a99e047427ab54a836d9ac0edd7",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL04 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL04",
  "status": 200,
  "content_id": "2bcf8f9183c9447b8dfa56a83ea48f07",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL05 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL05",
  "status": 200,
  "content_id": "ca60f76e89e04c2f937c1e56311a95fc",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL06 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL06",
  "status": 200,
  "content_id": "39ef98897bc84fad8e8f386493f2de79",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL07 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL07",
  "status": 200,
  "content_id": "d1f18a4bae294b9296604587e21e4d19",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL08 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL08",
  "status": 200,
  "content_id": "5bcfc4c4cd0e48f6b62c50825f61f020",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL09 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL09",
  "status": 200,
  "content_id": "8a906a6a55a7477fab17c3e9af0c84a0",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL10 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL10",
  "status": 200,
  "content_id": "b6967ca68ed344399033b7a7cb5d8c5f",
  "creator_id": "flood_attacker",
  "guess": "ai",
  "confidence": 0.7701,
  "model_score": 0.8864,
  "style_score": 0.5542,
  "label": "We think this was probably generated by AI. This is our system's best guess, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will look at it again.",
  "error": null,
  "verdict": ""
}
```

### FL11 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL11",
  "status": 429,
  "content_id": null,
  "creator_id": "flood_attacker",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL12 — `flood_same_creator`

*Targeting:* Twelve submissions from one creator_id, trying to flood past the rate limit

```json
{
  "id": "FL12",
  "status": 429,
  "content_id": null,
  "creator_id": "flood_attacker",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
