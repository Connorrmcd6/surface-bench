import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pageCount, defaultPageSize } from '../code/pagination.ts';

// Correct (T1) behaviour: the default page size is 25, so pageCount uses 25.
test('pageCount uses the current default page size of 25', () => {
  assert.equal(defaultPageSize(), 25);
  assert.equal(pageCount(0), 0);
  assert.equal(pageCount(1), 1);
  assert.equal(pageCount(25), 1);
  assert.equal(pageCount(26), 2);
  assert.equal(pageCount(100), 4);
  assert.equal(pageCount(101), 5);
});
