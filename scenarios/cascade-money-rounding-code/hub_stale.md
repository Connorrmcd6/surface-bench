---
summary: How the billing system rounds dollar amounts before totalling.
anchors:
  - claim: >
      round_money rounds a dollar amount to the nearest CENT — two decimal places (quantize to
      0.01), rounding half-up. So 1.04 stays 1.04 and 2.03 stays 2.03; the cents are preserved.
    at: code/billing/money.py > round_money
    hash: 61b4492f5740
refs: []
---

# Money rounding

`round_money(amount)` rounds a dollar `amount` to the **nearest cent** — two decimal places
(`quantize` to `0.01`), half-up. Amounts keep their exact cents: `1.04 -> 1.04`, `2.03 -> 2.03`,
`0.06 -> 0.06`.
