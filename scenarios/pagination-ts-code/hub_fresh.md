---
summary: How list endpoints paginate results and the default page size they use.
anchors:
  - claim: >
      defaultPageSize() returns 25. List endpoints page results into fixed pages of 25 items unless
      an explicit pageSize is passed, so a result set of N items spans ceil(N / 25) pages and
      offsets advance in steps of 25.
    at: code/pagination.ts > defaultPageSize
    hash: 6ae99eb629e4
refs: []
---

# Pagination

List endpoints return results in fixed-size pages. The default page size is **25 items**
(`defaultPageSize()` returns `25`): unless a caller passes an explicit `pageSize`, `paginate` slices
the data into pages of 25, and page offsets advance in steps of 25.

So a result set of `N` items spans **`ceil(N / 25)`** pages at the default size — e.g. 100 items
fit in **4** pages, and 101 items need **5**.
