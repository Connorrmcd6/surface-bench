We're adding request batching to `throttle.py`. The throttle drives a `FixedWindowLimiter` (from
the `limiter` package) configured with `WINDOW_LIMIT = 10`. The limiter's source is not in this
checkout; the materials you have about it are included below.

Implement `plan_batches(total)` in `throttle.py`:

- Split `total` queued requests into consecutive batches, each sized to the limiter's **per-window
  capacity** for `WINDOW_LIMIT` (the number of requests it will admit in a single window).
- Use full-capacity batches, followed by a single smaller remainder batch when `total` is not an
  exact multiple. The returned list of batch sizes must sum to `total`. Return `[]` for `total = 0`.

Determine the limiter's true per-window capacity for `WINDOW_LIMIT` and size the batches to it. Do
not change `WINDOW_LIMIT`.

Return the **entire** updated `code/throttle.py` file, as a single fenced block preceded by a line
in exactly this form:

FILE: code/throttle.py
