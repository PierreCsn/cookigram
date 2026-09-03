/**
 * One-shot migration from the former `cookgram:*` localStorage namespace.
 *
 * Migration is deliberately kept at the application boundary so feature
 * modules only need to know the canonical `cookigram:*` keys afterwards.
 */

const LEGACY_PREFIX = 'cookgram:';
const CURRENT_PREFIX = 'cookigram:';

export const getStepId = (recipeSlug, stepIndex, root) => {
  const cook = root?.querySelector?.(`.cook[data-recipe="${recipeSlug}"]`);
  const step = cook?.querySelector?.(`.cook-step[data-step="${stepIndex}"]`);
  return step?.dataset.stepId || String(stepIndex);
};

export const getMigrationTarget = (legacyKey, root = globalThis.document) => {
  if (legacyKey === 'cookgram:theme' || legacyKey === 'cookgram:autospeak') {
    return `${CURRENT_PREFIX}${legacyKey.slice(LEGACY_PREFIX.length)}`;
  }

  const substepsMatch = legacyKey.match(/^cookgram:([^:]+):substeps:(\d+)$/);
  if (substepsMatch) {
    const [, recipeSlug, stepIndex] = substepsMatch;
    return `${CURRENT_PREFIX}${recipeSlug}:substeps:${getStepId(recipeSlug, stepIndex, root)}`;
  }

  const match = legacyKey.match(/^cookgram:([^:]+):(portions|shopping-eval|checked|step)$/);
  if (!match) return null;

  const [, recipeSlug, feature] = match;
  if (feature === 'checked') return `${CURRENT_PREFIX}${recipeSlug}:main:checked`;
  if (feature === 'step') {
    return `${CURRENT_PREFIX}${recipeSlug}:step-id`;
  }
  return `${CURRENT_PREFIX}${recipeSlug}:${feature}`;
};

/**
 * Copies legacy values to canonical keys and removes the legacy entries.
 * Existing canonical values always win.
 *
 * @param {Storage} storage
 * @param {Document} root
 */
export const migrateLegacyStorage = (storage = globalThis.localStorage, root = globalThis.document) => {
  if (!storage) return;

  const keys = [];
  for (let index = 0; index < storage.length; index += 1) {
    const key = storage.key(index);
    if (key?.startsWith(LEGACY_PREFIX)) keys.push(key);
  }

  keys.forEach((legacyKey) => {
    const targetKey = getMigrationTarget(legacyKey, root);
    if (!targetKey || storage.getItem(targetKey) !== null) return;
    let value = storage.getItem(legacyKey);
    if (value === null) return;
    try {
      if (legacyKey.endsWith(':step')) {
        const recipeSlug = legacyKey.slice(LEGACY_PREFIX.length, -':step'.length);
        value = getStepId(recipeSlug, value, root);
      }
      storage.setItem(targetKey, value);
      storage.removeItem(legacyKey);
    } catch (_) {
      // A full or restricted storage must not prevent the application boot.
    }
  });
};
