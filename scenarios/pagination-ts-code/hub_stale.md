---
summary: How list endpoints paginate results and the default page size they use.
anchors:
  - claim: >
      defaultPageSize() returns 50. List endpoints page results into fixed pages of 50 items unless
      an explicit pageSize is passed, so a result set of N items spans ceil(N / 50) pages and
      offsets advance in steps of 50.
    at: code/pagination.ts > defaultPageSize
    hash: e0989902904f
refs: []
---

# Pagination

List endpoints return results in fixed-size pages. The default page size is **50 items**
(`defaultPageSize()` returns `50`): unless a caller passes an explicit `pageSize`, `paginate` slices
the data into pages of 50, and page offsets advance in steps of 50.

So a result set of `N` items spans **`ceil(N / 50)`** pages at the default size — e.g. 100 items
fit in **2** pages, and 101 items need **3**.
