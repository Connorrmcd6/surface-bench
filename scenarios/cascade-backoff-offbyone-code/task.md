We're pre-computing a retry backoff schedule in `poller.py`. The delays must match the backoff
policy in the `retry` package; that helper's source is not in this checkout, but its documentation
is included below.

Implement `delays(attempts)` in `poller.py`:

- `attempts` is a list of retry attempt numbers (e.g. `[1, 2, 3]`).
- For each attempt number, return its backoff delay in **milliseconds**. Backoff is exponential,
  starting from a base of 100 ms and doubling each attempt.
- Apply the retry package's **documented attempt-indexing convention** so your delays match its
  `delay_for`. Return `[]` for an empty list.

Return the **entire** updated `code/poller.py` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/poller.py
