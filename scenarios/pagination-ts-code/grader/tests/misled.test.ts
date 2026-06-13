import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pageCount } from '../code/pagination.ts';

// Misled (T0) behaviour: an agent that trusts the stale doc hardcodes a page size of 50,
// so 100 items collapse to 2 pages and 101 to 3.
test('pageCount uses the stale default page size of 50', () => {
  assert.equal(pageCount(100), 2);
  assert.equal(pageCount(101), 3);
});
