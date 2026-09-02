import assert from 'node:assert/strict';
import test, { describe, beforeEach } from 'node:test';

import { getSavedRecipes } from '../../static/js/modules/offline-save.js';

describe('Offline Save Unit Tests', () => {
  const SAVE_KEY = 'cookigram:saved-recipes';

  beforeEach(() => {
    let store = {};
    globalThis.localStorage = {
      getItem: (key) => (key in store ? store[key] : null),
      setItem: (key, value) => {
        store[key] = String(value);
      },
      removeItem: (key) => {
        delete store[key];
      },
      clear: () => {
        store = {};
      },
    };
  });

  test('getSavedRecipes returns an empty set when nothing is stored', () => {
    const saved = getSavedRecipes();
    assert.ok(saved instanceof Set);
    assert.strictEqual(saved.size, 0);
  });

  test('getSavedRecipes parses stored slugs into a set', () => {
    localStorage.setItem(SAVE_KEY, JSON.stringify(['a-b', 'c-d']));
    const saved = getSavedRecipes();
    assert.ok(saved.has('a-b'));
    assert.ok(saved.has('c-d'));
    assert.strictEqual(saved.size, 2);
  });

  test('getSavedRecipes tolerates corrupted JSON', () => {
    localStorage.setItem(SAVE_KEY, '{nope');
    const saved = getSavedRecipes();
    assert.ok(saved instanceof Set);
    assert.strictEqual(saved.size, 0);
  });

  test('getSavedRecipes tolerates non-array JSON', () => {
    localStorage.setItem(SAVE_KEY, JSON.stringify('not-an-array'));
    const saved = getSavedRecipes();
    assert.ok(saved instanceof Set);
    assert.strictEqual(saved.size, 0);
  });
});
