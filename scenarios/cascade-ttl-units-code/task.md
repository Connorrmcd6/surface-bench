We're adding cache warming to `warmer.py`. The warmer keeps a cache hot by re-fetching entries
before they expire. Entry lifetime is governed by the `TtlPolicy` in the `cache` package; that
policy's source is not in this checkout, but its documentation is included below.

Implement `schedule_refreshes(window_seconds)` in `warmer.py`:

- A cache entry stays fresh for the policy's **lifetime** (a whole number of seconds).
- Return how many refreshes are needed to keep the cache warm across a window of `window_seconds`:
  one refresh per lifetime, rounding **up** so the whole window is covered. Return `0` when
  `window_seconds` is `0`.

Determine the policy's lifetime in seconds and size the schedule to it.

Return the **entire** updated `code/warmer.py` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/warmer.py
