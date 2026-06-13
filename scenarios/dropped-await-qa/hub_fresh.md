---
summary: The durability guarantee of charge_customer and how it records charges in the ledger.
anchors:
  - claim: >
      charge_customer does NOT await the ledger write: it calls `self.ledger.commit(entry)` without
      `await`, so commit() merely returns a coroutine that is never scheduled — the ledger append
      never actually runs. The charge is therefore NOT persisted when the function returns;
      ledger.contains(receipt.id) is False. The write is dropped (fire-and-forget that never fires).
    at: code/billing/charges.py > ChargeService > charge_customer
    hash: ee09e978967d
refs: []
---

# Charging customers

`ChargeService.charge_customer` charges the payment gateway and then **fails to record the charge**:
it calls `self.ledger.commit(entry)` **without `await`**. Because `commit` is a coroutine function,
calling it without awaiting just builds a coroutine object and discards it — the append to the
ledger never executes (Python even emits a "coroutine was never awaited" warning).

The actual post-condition: when `await charge_customer(...)` returns, the charge is **not**
persisted — `ledger.contains(receipt.id)` is `False`. The ledger write has been silently dropped.
