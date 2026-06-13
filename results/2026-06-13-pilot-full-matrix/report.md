# Surface agent-impact benchmark

## Spend

**Total: $13.98** (estimated from token usage).

| Model | Spend |
|---|---|
| haiku | $1.49 |
| opus | $8.28 |
| sonnet | $4.21 |

## The gradient — Surface effect (C2−C1 success) by complexity tier

### haiku

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T0 — local (contradiction visible) | +0 pp [+0, +0] | +0 pp [+0, +0] |
| T1 — buried (truth needs tracing) | +71 pp [+60, +81] ✓ | +1 pp [-14, +17] |
| T2 — premise (invariant is load-bearing) | +0 pp [+0, +0] | +0 pp [+0, +0] |

### opus

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T0 — local (contradiction visible) | +0 pp [+0, +0] | +0 pp [+0, +0] |
| T1 — buried (truth needs tracing) | +61 pp [+49, +73] ✓ | +6 pp [-11, +21] |
| T2 — premise (invariant is load-bearing) | +0 pp [+0, +0] | +0 pp [+0, +0] |

### sonnet

| Tier | C2−C1 (fresh−stale) | C0−C1 (none−stale) |
|---|---|---|
| T0 — local (contradiction visible) | +3 pp [+0, +10] | -13 pp [-30, +0] |
| T1 — buried (truth needs tracing) | +57 pp [+46, +69] ✓ | +0 pp [-17, +17] |
| T2 — premise (invariant is load-bearing) | +0 pp [+0, +0] | +0 pp [+0, +0] |

## haiku

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 110 | 55% [46–64] | 22% [15–30] |
| C1 — code + stale documentation | 110 | 55% [45–64] | 43% [34–52] |
| C2 — code + fresh documentation | 110 | 100% [97–100] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 110 | 94% [87–97] | 0% [0–3] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +45 pp [+36, +55] ✓ significant
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +1 pp [-12, +14]
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +39 pp [+29, +49] ✓ significant
- `C2-C0` fresh vs no-docs (value of accurate prose): +45 pp [+35, +54] ✓ significant

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 442 [411–474] | 404 | 563 |
| C1 | 464 [430–500] | 430 | 471 |
| C2 | 430 [397–463] | 430 | — |
| C3 | 523 [486–563] | 501 | — |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +34 tok [-13, +82]
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): +22 tok [-24, +69]
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -59 tok [-111, -8] ✓ significant

## opus

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 110 | 64% [54–72] | 6% [3–13] |
| C1 — code + stale documentation | 110 | 60% [51–69] | 36% [28–46] |
| C2 — code + fresh documentation | 110 | 99% [95–100] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 110 | 97% [92–99] | 0% [0–3] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +39 pp [+30, +49] ✓ significant
- `C0-C1` no-docs vs stale (rotted worse than nothing?): +4 pp [-9, +16]
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +37 pp [+27, +47] ✓ significant
- `C2-C0` fresh vs no-docs (value of accurate prose): +35 pp [+26, +45] ✓ significant

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 517 [461–572] | 403 | 955 |
| C1 | 445 [402–490] | 439 | 398 |
| C2 | 417 [377–458] | 411 | — |
| C3 | 526 [479–573] | 512 | — |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +28 tok [-32, +89]
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -72 tok [-141, -0] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -80 tok [-144, -16] ✓ significant

## sonnet

| Condition | n | Success | Misled |
|---|---|---|---|
| C0 — code only (no documentation) | 110 | 59% [50–68] | 23% [16–31] |
| C1 — code + stale documentation | 110 | 63% [53–71] | 36% [28–46] |
| C2 — code + fresh documentation | 110 | 100% [97–100] | 0% [0–3] |
| C3 — code + stale documentation + surf divergence report | 110 | 100% [97–100] | 0% [0–3] |

**Deltas (success rate, 95% bootstrap CI):**

- `C2-C1` fresh vs stale (the Surface value): +37 pp [+28, +46] ✓ significant
- `C0-C1` no-docs vs stale (rotted worse than nothing?): -4 pp [-16, +9]
- `C3-C1` surf-report vs stale (does surfacing drift recover it?): +37 pp [+28, +46] ✓ significant
- `C2-C0` fresh vs no-docs (value of accurate prose): +41 pp [+32, +50] ✓ significant

**Output tokens (mean, 95% bootstrap CI) — generation cost:**

| Condition | mean out | when correct | when misled |
|---|---|---|---|
| C0 | 505 [469–541] | 439 | 668 |
| C1 | 405 [370–442] | 481 | 274 |
| C2 | 336 [307–369] | 336 | — |
| C3 | 450 [424–476] | 450 | — |

**Output-token deltas (95% bootstrap CI):**

- `C1-C2` stale − fresh (extra generation to cope with a stale doc): +68 tok [+22, +117] ✓ significant
- `C1-C0` stale − no-docs (does a wrong doc cost more than none?): -100 tok [-150, -48] ✓ significant
- `C1-C3` stale − stale+report (does the surf report cut the cost?): -45 tok [-89, +1]

