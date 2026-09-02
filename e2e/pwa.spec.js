import { expect, test } from './fixtures.js';

test.describe('PWA et mode hors ligne', () => {
  test('le manifest est valide et accessible', async ({ page }) => {
    const response = await page.goto('/manifest.webmanifest');
    expect(response?.status()).toBe(200);

    const manifest = await response?.json();
    expect(manifest.name).toBe('CookiGram');
    expect(manifest.display).toBe('standalone');
    expect(manifest.start_url).toBe('./');
    expect(manifest.icons.length).toBeGreaterThan(0);
  });

  test('le service worker permet la navigation hors ligne après consultation', async ({ page, context }) => {
    // 1. Charger la page d'accueil en ligne et attendre l'activation du service worker
    await page.goto('/');
    await page.evaluate(async () => {
      if ('serviceWorker' in navigator) {
        await navigator.serviceWorker.ready;
      }
    });

    // 2. Consulter une fiche recette en ligne pour la mettre en cache
    await page.goto('/recipes/lasagnes-moussaka/');
    await expect(page.locator('h1')).toContainText('Lasagnes');

    // 3. Basculer en mode hors ligne (mode avion)
    await context.setOffline(true);

    try {
      // Recharger la fiche recette hors ligne : doit charger depuis le cache SW
      await page.reload();
      await expect(page.locator('h1')).toContainText('Lasagnes');
      await expect(page.locator('.ingredient-list')).toBeVisible();

      // Retourner à l'accueil hors ligne : doit charger depuis le cache SW
      await page.goto('/');
      await expect(page.locator('.hero-title')).toBeVisible();
      await expect(page.locator('.recipe-card:visible').first()).toBeVisible();
    } finally {
      // Restaurer le réseau pour les autres tests
      await context.setOffline(false);
    }
  });
});
