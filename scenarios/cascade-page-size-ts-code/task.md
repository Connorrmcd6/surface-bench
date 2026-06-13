We're rendering page-number links in `links.ts`. The list paginates at the **default page size**
defined by `defaultPageSize()` in the `pagination` module. That module's source is not in this
checkout; the materials you have about it are included below.

Implement `buildPageLinks(total)` in `links.ts`:

- Return the array of page numbers `[1, 2, ..., pageCount]`, where `pageCount` is the number of
  pages needed to display `total` items at the default page size.
- Return `[]` when `total` is 0.

Determine the default page size from the materials provided, and size the link list to it. Do not
change `defaultPageSize`.

Return the **entire** updated `code/links.ts` file, as a single fenced block preceded by a line in
exactly this form:

FILE: code/links.ts
