# Robustness reanalysis — results/confirmatory-20260616T172420Z

Rows: 3250 · scenarios: 13 · cluster bootstrap: 10000 resamples, seed 20260616.

## 1. Scenario-clustered bootstrap (resampling scenarios, not completions)

Success-delta point estimate with 95% scenario-clustered CI (pp).

**H1 C2-C1**
- haiku: +79.2 [+60.8, +95.4] excludes 0
- sonnet: +80.8 [+57.7, +100.0] excludes 0
- opus: +63.8 [+42.3, +84.6] excludes 0
- gpt: +100.0 [+100.0, +100.0] excludes 0
- gemini: +76.9 [+56.9, +93.8] excludes 0

**H3 C3-C1**
- haiku: +54.6 [+33.8, +74.6] excludes 0
- sonnet: +69.2 [+45.4, +90.0] excludes 0
- opus: +66.2 [+45.4, +84.6] excludes 0
- gpt: +53.8 [+26.9, +77.7] excludes 0
- gemini: +60.0 [+37.7, +80.8] excludes 0

**H6 C3-Cw**
- haiku: +40.8 [+22.3, +60.8] excludes 0
- sonnet: +42.3 [+8.5, +72.3] excludes 0
- opus: +20.0 [+1.5, +42.3] excludes 0
- gpt: +45.4 [+22.3, +67.7] excludes 0
- gemini: +31.5 [+7.7, +57.7] excludes 0

**C2-C0 (marginal)**
- haiku: +17.7 [+3.1, +36.9] excludes 0
- sonnet: +6.2 [+0.0, +17.7] **CROSSES 0**
- opus: +4.6 [-2.3, +16.2] **CROSSES 0**
- gpt: +4.6 [+0.0, +12.3] **CROSSES 0**
- gemini: +5.4 [-6.9, +20.8] **CROSSES 0**

## 2. Verification suppression: fresh doc (C0-C2) vs stale (C0-C1)

| model | C0 | C1 | C2 | C3 | Cw | C0-C1 (H4) | C0-C2 |
|---|---|---|---|---|---|---|---|
| haiku | 100 | 23 | 25 | 58 | 33 | +77 | +75 |
| sonnet | 100 | 20 | 18 | 18 | 44 | +80 | +82 |
| opus | 100 | 33 | 38 | 29 | 87 | +67 | +62 |
| gpt | 96 | 0 | 2 | 23 | 9 | +96 | +94 |
| gemini | 100 | 85 | 74 | 100 | 100 | +15 | +26 |

## 3. Leave-them-out: drop 9 oracle-flagged cells

- gemini/cascade-default-timeout-ts-code: C2=70%
- gemini/cascade-page-size-ts-code: C2=70%
- gemini/cascade-quota-batcher-code: C1 never misleads
- gemini/cascade-ttl-units-code: C2=80%
- haiku/cascade-validate-guard-ts-code: C2=50%
- opus/cascade-default-timeout-ts-code: C2=40%
- opus/cascade-ratelimit-burst-qa: C1 never misleads
- sonnet/cascade-ratelimit-burst-qa: C1 never misleads
- sonnet/cascade-signal-threshold-code: C1 never misleads

**H1 C2-C1** (full → flagged-excluded)
- haiku: +79.2 → +81.7 (n_scen 12)
- sonnet: +80.8 → +95.5 (n_scen 11)
- opus: +63.8 → +72.7 (n_scen 11)
- gpt: +100.0 → +100.0 (n_scen 13)
- gemini: +76.9 → +88.9 (n_scen 9)

**H3 C3-C1** (full → flagged-excluded)
- haiku: +54.6 → +59.2 (n_scen 12)
- sonnet: +69.2 → +82.7 (n_scen 11)
- opus: +66.2 → +70.0 (n_scen 11)
- gpt: +53.8 → +53.8 (n_scen 13)
- gemini: +60.0 → +68.9 (n_scen 9)

**H6 C3-Cw** (full → flagged-excluded)
- haiku: +40.8 → +44.2 (n_scen 12)
- sonnet: +42.3 → +50.9 (n_scen 11)
- opus: +20.0 → +23.6 (n_scen 11)
- gpt: +45.4 → +45.4 (n_scen 13)
- gemini: +31.5 → +46.7 (n_scen 9)

## 4. Output-token ceiling hits & answer mode (per cell)

| model | cond | turn≥1024 % | text_answer % | forced % |
|---|---|---|---|---|
| haiku | C0 | 2.3 | 11.5 | 0.0 |
| haiku | C1 | 1.5 | 10.0 | 0.0 |
| haiku | C2 | 0.0 | 13.8 | 0.0 |
| haiku | C3 | 0.0 | 13.1 | 0.0 |
| haiku | Cw | 5.4 | 13.1 | 0.0 |
| sonnet | C0 | 0.0 | 99.2 | 0.0 |
| sonnet | C1 | 0.8 | 95.4 | 0.0 |
| sonnet | C2 | 0.0 | 96.2 | 0.0 |
| sonnet | C3 | 0.0 | 93.1 | 0.0 |
| sonnet | Cw | 0.0 | 99.2 | 0.0 |
| opus | C0 | 0.0 | 1.5 | 0.0 |
| opus | C1 | 1.5 | 5.4 | 0.0 |
| opus | C2 | 1.5 | 11.5 | 0.0 |
| opus | C3 | 6.9 | 4.6 | 0.0 |
| opus | Cw | 1.5 | 6.9 | 0.0 |
| gpt | C0 | 0.0 | 3.1 | 0.0 |
| gpt | C1 | 0.0 | 6.2 | 0.0 |
| gpt | C2 | 0.0 | 7.7 | 0.0 |
| gpt | C3 | 0.0 | 7.7 | 0.0 |
| gpt | Cw | 0.0 | 7.7 | 0.0 |
| gemini | C0 | 0.8 | 13.1 | 1.5 |
| gemini | C1 | 0.0 | 20.0 | 0.0 |
| gemini | C2 | 0.0 | 21.5 | 0.0 |
| gemini | C3 | 0.0 | 16.9 | 0.0 |
| gemini | Cw | 0.8 | 16.2 | 0.0 |
