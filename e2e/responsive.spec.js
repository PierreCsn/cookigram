import { expect, test } from './fixtures.js';

const WIDTHS = [360, 390, 768, 1024, 1440];

test.describe('Responsive : aucun débordement horizontal', () => {
  for (const width of WIDTHS) {
    test(`la page de recette ne déborde pas horizontalement à ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1024 });
      await page.goto('/recipes/poulet-tikka-masala/');

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);
    });
  }

  for (const width of WIDTHS) {
    test(`le mode cuisine ne déborde pas horizontalement à ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1024 });
      await page.goto('/recipes/poulet-tikka-masala/cook/');

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);
    });
  }
});