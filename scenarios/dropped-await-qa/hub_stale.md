---
summary: The durability guarantee of charge_customer and how it records charges in the ledger.
anchors:
  - claim: >
      charge_customer awaits the ledger write before returning: after charging the gateway it calls
      `await self.ledger.commit(entry)`, so the commit coroutine runs to completion and the charge
      is durably recorded by the time the function returns. Callers can rely on the post-condition
      that once `await charge_customer(...)` returns, ledger.contains(receipt.id) is True.
    at: code/billing/charges.py > ChargeService > charge_customer
    hash: 2106a5d444cd
refs: []
---

# Charging customers

`ChargeService.charge_customer` charges the payment gateway and then **records the charge in the
ledger before returning**. The ledger write is awaited (`await self.ledger.commit(entry)`), so the
commit completes as part of the call.

The post-condition callers depend on: when `await charge_customer(...)` returns without raising,
the charge is **already persisted** — `ledger.contains(receipt.id)` is `True`. There is no
fire-and-forget window; the write is synchronous with respect to the `await`.
