# Attack set used in unit 8

**This is not the staff attack set.** The staff set arrives as a zip from
the TF, and no zip or download link was supplied with this unit's brief.
So this set was constructed for this run, in the exact format
`run_attacks.py` reads (`attacks.csv` and
`attacks_malformed_requests.csv`, with `id`, `family`, `targets`, and
`text` / `raw_body` columns), covering the families the brief names:
evasion (typos, fragments, pasted quotation, paraphrase, stripped
punctuation, ornate text), false positives (plain human writing),
prompt injection, malformed requests, and a 12-row flood from one
creator. 35 rows in total: 15 in `attacks.csv`, 20 in
`attacks_malformed_requests.csv` (8 malformed + 12 flood).

If the staff `attack_set.zip` arrives, run it with
`python run_attacks.py --set <folder>` the same way and compare — the
before/after numbers in the README are for this set only, and that is
stated there.
