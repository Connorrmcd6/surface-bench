We're pre-computing the backoff schedule in `schedule.py`. The scheduler is paired with a
`RetryPolicy` (from the `retry` package) that decides how many times a transient operation is
attempted. The retry policy's source is not in this checkout; the materials you have about it are
included below.

Implement `backoff_schedule()` in `schedule.py`:

- Return the wait before each retry, in milliseconds — **one entry per retry the policy will make**
  for a persistently-failing transient operation.
- A retry happens between consecutive attempts, so the number of entries is **one fewer than the
  policy's maximum total attempts**.
- Delays grow exponentially: `BASE_DELAY_MS * 2 ** k` for the k-th retry, k starting at 0. Return
  `[]` if the policy makes only a single attempt.

Determine the policy's maximum total attempts from the materials provided, and size the schedule to
it. Do not change `BASE_DELAY_MS`.

Return the **entire** updated `code/schedule.py` file, as a single fenced block preceded by a line
in exactly this form:

FILE: code/schedule.py
