---
summary: The default page size that list views paginate at.
anchors:
  - claim: >
      defaultPageSize() returns 25. List views paginate in fixed pages of 25 items unless an
      explicit size is passed, so a result set of N items spans ceil(N / 25) pages and page links
      run from 1 to ceil(N / 25).
    at: code/pagination.ts > defaultPageSize
    hash: 6ae99eb629e4
refs: []
---

# Pagination

List views render results in fixed-size pages. The default page size is **25 items**
(`defaultPageSize()` returns `25`): unless a caller passes an explicit size, pagination slices the
data into pages of 25.

So a result set of `N` items spans **`ceil(N / 25)`** pages at the default size, and the page links
run from 1 to `ceil(N / 25)` — e.g. 100 items produce **4** page links.
