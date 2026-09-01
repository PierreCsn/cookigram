import { expect, test } from '@playwright/test';

const RECIPE = '/recipes/lasagnes-moussaka/';

test('checklist: cocher un ingrédient, persister après rechargement, réinitialiser', async ({ page }) => {
  await page.goto(RECIPE);

  const item = page.locator('li.ingredient-item', { has: page.locator('input.ingredient-checkbox[data-name="sauce tomate"]') });
  const cb = page.locator('input.ingredient-checkbox[data-name="sauce tomate"]');

  await expect(cb).not.toBeChecked();
  await expect(item).not.toHaveClass(/checked/);

  await cb.check();
  await expect(cb).toBeChecked();
  await expect(item).toHaveClass(/checked/);

  await page.reload();
  const cbAfterReload = page.locator('input.ingredient-checkbox[data-name="sauce tomate"]');
  await expect(cbAfterReload).toBeChecked();

  await page.locator('.reset-checklist').click();
  await expect(cbAfterReload).not.toBeChecked();

  await page.reload();
  await expect(page.locator('input.ingredient-checkbox[data-name="sauce tomate"]')).not.toBeChecked();
});