import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildPageLinks } from '../code/links.ts';

// Misled (T0) behaviour: an agent that trusts the stale doc hardcodes a page size of 50,
// so 100 items collapse to 2 page links instead of 4.
test('buildPageLinks used the stale default page size (50)', () => {
  assert.deepEqual(buildPageLinks(100), [1, 2]);
});
