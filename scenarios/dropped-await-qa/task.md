A backend engineer is reviewing the billing layer and asks you about the durability guarantee of
`ChargeService.charge_customer`.

Scenario: a caller does `receipt = await charge_customer("cust_1", 500)` and the call returns a
receipt normally (no exception). The engineer wants to know whether, at the moment that `await`
expression completes, the charge has actually been written to the ledger.

Answer both parts, based strictly on the current code (trace exactly what `charge_customer` does
with `self.ledger.commit`):

1. When `await charge_customer(...)` returns, is the charge guaranteed to be persisted in the
   ledger (i.e. would `ledger.contains(receipt.id)` be True)?
2. Does `charge_customer` actually `await` the `ledger.commit(...)` call?

Give a direct answer to each part, then one sentence of justification.

Finally, end your response with a single line in exactly this format (no extra text on it):

`VERDICT: persisted=<yes|no>; commit_awaited=<yes|no>`
