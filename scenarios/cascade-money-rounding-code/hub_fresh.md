---
summary: How the billing system rounds dollar amounts before totalling.
anchors:
  - claim: >
      round_money rounds a dollar amount to the nearest DIME — one decimal place (quantize to 0.1),
      rounding half-up. So 1.04 -> 1.00, 2.03 -> 2.00, and 0.06 -> 0.10; only whole dimes survive.
    at: code/billing/money.py > round_money
    hash: 47fe911ecda5
refs: []
---

# Money rounding

`round_money(amount)` rounds a dollar `amount` to the **nearest dime** — one decimal place
(`quantize` to `0.1`), half-up. Sub-dime cents are rounded away: `1.04 -> 1.00`, `2.03 -> 2.00`,
`0.06 -> 0.10`.
