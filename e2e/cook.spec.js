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
});
