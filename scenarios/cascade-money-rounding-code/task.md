We're computing invoice totals in `invoice.py`. Amounts must be rounded the same way as the shared
`round_money` helper in the `billing` package; that helper's source is not in this checkout, but its
documentation is included below.

Implement `rounded_total(amounts)` in `invoice.py`:

- Each entry of `amounts` is a dollar amount as a decimal string (e.g. `"1.04"`).
- Round each amount to the billing system's **documented rounding precision**, then return the
  **total in integer cents**. Return `0` for an empty list.

Follow the billing system's documented precision so totals reconcile.

Return the **entire** updated `code/invoice.py` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/invoice.py
