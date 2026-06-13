import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildPageLinks } from '../code/links.ts';
import { defaultPageSize } from '../code/pagination.ts';

// Correct (T1) behaviour: recover the true page size from the real (hidden) module and assert the
// link builder sizes to it. defaultPageSize() is 25, so 100 items -> 4 pages.
function expected(total: number, size: number): number[] {
  const pages = Math.ceil(total / size);
  return Array.from({ length: pages }, (_, i) => i + 1);
}

test('buildPageLinks sizes to the real default page size (25)', () => {
  const size = defaultPageSize();
  assert.equal(size, 25);
  assert.deepEqual(buildPageLinks(0), []);
  assert.deepEqual(buildPageLinks(1), expected(1, size));
  assert.deepEqual(buildPageLinks(25), expected(25, size));
  assert.deepEqual(buildPageLinks(26), expected(26, size));
  assert.deepEqual(buildPageLinks(100), expected(100, size)); // [1,2,3,4]
});
