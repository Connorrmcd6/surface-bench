The `retry` package has a `RetryPolicy` whose `should_retry` decides, after a failed attempt,
whether the caller should try again. We want to surface the policy's ceiling so a caller can
pre-size a progress bar / budget without driving the retry loop.

Implement a new method on `RetryPolicy`:

```python
def max_total_attempts(self) -> int:
    ...
```

It must return the **maximum number of times a transient (retryable) operation will be attempted
in total** — the initial attempt plus every retry — for an operation that keeps failing with a
`TransientError`. The value must be exactly consistent with what `should_retry` actually does in
the current code (trace it: `should_retry(attempt_number, err)` is called with the 1-based count
of attempts already completed, and a retry happens whenever it returns `True`).

Base the number strictly on the current `should_retry` implementation. Do not change `should_retry`.

Return the **entire** updated `code/retry/policy.py` file, as a single fenced block preceded by a
line in exactly this form:

FILE: code/retry/policy.py
