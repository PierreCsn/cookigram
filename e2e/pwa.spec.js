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

    const pngIcons = manifest.icons.filter((i) => i.type === 'image/png');
    expect(pngIcons.length).toBeGreaterThan(0);
    expect(manifest.icons.some((i) => i.sizes === '192x192')).toBe(true);
    expect(manifest.icons.some((i) => i.sizes === '512x512')).toBe(true);
  });

  test('les icônes PNG et le lien apple-touch-icon sont accessibles', async ({ page }) => {
    await page.goto('/');
    const appleTouch = page.locator('link[rel="apple-touch-icon"]');
    await expect(appleTouch).toHaveAttribute('href', /icon-192\.png/);

    const png192 = await page.request.get('/assets/icons/icon-192.png');
    expect(png192?.status()).toBe(200);
    expect(png192?.headers()['content-type']).toContain('image/png');

    const png512 = await page.request.get('/assets/icons/icon-512.png');
    expect(png512?.status()).toBe(200);
  });

  test('le rel="icon" est déclaré et les favicons sont servis en HTTP 200', async ({ page }) => {
    await page.goto('/recipes/poulet-tikka-masala/');

    const svg = page.locator('link[rel="icon"][type="image/svg+xml"]');
    await expect(svg).toHaveAttribute('href', /icon\.svg$/);

    const png192 = page.locator('link[rel="icon"][type="image/png"][sizes="192x192"]');
    await expect(png192).toHaveAttribute('href', /icon-192\.png$/);

    const svgResp = await page.request.get('/assets/icons/icon.svg');
    expect(svgResp?.status()).toBe(200);
    expect(svgResp?.headers()['content-type']).toContain('image/svg+xml');

    const pngResp = await page.request.get('/assets/icons/icon-192.png');
    expect(pngResp?.status()).toBe(200);
  });

  test('la page 404 personnalisée contient le bon contenu', async ({ page }) => {
    await page.goto('/404.html');
    await expect(page.getByRole('heading', { name: 'Page introuvable' })).toBeVisible();
    await expect(page.locator('.primary')).toHaveAttribute('href', './');
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
