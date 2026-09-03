/**
 * Pure parsing, scaling, and formatting functions for cooking quantities,
 * and the interactive portion picker feature.
 */

/**
 * Parses a quantity value string like "800", "0,5", "1/2" or "1 1/2".
 *
 * @param {string | number} raw
 * @returns {number}
 */
export const parseQuantityValue = (raw) => {
  const parts = String(raw).trim().split(/\s+/);
  let total = 0;
  for (const part of parts) {
    if (!part) continue;
    const p = part.replace(',', '.');
    if (p.includes('/')) {
      const [n, d] = p.split('/');
      if (!/^\d+(\.\d+)?$/.test(n) || !/^\d+(\.\d+)?$/.test(d)) return Number.NaN;
      total += Number(n) / Number(d);
    } else if (/^\d+(\.\d+)?$/.test(p)) {
      total += Number(p);
    } else {
      return Number.NaN;
    }
  }
  return total;
};

// A leading quantity expression: "800", "0,5", "1/2" or "1 1/2".
export const QUANTITY_TOKEN = /(\d+(?:[.,]\d+)?(?:(?:\s+\d+)?\s*\/\s*\d+)?)/;

/**
 * Returns finite parsed numeric value or null.
 *
 * @param {string | number} raw
 * @returns {number | null}
 */
export const parseQuantity = (raw) => {
  const str = String(raw ?? '').trim();
  if (!str) return null;
  const value = parseQuantityValue(str);
  return Number.isFinite(value) ? value : null;
};


/**
 * Formats a scaled numeric quantity, preferring simple culinary fractions
 * for small numbers ("1 1/2", "3/4") and decimals for larger values ("37,5").
 *
 * @param {number} value
 * @returns {string}
 */
export const formatScaled = (value) => {
  const rounded = Math.round(value * 100) / 100;
  if (Number.isInteger(rounded)) return String(rounded);
  const whole = Math.floor(rounded);
  const frac = rounded - whole;
  if (whole < 10) {
    for (let d = 2; d <= 4; d += 1) {
      for (let n = 1; n < d; n += 1) {
        if (Math.abs(frac - n / d) < 0.01) {
          return whole > 0 ? `${whole} ${n}/${d}` : `${n}/${d}`;
        }
      }
    }
  }
  return String(rounded).replace('.', ',');
};

/**
 * Scales the leading quantity and any "sur <total>" occurrences of an ingredient
 * quantity string, leaving prep directives such as "en morceaux de 2 cm" untouched.
 *
 * @param {string} text
 * @param {number} factor
 * @returns {string}
 */
export const scaleIngredientText = (text, factor) => {
  let scaled = String(text).replace(QUANTITY_TOKEN, (token) =>
    formatScaled(parseQuantity(token) * factor)
  );
  scaled = scaled.replace(
    /,\s*(sur\s+)(\d+(?:[.,]\d+)?(?:(?:\s+\d+)?\s*\/\s*\d+)?)/gi,
    (_, keyword, token) => `, ${keyword}${formatScaled(parseQuantity(token) * factor)}`
  );
  return scaled;
};

export const scaleQuantity = (source, factor) => scaleIngredientText(source || '', factor);

export const scaleText = (source, factor) =>
  String(source || '').replace(
    /\(([^)]*)\)/g,
    (_, content) => `(${scaleIngredientText(content, factor)})`
  );

/**
 * Initializes the portion picker on recipe pages.
 */
export const initPortions = () => {
  const portionPicker = document.querySelector('.portion-picker');
  if (!portionPicker) return;

  const base = Number(portionPicker.dataset.basePortions);
  const min = Number(portionPicker.dataset.min);
  const max = Number(portionPicker.dataset.max);
  const step = Number(portionPicker.dataset.step) || 1;
  const storageKey = `cookigram:${portionPicker.dataset.recipe}:portions`;

  const getSavedPortions = () => {
    const raw = localStorage.getItem(storageKey);
    const parsed = Number(raw);
    if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
      return base;
    }
    return parsed;
  };

  let portions = getSavedPortions();

  const renderPortions = () => {
    const factor = portions / base;
    portionPicker.querySelector('output').textContent = portions;
    document.querySelectorAll('[data-scale-quantity]').forEach((node) => {
      node.textContent = scaleQuantity(node.dataset.scaleQuantity, factor);
    });
    document.querySelectorAll('[data-scale-text]').forEach((node) => {
      node.textContent = scaleText(node.dataset.scaleText, factor);
    });
    portionPicker.querySelector('[data-change="-1"]').disabled = portions <= min;
    portionPicker.querySelector('[data-change="1"]').disabled = portions >= max;
  };

  portionPicker.querySelectorAll('[data-change]').forEach((button) => {
    button.addEventListener('click', () => {
      const delta = Number(button.dataset.change) * step;
      const next = portions + delta;
      if (next < min || next > max) return;
      portions = next;
      localStorage.setItem(storageKey, String(portions));
      renderPortions();
    });
  });

  renderPortions();
};
