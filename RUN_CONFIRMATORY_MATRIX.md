# Confirmatory run — 5-model multi-turn matrix (one model at a time)

Keep the Mac **plugged in** with the **lid open**. Run each block in the `surface-bench` directory.
Run the five models **one at a time**: wait for `wrote results/run-<model>/raw.jsonl` before starting
the next. Each model writes its own dir, so if one fails you only re-run that model.

## 0. Pre-flight: confirm the pre-registration is frozen (DO THIS BEFORE ANY MODEL RUN)

The pre-registration has already been **frozen and tagged** as `prereg-v2-multi` (`surf 0.6.2`), and
pushed. Just confirm the tag is present before running:

```sh
git tag --list prereg-v2-multi      # must print: prereg-v2-multi
```

**Do not start a model run unless that tag exists** — the freeze must predate all confirmatory data.

## 1. Load API keys

```sh
set -a; source ~/.surface-bench.env; set +a
```

## 2. Run each model (one at a time)

The scenario set is the cascade family; `idempotency-window-qa` auto-excludes in multi mode
(650 cells/model). Run **one** block, watch it finish, then run the next.

**haiku**
```sh
nohup caffeinate -i -s uv run python -m surface_bench.run --models haiku --mode multi --max-turns 8 --trials 10 --scenarios $(ls -d scenarios/cascade-* | xargs -n1 basename) --out results/run-haiku > run-haiku.log 2>&1 &
```
**sonnet**
```sh
nohup caffeinate -i -s uv run python -m surface_bench.run --models sonnet --mode multi --max-turns 8 --trials 10 --scenarios $(ls -d scenarios/cascade-* | xargs -n1 basename) --out results/run-sonnet > run-sonnet.log 2>&1 &
```
**opus**
```sh
nohup caffeinate -i -s uv run python -m surface_bench.run --models opus --mode multi --max-turns 8 --trials 10 --scenarios $(ls -d scenarios/cascade-* | xargs -n1 basename) --out results/run-opus > run-opus.log 2>&1 &
```
**gpt** (OpenAI — watch credit; ≈ $9)
```sh
nohup caffeinate -i -s uv run python -m surface_bench.run --models gpt --mode multi --max-turns 8 --trials 10 --scenarios $(ls -d scenarios/cascade-* | xargs -n1 basename) --out results/run-gpt > run-gpt.log 2>&1 &
```
**gemini** (Google — watch credit; ≈ $13, slowest/most rate-limited)
```sh
nohup caffeinate -i -s uv run python -m surface_bench.run --models gemini --mode multi --max-turns 8 --trials 10 --scenarios $(ls -d scenarios/cascade-* | xargs -n1 basename) --out results/run-gemini > run-gemini.log 2>&1 &
```

## 3. Confirm it's running / watch

```sh
jobs                      # should show the job running (not "done")
tail -f run-<model>.log   # Ctrl+C stops the tail only; the run keeps going
```

The first log line should say it is *excluding* `cascade-idempotency-window-qa`. The run is done when
the log ends with `wrote results/run-<model>/raw.jsonl`.

## 4. Sanity-check each model before moving on

```sh
wc -l < results/run-<model>/raw.jsonl              # expect 650
grep -c '"error"' results/run-<model>/raw.jsonl    # expect 0
```

If a model died partway, just re-run its block (it overwrites only its own dir).

## 5. After all five finish: merge + report + oracle

```sh
TS=$(date -u +%Y%m%dT%H%M%SZ); D=results/confirmatory-$TS; mkdir -p "$D"
cat results/run-*/raw.jsonl > "$D/raw.jsonl"
uv run python - "$D" <<'PY'
import json, glob, sys
dirs = sorted(glob.glob("results/run-*/run.json"))
base = json.load(open(dirs[0])); base["models"] = {}
for f in dirs:
    base["models"].update(json.load(open(f))["models"])
json.dump(base, open(sys.argv[1] + "/run.json", "w"), indent=2)
print("merged", len(base["models"]), "models into", sys.argv[1])
PY
uv run python -m surface_bench.report "$D"
uv run python -m surface_bench.oracle "$D"
echo "merged matrix in $D"
```

Expect 3250 rows total (5 × 650). The oracle must exit clean on the real models.

## Stop a run (if needed)

```sh
pkill -f surface_bench.run
```
