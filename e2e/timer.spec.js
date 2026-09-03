import { expect, test } from './fixtures.js';

const COOK_URL = '/recipes/veloute-potiron-cannelle/cook/';

test.describe('Minuteur de cuisson', () => {
  test('démarrage, pause, reprise et remise à zéro', async ({ page }) => {
    await page.goto(COOK_URL);

    await page.locator('.mep-start:visible').click();
    const firstStep = page.locator('.cook-step:not(.cook-mep-step)').first();
    const timer = firstStep.locator('.timer').first();

    const statusEl = timer.locator('.timer-status');
    const displayEl = timer.locator('.timer-display');
    const toggleBtn = timer.locator('.timer-toggle');
    const resetBtn = timer.locator('.timer-reset');

    // État initial
    await expect(statusEl).toHaveText('Minuteur');
    await expect(displayEl).toHaveText('5 s');
    await expect(toggleBtn).toContainText('Démarrer');
    await expect(resetBtn).toBeHidden();
    await expect(timer).not.toHaveClass(/running/);
    await expect(timer).not.toHaveClass(/paused/);

    // 1. Démarrer
    await toggleBtn.click();
    await expect(timer).toHaveClass(/running/);
    await expect(statusEl).toHaveText('En cours...');
    await expect(toggleBtn).toContainText('Pause');
    await expect(resetBtn).toBeVisible();

    // 2. Mettre en pause
    await toggleBtn.click();
    await expect(timer).toHaveClass(/paused/);
    await expect(timer).not.toHaveClass(/running/);
    await expect(statusEl).toHaveText('En pause');
    await expect(toggleBtn).toContainText('Reprendre');

    // 3. Reprendre
    await toggleBtn.click();
    await expect(timer).toHaveClass(/running/);
    await expect(timer).not.toHaveClass(/paused/);
    await expect(statusEl).toHaveText('En cours...');

    // 4. Remise à zéro
    await resetBtn.click();
    await expect(timer).not.toHaveClass(/running/);
    await expect(timer).not.toHaveClass(/paused/);
    await expect(statusEl).toHaveText('Minuteur');
    await expect(displayEl).toHaveText('5 s');
    await expect(toggleBtn).toContainText('Démarrer');
    await expect(resetBtn).toBeHidden();
  });
});
