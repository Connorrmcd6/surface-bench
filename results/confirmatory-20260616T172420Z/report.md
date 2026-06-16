# Surface agent-impact benchmark

## Spend

**Total: $62.16** (estimated from token usage).

| Model | Spend |
|---|---|
| gemini | $8.99 |
| gpt | $5.95 |
| haiku | $5.29 |
| opus | $28.59 |
| sonnet | $13.33 |

## The gradient — Surface effect (C2−C1 success) by complexity tier

### gemini

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T1 — buried (truth needs tracing) | +52 pp [+37, +67] ✓ | +48 pp [+33, +63] ✓ |
| T2 — premise (invariant is load-bearing) | +99 pp [+96, +100] ✓ | +91 pp [+84, +97] ✓ |

### gpt

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T1 — buried (truth needs tracing) | +100 pp [+100, +100] ✓ | +98 pp [+95, +100] ✓ |
| T2 — premise (invariant is load-bearing) | +100 pp [+100, +100] ✓ | +93 pp [+86, +99] ✓ |

### haiku

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T1 — buried (truth needs tracing) | +90 pp [+82, +97] ✓ | +53 pp [+38, +67] ✓ |
| T2 — premise (invariant is load-bearing) | +70 pp [+59, +81] ✓ | +69 pp [+56, +80] ✓ |

### opus

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T1 — buried (truth needs tracing) | +70 pp [+57, +82] ✓ | +60 pp [+45, +73] ✓ |
| T2 — premise (invariant is load-bearing) | +59 pp [+47, +70] ✓ | +59 pp [+47, +70] ✓ |

### sonnet

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T1 — buried (truth needs tracing) | +92 pp [+83, +98] ✓ | +78 pp [+67, +88] ✓ |
| T2 — premise (invariant is load-bearing) | +71 pp [+60, +81] ✓ | +71 pp [+60, +81] ✓ |

## Verification — did the agent check the hidden dependency? (multi-turn)

With no doc the agent should go read the hidden code; a confident **stale** doc should suppress that check (H4). Within C1, those who verified should be correct (H5).

### gemini

| Condition | n | Verified hidden dep | When verified, correct |
|---|---|---|---|
| C0 | 130 | 100% [97–100] | 88% |
| C1 | 130 | 85% [77–90] | 20% |
| C2 | 130 | 74% [66–81] | 92% |
| C3 | 130 | 100% [97–100] | 77% |
| Cw | 130 | 100% [97–100] | 45% |

- verification `C0-C1`: +15 pp [+9, +22] ✓ significant

- verification `C2-C1`: -11 pp [-21, -1] ✓ significant
- C1 mediation (H5): verifiers 20% correct (n=110) vs non-verifiers 0% (n=20)

### gpt

| Condition | n | Verified hidden dep | When verified, correct |
|---|---|---|---|
| C0 | 130 | 96% [91–98] | 99% |
| C1 | 130 | 0% [0–3] | — |
| C2 | 130 | 2% [1–7] | 100% |
| C3 | 130 | 23% [17–31] | 100% |
| Cw | 130 | 9% [5–15] | 92% |

- verification `C0-C1`: +96 pp [+92, +99] ✓ significant

- verification `C2-C1`: +2 pp [+0, +5]
- C1 mediation (H5): verifiers — correct (n=0) vs non-verifiers 0% (n=130)

### haiku

| Condition | n | Verified hidden dep | When verified, correct |
|---|---|---|---|
| C0 | 130 | 100% [97–100] | 78% |
| C1 | 130 | 23% [17–31] | 47% |
| C2 | 130 | 25% [18–33] | 91% |
| C3 | 130 | 58% [49–66] | 77% |
| Cw | 130 | 33% [26–42] | 77% |

- verification `C0-C1`: +77 pp [+69, +84] ✓ significant

- verification `C2-C1`: +2 pp [-9, +12]
- C1 mediation (H5): verifiers 47% correct (n=30) vs non-verifiers 8% (n=100)

### opus

| Condition | n | Verified hidden dep | When verified, correct |
|---|---|---|---|
| C0 | 130 | 100% [97–100] | 91% |
| C1 | 130 | 33% [26–42] | 95% |
| C2 | 130 | 38% [30–46] | 88% |
| C3 | 130 | 29% [22–38] | 100% |
| Cw | 130 | 87% [80–92] | 89% |

- verification `C0-C1`: +67 pp [+58, +75] ✓ significant

- verification `C2-C1`: +5 pp [-7, +16]
- C1 mediation (H5): verifiers 95% correct (n=43) vs non-verifiers 0% (n=87)

### sonnet

| Condition | n | Verified hidden dep | When verified, correct |
|---|---|---|---|
| C0 | 130 | 100% [97–100] | 94% |
| C1 | 130 | 20% [14–28] | 62% |
| C2 | 130 | 18% [12–25] | 100% |
| C3 | 130 | 18% [12–25] | 100% |
| Cw | 130 | 44% [36–52] | 89% |

- verification `C0-C1`: +80 pp [+73, +86] ✓ significant

- verification `C2-C1`: -2 pp [-12, +7]
- C1 mediation (H5): verifiers 62% correct (n=26) vs non-verifiers 9% (n=104)

## gemini

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 130 | 88% [82–93] | 0% [0–3] |
| C1 — code + stale documentation | 130 | 17% [11–24] | 77% [69–83] |
| C2 — code + fresh documentation | 130 | 94% [88–97] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 130 | 77% [69–83] | 14% [9–21] |
| Cw — code + stale documentation + generic staleness warning | 130 | 45% [37–54] | 45% [37–54] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +77 pp [+69, +85] ✓ significant (Holm ✓)
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +72 pp [+63, +80] ✓ significant (Holm ✓)
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +60 pp [+50, +69] ✓ significant (Holm ✓)
- `C2-C0` fresh vs no-docs (value of accurate prose): +5 pp [-2, +12] (Holm ✗)
- `C3-Cw` surf-report vs bare warning (is the value the *fix*, not just suspicion?): +32 pp [+20, +43] ✓ significant (Holm ✓)
- `Cw-C1` bare warning vs stale (does a generic warning alone help?): +28 pp [+18, +39] ✓ significant (Holm ✓)

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 429 [394–466] | 444 | — |
| C1 | 458 [422–496] | 672 | 422 |
| C2 | 372 [348–399] | 373 | — |
| C3 | 509 [474–546] | 529 | 364 |
| Cw | 514 [478–551] | 597 | 470 |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +86 tok [+42, +131] ✓ significant
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): +29 tok [-21, +81]
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -51 tok [-101, -1] ✓ significant

## gpt

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 130 | 95% [90–98] | 4% [2–9] |
| C1 — code + stale documentation | 130 | 0% [0–3] | 100% [97–100] |
| C2 — code + fresh documentation | 130 | 100% [97–100] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 130 | 54% [45–62] | 46% [38–55] |
| Cw — code + stale documentation + generic staleness warning | 130 | 8% [5–15] | 91% [85–95] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +100 pp [+100, +100] ✓ significant (Holm ✓)
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +95 pp [+92, +98] ✓ significant (Holm ✓)
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +54 pp [+45, +62] ✓ significant (Holm ✓)
- `C2-C0` fresh vs no-docs (value of accurate prose): +5 pp [+2, +8] ✓ significant (Holm ✓)
- `C3-Cw` surf-report vs bare warning (is the value the *fix*, not just suspicion?): +45 pp [+35, +55] ✓ significant (Holm ✓)
- `Cw-C1` bare warning vs stale (does a generic warning alone help?): +8 pp [+4, +14] ✓ significant (Holm ✓)

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 320 [307–335] | 325 | 230 |
| C1 | 222 [210–235] | — | 222 |
| C2 | 226 [214–238] | 226 | — |
| C3 | 240 [227–254] | 265 | 212 |
| Cw | 234 [220–248] | 335 | 223 |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): -3 tok [-20, +14]
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -98 tok [-116, -79] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -18 tok [-36, +0]

## haiku

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 130 | 78% [71–85] | 2% [0–5] |
| C1 — code + stale documentation | 130 | 17% [11–24] | 82% [74–87] |
| C2 — code + fresh documentation | 130 | 96% [91–98] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 130 | 72% [63–79] | 26% [19–34] |
| Cw — code + stale documentation + generic staleness warning | 130 | 31% [23–39] | 69% [61–77] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +79 pp [+72, +86] ✓ significant (Holm ✓)
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +62 pp [+52, +71] ✓ significant (Holm ✓)
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +55 pp [+44, +65] ✓ significant (Holm ✓)
- `C2-C0` fresh vs no-docs (value of accurate prose): +18 pp [+10, +25] ✓ significant (Holm ✓)
- `C3-Cw` surf-report vs bare warning (is the value the *fix*, not just suspicion?): +41 pp [+29, +52] ✓ significant (Holm ✓)
- `Cw-C1` bare warning vs stale (does a generic warning alone help?): +14 pp [+4, +24] ✓ significant (Holm ✓)

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 763 [726–805] | 760 | 1106 |
| C1 | 601 [561–646] | 667 | 587 |
| C2 | 568 [532–606] | 567 | — |
| C3 | 777 [742–813] | 821 | 656 |
| Cw | 666 [607–731] | 945 | 542 |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +33 tok [-22, +90]
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -162 tok [-218, -103] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -175 tok [-230, -118] ✓ significant

## opus

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 130 | 91% [85–95] | 0% [0–3] |
| C1 — code + stale documentation | 130 | 32% [24–40] | 68% [59–75] |
| C2 — code + fresh documentation | 130 | 95% [90–98] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 130 | 98% [93–99] | 2% [1–7] |
| Cw — code + stale documentation + generic staleness warning | 130 | 78% [70–84] | 13% [8–20] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +64 pp [+55, +72] ✓ significant (Holm ✓)
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +59 pp [+50, +68] ✓ significant (Holm ✓)
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +66 pp [+58, +75] ✓ significant (Holm ✓)
- `C2-C0` fresh vs no-docs (value of accurate prose): +5 pp [-2, +11] (Holm ✗)
- `C3-Cw` surf-report vs bare warning (is the value the *fix*, not just suspicion?): +20 pp [+12, +28] ✓ significant (Holm ✓)
- `Cw-C1` bare warning vs stale (does a generic warning alone help?): +46 pp [+35, +57] ✓ significant (Holm ✓)

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 810 [771–850] | 817 | — |
| C1 | 610 [553–669] | 991 | 427 |
| C2 | 561 [513–614] | 551 | — |
| C3 | 783 [717–858] | 775 | 1146 |
| Cw | 851 [798–905] | 950 | 325 |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +48 tok [-29, +125]
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -200 tok [-269, -127] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -174 tok [-266, -81] ✓ significant

## sonnet

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 130 | 94% [88–97] | 0% [0–3] |
| C1 — code + stale documentation | 130 | 19% [13–27] | 81% [73–87] |
| C2 — code + fresh documentation | 130 | 100% [97–100] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 130 | 88% [82–93] | 12% [7–18] |
| Cw — code + stale documentation + generic staleness warning | 130 | 46% [38–55] | 52% [44–61] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +81 pp [+74, +87] ✓ significant (Holm ✓)
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +75 pp [+66, +82] ✓ significant (Holm ✓)
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +69 pp [+61, +78] ✓ significant (Holm ✓)
- `C2-C0` fresh vs no-docs (value of accurate prose): +6 pp [+2, +11] ✓ significant (Holm ✓)
- `C3-Cw` surf-report vs bare warning (is the value the *fix*, not just suspicion?): +42 pp [+32, +52] ✓ significant (Holm ✓)
- `Cw-C1` bare warning vs stale (does a generic warning alone help?): +27 pp [+16, +38] ✓ significant (Holm ✓)

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 607 [583–631] | 607 | — |
| C1 | 555 [525–586] | 626 | 538 |
| C2 | 508 [487–529] | 508 | — |
| C3 | 572 [540–607] | 567 | 611 |
| Cw | 580 [554–607] | 662 | 503 |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +47 tok [+11, +85] ✓ significant
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -52 tok [-90, -12] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -17 tok [-63, +28]

## Per-scenario success rate

### gemini

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| cascade-access-policy-code | 100% | 90% | 100% | 100% | 100% |
| cascade-backoff-offbyone-code | 100% | 0% | 100% | 90% | 0% |
| cascade-default-timeout-ts-code | 100% | 20% | 70% | 100% | 100% |
| cascade-money-rounding-code | 100% | 0% | 100% | 100% | 0% |
| cascade-page-size-ts-code | 0% | 0% | 70% | 30% | 10% |
| cascade-quota-batcher-code | 100% | 100% | 100% | 100% | 100% |
| cascade-ratelimit-burst-qa | 100% | 10% | 100% | 100% | 0% |
| cascade-retry-budget-code | 100% | 0% | 100% | 100% | 100% |
| cascade-serialize-key-order-ts-code | 100% | 0% | 100% | 100% | 100% |
| cascade-session-expiry-tz-qa | 100% | 0% | 100% | 0% | 0% |
| cascade-signal-threshold-code | 100% | 0% | 100% | 100% | 0% |
| cascade-ttl-units-code | 100% | 0% | 80% | 50% | 80% |
| cascade-validate-guard-ts-code | 50% | 0% | 100% | 30% | 0% |

### gpt

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| cascade-access-policy-code | 100% | 0% | 100% | 100% | 20% |
| cascade-backoff-offbyone-code | 50% | 0% | 100% | 10% | 0% |
| cascade-default-timeout-ts-code | 100% | 0% | 100% | 80% | 0% |
| cascade-money-rounding-code | 100% | 0% | 100% | 10% | 0% |
| cascade-page-size-ts-code | 90% | 0% | 100% | 100% | 0% |
| cascade-quota-batcher-code | 100% | 0% | 100% | 100% | 40% |
| cascade-ratelimit-burst-qa | 100% | 0% | 100% | 100% | 30% |
| cascade-retry-budget-code | 100% | 0% | 100% | 100% | 10% |
| cascade-serialize-key-order-ts-code | 100% | 0% | 100% | 0% | 0% |
| cascade-session-expiry-tz-qa | 100% | 0% | 100% | 0% | 0% |
| cascade-signal-threshold-code | 100% | 0% | 100% | 100% | 0% |
| cascade-ttl-units-code | 100% | 0% | 100% | 0% | 10% |
| cascade-validate-guard-ts-code | 100% | 0% | 100% | 0% | 0% |

### haiku

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| cascade-access-policy-code | 90% | 0% | 100% | 90% | 10% |
| cascade-backoff-offbyone-code | 100% | 0% | 100% | 90% | 0% |
| cascade-default-timeout-ts-code | 20% | 0% | 100% | 90% | 0% |
| cascade-money-rounding-code | 100% | 0% | 100% | 30% | 0% |
| cascade-page-size-ts-code | 10% | 0% | 100% | 100% | 0% |
| cascade-quota-batcher-code | 60% | 0% | 100% | 100% | 60% |
| cascade-ratelimit-burst-qa | 100% | 70% | 100% | 100% | 100% |
| cascade-retry-budget-code | 100% | 0% | 100% | 80% | 60% |
| cascade-serialize-key-order-ts-code | 100% | 0% | 100% | 30% | 0% |
| cascade-session-expiry-tz-qa | 100% | 0% | 100% | 50% | 20% |
| cascade-signal-threshold-code | 100% | 90% | 100% | 70% | 70% |
| cascade-ttl-units-code | 100% | 60% | 100% | 100% | 80% |
| cascade-validate-guard-ts-code | 40% | 0% | 50% | 0% | 0% |

### opus

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| cascade-access-policy-code | 100% | 20% | 100% | 100% | 100% |
| cascade-backoff-offbyone-code | 100% | 0% | 100% | 100% | 100% |
| cascade-default-timeout-ts-code | 50% | 10% | 40% | 100% | 100% |
| cascade-money-rounding-code | 100% | 90% | 100% | 100% | 100% |
| cascade-page-size-ts-code | 30% | 0% | 100% | 100% | 0% |
| cascade-quota-batcher-code | 100% | 0% | 100% | 100% | 100% |
| cascade-ratelimit-burst-qa | 100% | 100% | 100% | 100% | 100% |
| cascade-retry-budget-code | 100% | 90% | 100% | 100% | 100% |
| cascade-serialize-key-order-ts-code | 100% | 0% | 100% | 100% | 20% |
| cascade-session-expiry-tz-qa | 100% | 50% | 100% | 100% | 20% |
| cascade-signal-threshold-code | 100% | 50% | 100% | 100% | 100% |
| cascade-ttl-units-code | 100% | 0% | 100% | 70% | 100% |
| cascade-validate-guard-ts-code | 100% | 0% | 100% | 100% | 70% |

### sonnet

| Scenario | C0 | C1 | C2 | C3 | Cw |
|---|---|---|---|---|---|
| cascade-access-policy-code | 100% | 0% | 100% | 100% | 30% |
| cascade-backoff-offbyone-code | 100% | 0% | 100% | 100% | 10% |
| cascade-default-timeout-ts-code | 90% | 0% | 100% | 100% | 0% |
| cascade-money-rounding-code | 100% | 0% | 100% | 90% | 0% |
| cascade-page-size-ts-code | 30% | 0% | 100% | 100% | 0% |
| cascade-quota-batcher-code | 100% | 50% | 100% | 100% | 100% |
| cascade-ratelimit-burst-qa | 100% | 100% | 100% | 100% | 100% |
| cascade-retry-budget-code | 100% | 0% | 100% | 100% | 100% |
| cascade-serialize-key-order-ts-code | 100% | 0% | 100% | 100% | 0% |
| cascade-session-expiry-tz-qa | 100% | 0% | 100% | 100% | 60% |
| cascade-signal-threshold-code | 100% | 100% | 100% | 90% | 100% |
| cascade-ttl-units-code | 100% | 0% | 100% | 0% | 100% |
| cascade-validate-guard-ts-code | 100% | 0% | 100% | 70% | 0% |

