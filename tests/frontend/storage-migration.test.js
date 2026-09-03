import assert from 'node:assert/strict';
import test from 'node:test';

import { getMigrationTarget, migrateLegacyStorage } from '../../static/js/modules/storage-migration.js';

const makeStorage = (initial = {}) => {
  const values = new Map(Object.entries(initial));
  return {
    get length() {
      return values.size;
    },
    key: (index) => [...values.keys()][index] ?? null,
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
  };
};

test('maps legacy storage keys to their canonical namespace', () => {
  assert.equal(getMigrationTarget('cookgram:theme'), 'cookigram:theme');
  assert.equal(getMigrationTarget('cookgram:recipe:portions'), 'cookigram:recipe:portions');
  assert.equal(getMigrationTarget('cookgram:recipe:checked'), 'cookigram:recipe:main:checked');
  assert.equal(getMigrationTarget('cookgram:recipe:substeps:2'), 'cookigram:recipe:substeps:2');
  assert.equal(getMigrationTarget('cookgram:recipe:unknown'), null);
});

test('migrates values once and keeps existing canonical values', () => {
  const storage = makeStorage({
    'cookgram:theme': 'dark',
    'cookgram:recipe:portions': '6',
    'cookgram:recipe:checked': '["salt"]',
    'cookigram:recipe:portions': '4',
  });

  migrateLegacyStorage(storage);

  assert.equal(storage.getItem('cookigram:theme'), 'dark');
  assert.equal(storage.getItem('cookigram:recipe:portions'), '4');
  assert.equal(storage.getItem('cookigram:recipe:main:checked'), '["salt"]');
  assert.equal(storage.getItem('cookgram:theme'), null);
  assert.equal(storage.getItem('cookgram:recipe:portions'), '6');
  assert.equal(storage.getItem('cookgram:recipe:checked'), null);
});

test('converts legacy numeric cook steps to their stable step id', () => {
  const storage = makeStorage({ 'cookgram:recipe:step': '1' });
  const root = {
    querySelector: (selector) => {
      if (selector === '.cook[data-recipe="recipe"]') {
        return {
          querySelector: (stepSelector) =>
            stepSelector === '.cook-step[data-step="1"]'
              ? { dataset: { stepId: 'mix-sauce' } }
              : null,
        };
      }
      return null;
    },
  };

  migrateLegacyStorage(storage, root);

  assert.equal(storage.getItem('cookigram:recipe:step-id'), 'mix-sauce');
  assert.equal(storage.getItem('cookgram:recipe:step'), null);
});
