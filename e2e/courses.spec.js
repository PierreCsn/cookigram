import { expect, test } from '@playwright/test';

const RECIPE = '/recipes/lasagnes-moussaka/';

test('courses: ouverture du modal, compteurs, sélection persistée et copie', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: 'http://127.0.0.1:4173' });
  await page.goto(RECIPE);

  const openModalBtn = page.locator('.open-shopping-modal');
  await expect(openModalBtn).toContainText('Évaluer la liste (8)');
  await openModalBtn.click();

  const modal = page.locator('#shopping-modal');
  await expect(modal).toBeVisible();

  const aubergineCb = modal.locator('.to-buy-cb[data-slug="aubergine"]');
  await expect(aubergineCb).toBeChecked();

  await aubergineCb.uncheck();
  await expect(modal.locator('.to-buy-counter')).toHaveText('7 articles');
  await expect(page.locator('.open-shopping-modal')).toContainText('(7)');

  await modal.locator('.modal-copy-btn').click();
  const clipboard = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboard).toContain('Oignon');
  expect(clipboard).not.toContain('Aubergine');

  await modal.locator('.modal-close-btn').click();
  await page.locator('.open-shopping-modal').click();
  await expect(modal.locator('.to-buy-cb[data-slug="aubergine"]')).not.toBeChecked();
  await expect(modal.locator('.to-buy-cb[data-slug="oignon"]')).toBeChecked();
});