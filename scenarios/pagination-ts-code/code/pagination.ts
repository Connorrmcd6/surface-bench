/** The default number of items per page for list endpoints. */
export function defaultPageSize(): number {
  return 25;
}

export interface Page<T> {
  items: T[];
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/**
 * Slice `items` into the `page`-th (0-based) fixed-size page.
 * `pageSize` defaults to `defaultPageSize()`.
 */
export function paginate<T>(
  items: T[],
  page: number,
  pageSize: number = defaultPageSize(),
): Page<T> {
  const start = page * pageSize;
  const slice = items.slice(start, start + pageSize);
  return {
    items: slice,
    page,
    pageSize,
    hasMore: start + pageSize < items.length,
  };
}
