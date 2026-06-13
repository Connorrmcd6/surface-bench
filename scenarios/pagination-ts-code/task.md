The `pagination.ts` module paginates list results. We need a helper that reports how many pages a
result set will span at the **default** page size, so the UI can render the right number of page
links up front.

Add and export a new function in `code/pagination.ts`:

```ts
export function pageCount(total: number): number {
  ...
}
```

`pageCount(total)` must return the number of fixed-size pages needed to display `total` items
**using the default page size** (the same default `paginate` applies when no `pageSize` is given).
`pageCount(0)` must return `0`.

Base the page size strictly on the current code, not on any prose description. Do not change
`defaultPageSize` or `paginate`.

Return the **entire** updated `code/pagination.ts` file, as a single fenced block preceded by a
line in exactly this form:

FILE: code/pagination.ts
