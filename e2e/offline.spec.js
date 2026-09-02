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

test('la page de secours hors ligne saffiche pour une ressource non cachée', async ({ page, context }) => {
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  await context.setOffline(true);
  await page.goto('/page-inexistante/');
  await expect(page.getByRole('heading', { name: 'Page non disponible hors ligne' })).toBeVisible();
  await expect(page.locator('.offline-card p').first()).toContainText("n'a pas été téléchargée");
  await context.setOffline(false);
});

test('le bouton de téléchargement hors ligne fonctionne', async ({ page }) => {
  await page.goto('/recipes/curry-poulet-noix-coco/');
  await expect(page.locator('.offline-save-btn')).toBeVisible();
  await expect(page.locator('.offline-save-btn')).toContainText('Télécharger hors ligne');

  await page.locator('.offline-save-btn').click();
  await expect(page.locator('.offline-save-btn')).toContainText('Disponible hors ligne');
  await expect(page.locator('.offline-save-btn')).toHaveClass(/offline-saved/);

  const saved = await page.evaluate(() => {
    return JSON.parse(localStorage.getItem('cookigram:saved-recipes') || '[]');
  });
  expect(saved).toContain('curry-poulet-noix-coco');

  await page.locator('.offline-save-btn').click();
  await expect(page.locator('.offline-save-btn')).toContainText('Télécharger hors ligne');
  await expect(page.locator('.offline-save-btn')).not.toHaveClass(/offline-saved/);
});

test('le service worker se met à jour et active la nouvelle version', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  const firstVersion = await page.evaluate(() => {
    return navigator.serviceWorker.controller?.scriptURL || null;
  });

  await page.reload();
  await page.evaluate(() => navigator.serviceWorker.ready);
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  const secondVersion = await page.evaluate(() => {
    return navigator.serviceWorker.controller?.scriptURL || null;
  });
  expect(secondVersion).toBeTruthy();
  expect(secondVersion).toBe(firstVersion);
});

test('retour en ligne après déconnexion fonctionne', async ({ page, context }) => {
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);

  await page.goto('/recipes/curry-poulet-noix-coco/');
  await expect(page.locator('h1')).toContainText('Curry');

  await context.setOffline(true);
  await page.reload();
  await expect(page.locator('h1')).toContainText('Curry');

  await context.setOffline(false);
  await page.reload();
  await expect(page.locator('h1')).toContainText('Curry');
});
