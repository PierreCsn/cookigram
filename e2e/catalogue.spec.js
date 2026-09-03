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
      await expect(clearAdvBtn).not.toHaveClass(/active/);
    }
  });

  test('les badges de tags des fiches relient au catalogue filtré via ancre', async ({ page }) => {
    await page.goto('/recipes/curry-poulet-noix-coco/');

    // Les badges de tags sont des liens explorables vers le catalogue.
    const curryTag = page.locator('.tag-link', { hasText: 'curry' }).first();
    await expect(curryTag).toBeVisible();
    await expect(curryTag).toHaveAttribute('href', '../../#tag-curry');

    // Le clic ramène à l'accueil et active le filtre correspondant.
    await curryTag.click();
    await expect(page).toHaveURL(/#tag-curry$/);

    const chip = page.locator('.filter-chips .chip[data-tag="curry"]');
    await expect(chip).toHaveClass(/active/);

    const visibleCards = page.locator('.recipe-card:visible');
    const visibleCount = await visibleCards.count();
    expect(visibleCount).toBeGreaterThan(0);
    // Chaque carte filtrée affiche bien le tag "curry".
    const curryCards = await page.locator('.recipe-card:visible').evaluateAll((cards) =>
      cards.filter((c) => c.getAttribute('data-tags')?.split(' ').includes('curry')).length
    );
    expect(curryCards).toBe(visibleCount);
  });

  test('filtre par durée de préparation et cuisson dans les filtres avancés', async ({ page }) => {
    await page.goto('/');

    const initialTotal = await page.locator('.recipe-card:visible').count();
    const advToggle = page.locator('.advanced-filter-toggle');
    const advPanel = page.locator('#advanced-filters-panel');

    await expect(advPanel).toBeHidden();
    await advToggle.click();
    await expect(advPanel).toBeVisible();

    // Filtre "Prêt en <= 30 min"
    const under30Chip = advPanel.locator('.time-chip[data-time-filter="under-30"]');
    await under30Chip.click();
    await expect(under30Chip).toHaveClass(/active/);

    const filteredCards = page.locator('.recipe-card:visible');
    const filteredCount = await filteredCards.count();
    expect(filteredCount).toBeGreaterThan(0);
    expect(filteredCount).toBeLessThan(initialTotal);

    // Vérifier que le badge de filtres actifs affiche 1
    const badge = page.locator('.adv-badge');
    await expect(badge).toBeVisible();
    await expect(badge).toHaveText('1');

    // Cliquer à nouveau pour désactiver le filtre de durée
    await under30Chip.click();
    await expect(under30Chip).not.toHaveClass(/active/);
    await expect(page.locator('.recipe-card:visible')).toHaveCount(initialTotal);
    await expect(badge).toBeHidden();
  });
});

test.describe('Catalogue: harmonisation des cartes (#34)', () => {
  test('les visuels chargent avec un fondu et désactivent le shimmer', async ({ page }) => {
    await page.goto('/');

    const visual = page.locator('.card-visual').first();
    const img = visual.locator('img');

    await expect(img).toBeVisible();
    // Une fois l'image décodée, le shimmer s'arrête et le fondu se déclenche.
    await expect(visual).toHaveClass(/is-loaded/, { timeout: 15000 });
    // Le fondu termine sur une opacité pleine (transition 0.25s).
    await expect(img).toHaveCSS('opacity', '1', { timeout: 5000 });

    const transitionDuration = await img.evaluate((el) => {
      const { transitionDuration: d } = getComputedStyle(el);
      return parseFloat(d);
    });
    expect(transitionDuration).toBeGreaterThanOrEqual(0.25);
  });

  test('les métadonnées des cartes d\'une même rangée sont alignées en bas', async ({ page }) => {
    await page.goto('/');

    const rows = await page.evaluate(() => {
      const metas = [...document.querySelectorAll('.recipe-card .recipe-meta')];
      const positions = metas.map((meta) => {
        const card = meta.closest('.recipe-card');
        const cardRect = card.getBoundingClientRect();
        const metaRect = meta.getBoundingClientRect();
        return {
          top: Math.round(cardRect.top),
          gapFromBottom: Math.round(cardRect.bottom - metaRect.bottom),
        };
      });
      positions.sort((a, b) => a.top - b.top);
      return positions;
    });

    // Les cartes d'une même rangée visuelle partagent le même offset haut.
    const firstRowTop = rows[0].top;
    const firstRow = rows.filter((r) => r.top === firstRowTop);
    // Tous les pieds reposent au même niveau : écart au bas identique.
    const gaps = new Set(firstRow.map((r) => r.gapFromBottom));
    expect(firstRow.length).toBeGreaterThan(1);
    expect(gaps.size).toBe(1);
  });
});
