import { expect, test } from '@playwright/test';

const RECIPE = '/recipes/roti-de-porc-sauce-echalote/';

test('sélectionne une variante par URL et revient au défaut si elle est inconnue', async ({ page }) => {
  await page.goto(`${RECIPE}?variant=sous-vide-four`);
  await expect(page.locator('.variant-select')).toHaveValue('sous-vide-four');
  await expect(page.getByText('jus de cuisson sous vide', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Cuire le rôti sous vide' })).toBeVisible();

  await page.goto(`${RECIPE}?variant=inconnue`);
  await expect(page.locator('.variant-select')).toHaveValue('thermomix-varoma');
  await expect(page).toHaveURL(RECIPE);
});

test('le sélecteur mobile reste accessible et transmet la variante au mode cuisine', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(RECIPE);
  const picker = page.locator('.variant-select');
  await expect(picker).toBeVisible();
  await expect(picker).toHaveCSS('min-height', '48px');
  await picker.selectOption('sous-vide-four');
  await expect(page).toHaveURL(/variant=sous-vide-four/);
  await page.locator('.start-cooking').click();
  await expect(page).toHaveURL(/cook\/\?variant=sous-vide-four/);
  await page.locator('.next').click();
  await page.locator('.next').click();
  await expect(page.getByText('À réaliser en parallèle')).toBeVisible();
  await expect(page.locator('.parallel-checkbox')).toHaveCount(2);
});
