The `limiter` package exposes a per-key `FixedWindowLimiter`. We want a companion method that
tells a caller how much budget a key has left *before* they attempt a request, so the UI can show
"N requests remaining" without consuming any.

Implement a new method on `FixedWindowLimiter`:

```python
def remaining(self, key: str) -> int:
    ...
```

`remaining(key)` must return the number of further calls to `allow(key)` that would be admitted
(return `True`) right now, in the key's current window, **without** recording an attempt itself —
i.e. it must be a read-only query that is exactly consistent with how `allow` actually admits
requests. For a key that has never been seen it should return the full per-window budget; for a
key whose window is exhausted it should return 0.

Base your implementation strictly on the current behaviour of `allow` in the code. Do not change
`allow`.

Return the **entire** updated `code/limiter/window.py` file, as a single fenced block preceded by
a line in exactly this form:

FILE: code/limiter/window.py
