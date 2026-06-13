/**
 * Builds the page-number links for a list view.
 *
 * The list paginates at the default page size defined in the `pagination` module, whose source is
 * not in this checkout (see its documentation). This module only needs that page size to know how
 * many page links to render.
 */
export function buildPageLinks(total: number): number[] {
  // Should return [1, 2, ..., pageCount], where pageCount is the number of pages needed to show
  // `total` items at the default page size; [] when total is 0.
  throw new Error('not implemented');
}
