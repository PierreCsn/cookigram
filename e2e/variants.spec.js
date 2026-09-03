import { expect, test } from './fixtures.js';

const RECIPE = '/recipes/roti-de-porc-sauce-echalote/';

test('sélectionne une variante par URL et revient au défaut si elle est inconnue', async ({ page }) => {
  await page.goto(`${RECIPE}?variant=sous-vide-four`);
  await expect(page.locator('.variant-select')).toHaveValue('sous-vide-four');
  await expect(page.getByText('jus de cuisson sous vide', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Cuire le rôti sous vide' })).toBeVisible();

  await page.goto(`${RECIPE}?variant=inconnue`);
  await expect(page.locator('.variant-select')).toHaveValue('thermomix-varoma');
  await expect(page).toHaveURL(RECIPE);
});

test('le sélecteur mobile reste accessible et transmet la variante au mode cuisine', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(RECIPE);
  const picker = page.locator('.variant-select');
  await expect(picker).toBeVisible();
  await expect(picker).toHaveCSS('min-height', '48px');
  await picker.selectOption('sous-vide-four');
  await expect(page).toHaveURL(/variant=sous-vide-four/);
  await page.locator('.start-cooking').click();
  await expect(page).toHaveURL(/cook\/\?variant=sous-vide-four/);
  await page.locator('.next').click();
  await page.locator('.next').click();
  await expect(page.getByText('À réaliser en parallèle')).toBeVisible();
  await expect(page.locator('.parallel-checkbox')).toHaveCount(2);
});

test('affiche le panneau saveurs (accord, notes, piquant) sur une recette riche', async ({ page }) => {
  await page.goto('/recipes/porc-au-caramel/');
  const panel = page.locator('.flavor-panel');
  await expect(panel).toBeVisible();
  await expect(panel.locator('.flavor-label')).toHaveText('Saveurs & accord');
  await expect(panel.locator('.flavor-chips.flavor-pairing li')).toHaveText([
    'échine de porc',
    'caramel',
    'gingembre',
    'sauce soja',
  ]);
  await expect(panel.locator('.flavor-chips.flavor-notes li')).toHaveText(['sucré-salé', 'umami', 'laqué']);
  await expect(panel.locator('.flavor-harmony')).toBeVisible();
  await expect(panel.locator('.flavor-spice')).toContainText('1/5');
});

test("n'affiche pas de panneau saveurs sans flavors", async ({ page }) => {
  await page.goto('/recipes/blanquette-de-poulet/');
  await expect(page.locator('.flavor-panel')).toHaveCount(0);
});
