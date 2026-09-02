import assert from 'node:assert/strict';
import test, { describe } from 'node:test';

import {
  formatScaled,
  parseQuantity,
  parseQuantityValue,
  scaleIngredientText,
  scaleQuantity,
  scaleText,
} from '../../static/js/modules/portions.js';

describe('Portions & Quantity Scaling Unit Tests', () => {
  describe('parseQuantityValue & parseQuantity', () => {
    test('parseQuantityValue evaluates string tokens correctly', () => {
      assert.strictEqual(parseQuantityValue('800'), 800);
      assert.strictEqual(parseQuantityValue('1 1/2'), 1.5);
      assert.ok(Number.isNaN(parseQuantityValue('invalid_xyz')));
    });

    test('parses plain integers and floats', () => {

      assert.strictEqual(parseQuantity('100'), 100);
      assert.strictEqual(parseQuantity('2.5'), 2.5);
      assert.strictEqual(parseQuantity('0,5'), 0.5);
      assert.strictEqual(parseQuantity('12,75'), 12.75);
    });

    test('parses simple culinary fractions', () => {
      assert.strictEqual(parseQuantity('1/2'), 0.5);
      assert.strictEqual(parseQuantity('1/4'), 0.25);
      assert.strictEqual(parseQuantity('3/4'), 0.75);
      assert.strictEqual(parseQuantity('1/3'), 1 / 3);
    });

    test('parses mixed numbers with whole and fraction', () => {
      assert.strictEqual(parseQuantity('1 1/2'), 1.5);
      assert.strictEqual(parseQuantity('2 1/4'), 2.25);
      assert.strictEqual(parseQuantity('3 3/4'), 3.75);
    });

    test('returns null / NaN for invalid quantity tokens', () => {
      assert.strictEqual(parseQuantity(''), null);
      assert.strictEqual(parseQuantity('abc'), null);
      assert.strictEqual(parseQuantity('1/0'), null);

    });
  });

  describe('formatScaled', () => {
    test('formats integers cleanly without decimals', () => {
      assert.strictEqual(formatScaled(1), '1');
      assert.strictEqual(formatScaled(4), '4');
      assert.strictEqual(formatScaled(100), '100');
    });

    test('formats small quantities into culinary fractions when close to 1/2, 1/3, 1/4, 2/3, 3/4', () => {
      assert.strictEqual(formatScaled(0.5), '1/2');
      assert.strictEqual(formatScaled(0.25), '1/4');
      assert.strictEqual(formatScaled(0.75), '3/4');
      assert.strictEqual(formatScaled(1.5), '1 1/2');
      assert.strictEqual(formatScaled(2.25), '2 1/4');
      assert.strictEqual(formatScaled(3.75), '3 3/4');
    });

    test('formats numbers >= 10 with French comma notation instead of fractions', () => {
      assert.strictEqual(formatScaled(12.5), '12,5');
      assert.strictEqual(formatScaled(37.5), '37,5');
      assert.strictEqual(formatScaled(150.25), '150,25');
    });
  });

  describe('scaleIngredientText', () => {
    test('scales single leading quantity', () => {
      assert.strictEqual(scaleIngredientText('100 g', 2), '200 g');
      assert.strictEqual(scaleIngredientText('1/2 c. à café', 2), '1 c. à café');
      assert.strictEqual(scaleIngredientText('1 c. à soupe', 1.5), '1 1/2 c. à soupe');
    });

    test('scales quantity while preserving preparation notes', () => {
      assert.strictEqual(
        scaleIngredientText('200 g, coupés en dés de 2 cm', 1.5),
        '300 g, coupés en dés de 2 cm'
      );
      assert.strictEqual(
        scaleIngredientText('2 pièces, épluchées et tranchées', 2),
        '4 pièces, épluchées et tranchées'
      );
    });

    test('scales "sur <total>" secondary quantities', () => {
      assert.strictEqual(
        scaleIngredientText('1/2 pièce, sur 2 pièces au total', 2),
        '1 pièce, sur 4 pièces au total'
      );
    });
  });

  describe('scaleQuantity & scaleText', () => {
    test('scaleQuantity handles empty or missing input gracefully', () => {
      assert.strictEqual(scaleQuantity('', 2), '');
      assert.strictEqual(scaleQuantity(null, 2), '');
    });

    test('scaleText scales quantities enclosed in parentheses within instructions', () => {
      const stepText = "Ajouter l'huile d'olive (15 ml) et les carottes (200 g).";
      const scaled = scaleText(stepText, 2);
      assert.strictEqual(
        scaled,
        "Ajouter l'huile d'olive (30 ml) et les carottes (400 g)."
      );
    });

    test('scaleText leaves text without parentheses untouched', () => {
      const stepText = 'Faire revenir à feu vif pendant 5 minutes.';
      assert.strictEqual(scaleText(stepText, 2), stepText);
    });
  });
});
