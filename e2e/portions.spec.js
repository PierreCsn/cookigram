import { expect, test } from './fixtures.js';

const RECIPE = '/recipes/lasagnes-moussaka/';

test('portions: recalcul, limites min/max et persistance', async ({ page }) => {
  await page.goto(RECIPE);

  const output = page.locator('.portion-picker output');
  const qty = page.locator('[data-scale-quantity="400 g"]');
  await expect(output).toHaveText('4');
  await expect(qty).toHaveText('400 g');

  const plus = page.locator('[data-change="1"]');
  const minus = page.locator('[data-change="-1"]');

  await plus.click();
  await expect(output).toHaveText('5');
  await expect(qty).toHaveText('500 g');

  while (!(await plus.isDisabled())) {
    await plus.click();
  }
  await expect(output).toHaveText('8');
  await expect(plus).toBeDisabled();

  while (!(await minus.isDisabled())) {
    await minus.click();
  }
  await expect(output).toHaveText('2');
  await expect(minus).toBeDisabled();

  await plus.click();
  await expect(output).toHaveText('3');
  await page.reload();
  await expect(page.locator('.portion-picker output')).toHaveText('3');
});