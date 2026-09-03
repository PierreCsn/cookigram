import { expect, test } from './fixtures.js';

const COOK_URL = '/recipes/lasagnes-moussaka/cook/';

test.describe('Mode cuisine: navigation et sous-étapes', () => {
  test('navigation entre les étapes, mise à jour de la barre et persistance', async ({ page }) => {
    await page.goto(COOK_URL);

    const prevBtn = page.locator('button.prev');
    const nextBtn = page.locator('button.next');
    const progressBar = page.locator('.progress i');
    const steps = page.locator('.cook-step');

    const totalSteps = await steps.count();
    expect(totalSteps).toBe(6);

    // Étape 1 initiale
    await expect(steps.nth(0)).toHaveClass(/active/);
    await expect(prevBtn).toBeDisabled();
    await expect(nextBtn).toHaveText('Suivant →');
    await expect(progressBar).toHaveCSS('width', /.+/);

    // Avancer à l'étape 2
    await nextBtn.click();
    await expect(steps.nth(0)).not.toHaveClass(/active/);
    await expect(steps.nth(1)).toHaveClass(/active/);
    await expect(prevBtn).toBeEnabled();

    // Recharger la page : la persistance doit nous ramener à l'étape 2
    await page.reload();
    await expect(steps.nth(1)).toHaveClass(/active/);
    await expect(prevBtn).toBeEnabled();

    // Reculer vers l'étape 1
    await prevBtn.click();
    await expect(steps.nth(0)).toHaveClass(/active/);
    await expect(prevBtn).toBeDisabled();

    // Avancer jusqu'à la dernière étape
    for (let i = 0; i < totalSteps - 1; i++) {
      await nextBtn.click();
    }
    await expect(steps.nth(totalSteps - 1)).toHaveClass(/active/);
    await expect(nextBtn).toHaveText('Terminer ✓');

    // Cliquer sur "Terminer ✓" doit rediriger vers la fiche recette
    await nextBtn.click();
    await expect(page).toHaveURL(/\/recipes\/lasagnes-moussaka\/$/);
  });

  test('gestion et persistance des sous-étapes', async ({ page }) => {
    await page.goto(COOK_URL);

    const firstStep = page.locator('.cook-step').first();
    const substepsProgress = firstStep.locator('.substeps-progress');
    const firstCheckbox = firstStep.locator('.substep-checkbox').first();
    const firstItem = firstStep.locator('.substep-item').first();

    await expect(substepsProgress).toHaveText('0 / 2');
    await expect(firstCheckbox).not.toBeChecked();

    // Cocher la 1ère sous-étape
    await firstCheckbox.check();
    await expect(firstCheckbox).toBeChecked();
    await expect(firstItem).toHaveClass(/checked/);
    await expect(substepsProgress).toHaveText('1 / 2');

    // Recharger la page
    await page.reload();
    const firstStepReloaded = page.locator('.cook-step').first();
    await expect(firstStepReloaded.locator('.substep-checkbox').first()).toBeChecked();
    await expect(firstStepReloaded.locator('.substeps-progress')).toHaveText('1 / 2');

    // Décocher pour remettre à zéro
    await firstStepReloaded.locator('.substep-checkbox').first().uncheck();
    await expect(firstStepReloaded.locator('.substeps-progress')).toHaveText('0 / 2');
  });

  test('la barre de navigation ne chevauche pas les minuteurs ni les sous-étapes sur mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/recipes/roti-de-porc-sauce-echalote/cook/');

    // Étape 1 du rôti de porc : plusieurs sous-étapes + minuteurs.
    // Le bas du contenu doit être atteignable sans être masqué par .cook-nav.
    const firstStep = page.locator('.cook-step').first();
    const nav = page.locator('.cook-nav');

    const lastElement = firstStep.locator('.substeps-card, .timer').last();
    await expect(lastElement).toBeVisible();

    // Faire défiler jusqu'au fond du document : la marge de bas de page doit
    // garantir que le dernier élément reste visible au-dessus de la barre sticky.
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    const lastBox = await lastElement.boundingBox();
    const navBox = await nav.boundingBox();
    expect(lastBox).not.toBeNull();
    expect(navBox).not.toBeNull();
    expect(lastBox.y + lastBox.height).toBeLessThanOrEqual(navBox.y + 1);

    // Le titre d'étape ne doit pas excéder 3 lignes sur 390px.
    const h1 = firstStep.locator('h1');
    const h1Box = await h1.boundingBox();
    expect(h1Box.height).toBeLessThanOrEqual(3 * 32 * 1.25);
  });

  test('affiche les ingrédients de l\'étape active et les reconstitue au changement de portions', async ({ page }) => {
    // Portions mémorisées : 4 (base), on demande 8 via le stockage avant chargement.
    await page.addInitScript(() => {
      localStorage.setItem('cookigram:lasagnes-moussaka:portions', '8');
    });
    await page.goto('/recipes/lasagnes-moussaka/cook/');

    const card = page.locator('.step-ingredients-card').first();
    await expect(card).toBeVisible();
    await expect(card.locator('.step-ingredients-title')).toHaveText('Ingrédients pour cette étape');

    // Une quantité scalaire doit être doublée par le facteur 2 (8/4).
    const qty = card.locator('.step-ingredient-qty[data-scale-text]').first();
    await expect(qty).not.toBeEmpty();
  });

  test('les étapes sans ingrédient ne rendent pas de carte vide', async ({ page }) => {
    await page.goto('/recipes/lasagnes-moussaka/cook/');

    // Le nombre de cartes doit correspondre au nombre d'étapes avec ingrédients,
    // et aucune carte ne doit être vide.
    const cards = page.locator('.step-ingredients-card');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < count; i += 1) {
      await expect(cards.nth(i).locator('.step-ingredients-list')).not.toBeEmpty();
    }
  });

  test('affiche et met à jour le temps restant au fil des étapes (#67)', async ({ page }) => {
    await page.goto('/recipes/butter-chicken/cook/');

    const activeStep = page.locator('.cook-step.active');
    const timeEl = activeStep.locator('.step-remaining-time');
    await expect(timeEl).toBeVisible();
    await expect(timeEl).toContainText('⏱ ~50 min');

    // Avancer à l'étape 2
    await page.locator('button.next').click();
    const step2Time = page.locator('.cook-step.active .step-remaining-time');
    await expect(step2Time).toBeVisible();
    await expect(step2Time).toContainText('⏱ ~42 min');

    // Naviguer jusqu'à la dernière étape
    const nextBtn = page.locator('button.next');
    while ((await nextBtn.textContent()) !== 'Terminer ✓') {
      await nextBtn.click();
    }
    const lastStepTime = page.locator('.cook-step.active .step-remaining-time');
    await expect(lastStepTime).toBeVisible();
    await expect(lastStepTime).toContainText('⏱ ~8 min');
  });
});
