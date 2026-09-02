import { expect, test } from '@playwright/test';

test('une recette préchargée reste disponible hors ligne', async ({ page, context }) => {
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  await context.setOffline(true);
  await page.goto('/recipes/curry-poulet-noix-coco/');
  await expect(page.getByRole('heading', { name: 'Curry de poulet à la noix de coco' })).toBeVisible();
  await expect(page.locator('.plate img')).toHaveAttribute('src', /curry-poulet-noix-coco\.jpg/);
  await page.locator('.start-cooking').click();
  await expect(page.getByText('Étape 1 sur 8')).toBeVisible();
  await context.setOffline(false);
});
