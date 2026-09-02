import { expect, test } from './fixtures.js';

test.describe('Catalogue: recherche et filtres', () => {
  test('recherche textuelle, vidage et remise à zéro', async ({ page }) => {
    await page.goto('/');

    const searchInput = page.locator('#recipe-search');
    const searchClear = page.locator('.search-clear');
    const count = page.locator('.recipes-count');
    const visibleCards = page.locator('.recipe-card:visible');

    const initialTotal = await visibleCards.count();
    expect(initialTotal).toBeGreaterThan(0);
    await expect(count).toHaveText(new RegExp(`^${initialTotal} recette`));

    // Recherche par mot clé
    await searchInput.fill('lasagnes');
    await expect(count).not.toHaveText(new RegExp(`^${initialTotal} recette`));
    const filteredCount = await visibleCards.count();
    expect(filteredCount).toBeGreaterThan(0);
    expect(filteredCount).toBeLessThan(initialTotal);
    await expect(visibleCards).toHaveCount(filteredCount);
    await expect(count).toHaveText(new RegExp(`^${filteredCount} recette`));
    await expect(searchClear).toBeVisible();

    // Effacer la recherche via la croix
    await searchClear.click();
    await expect(searchInput).toHaveValue('');
    await expect(searchClear).toBeHidden();
    await expect(visibleCards).toHaveCount(initialTotal);
    await expect(count).toHaveText(new RegExp(`^${initialTotal} recette`));

    // Recherche sans résultat -> affichage empty state
    await searchInput.fill('introuvable_xyz_999');
    await expect(page.locator('.empty-search')).toBeVisible();
    await expect(visibleCards).toHaveCount(0);
    await expect(count).toHaveText('0 recette');

    // Réinitialiser depuis le bouton empty-state
    await page.locator('.reset-search-btn').click();
    await expect(page.locator('.empty-search')).toBeHidden();
    await expect(visibleCards).toHaveCount(initialTotal);
    await expect(count).toHaveText(new RegExp(`^${initialTotal} recette`));
  });

  test('filtres par tags principaux et filtres avancés', async ({ page }) => {
    await page.goto('/');

    const initialTotal = await page.locator('.recipe-card:visible').count();

    // Filtre par catégorie (ex: pâtes)
    const patesChip = page.locator('.filter-chips .chip[data-tag="pâtes"]');
    if (await patesChip.count() > 0) {
      await patesChip.click();
      await expect(patesChip).toHaveClass(/active/);
      const filteredCount = await page.locator('.recipe-card:visible').count();
      expect(filteredCount).toBeGreaterThan(0);
      expect(filteredCount).toBeLessThanOrEqual(initialTotal);

      // Revenir à "Tous"
      await page.locator('.filter-chips .chip[data-tag="all"]').click();
      await expect(page.locator('.recipe-card:visible')).toHaveCount(initialTotal);
    }

    // Panneau de filtres avancés
    const advToggle = page.locator('.advanced-filter-toggle');
    const advPanel = page.locator('#advanced-filters-panel');

    if (await advToggle.count() > 0) {
      await expect(advPanel).toBeHidden();
      await advToggle.click();
      await expect(advPanel).toBeVisible();
      await expect(advToggle).toHaveAttribute('aria-expanded', 'true');

      const advChip = advPanel.locator('.adv-chip').first();
      await advChip.click();
      await expect(advChip).toHaveClass(/active/);

      const clearAdvBtn = advPanel.locator('.clear-advanced-btn');
      await expect(clearAdvBtn).toBeVisible();
      await clearAdvBtn.click();
      await expect(advChip).not.toHaveClass(/active/);
    }
  });
});
