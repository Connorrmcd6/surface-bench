---
summary: The default page size that list views paginate at.
anchors:
  - claim: >
      defaultPageSize() returns 50. List views paginate in fixed pages of 50 items unless an
      explicit size is passed, so a result set of N items spans ceil(N / 50) pages and page links
      run from 1 to ceil(N / 50).
    at: code/pagination.ts > defaultPageSize
    hash: e0989902904f
refs: []
---

# Pagination

List views render results in fixed-size pages. The default page size is **50 items**
(`defaultPageSize()` returns `50`): unless a caller passes an explicit size, pagination slices the
data into pages of 50.

So a result set of `N` items spans **`ceil(N / 50)`** pages at the default size, and the page links
run from 1 to `ceil(N / 50)` — e.g. 100 items produce **2** page links.
