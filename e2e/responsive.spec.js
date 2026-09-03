import { expect, test } from './fixtures.js';

const WIDTHS = [360, 390, 768, 1024, 1440];

test.describe('Responsive : aucun débordement horizontal', () => {
  for (const width of WIDTHS) {
    test(`la page de recette ne déborde pas horizontalement à ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1024 });
      await page.goto('/recipes/poulet-tikka-masala/');

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);
    });
  }

  for (const width of WIDTHS) {
    test(`le mode cuisine ne déborde pas horizontalement à ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 1024 });
      await page.goto('/recipes/poulet-tikka-masala/cook/');

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);
    });
  }
});

test.describe('Responsive : illustration recette visible sur mobile', () => {
  for (const width of [360, 390, 414]) {
    test(`l'illustration de la fiche recette est visible à ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 844 });
      await page.goto('/recipes/poulet-tikka-masala/');

      const plate = page.locator('.recipe-heading .plate');
      await expect(plate).toBeVisible();
      const img = plate.locator('img');
      await expect(img).toBeVisible();
      await expect(img).toHaveAttribute('fetchpriority', 'high');

      const box = await plate.boundingBox();
      expect(box.width).toBeGreaterThan(0);
      expect(box.width).toBeLessThanOrEqual(width);
    });
  }
});

test.describe('Responsive : cibles tactiles >= 44px sur mobile', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
  });

  const MIN = 44;

  test('les filtres du catalogue atteignent la taille tactile minimale', async ({ page }) => {
    await page.goto('/');
    const sizes = await page.evaluate(() => {
      const pick = (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { w: r.width, h: r.height };
      };
      return {
        chip: pick('.chip'),
        advancedToggle: pick('.advanced-filter-toggle'),
        themeToggle: pick('.theme-toggle'),
      };
    });
    for (const [name, box] of Object.entries(sizes)) {
      expect(box, name).not.toBeNull();
      expect(box.h, `${name} hauteur`).toBeGreaterThanOrEqual(MIN);
    }
  });

  test('les contrôles de la fiche recette atteignent la taille tactile minimale', async ({ page }) => {
    await page.goto('/recipes/lasagnes-moussaka/');
    const sizes = await page.evaluate(() => {
      const pick = (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { w: r.width, h: r.height };
      };
      return {
        shoppingBtn: pick('.open-shopping-modal'),
        resetChecklist: pick('.reset-checklist'),
        shareCompact: pick('.share-btn-compact'),
        shareBtn: pick('.recipe-actions .share-btn'),
        offlineBtn: pick('.offline-save-btn'),
        portionMinus: pick('.portion-controls button[data-change="-1"]'),
        portionPlus: pick('.portion-controls button[data-change="1"]'),
        themeToggle: pick('.theme-toggle'),
      };
    });
    for (const [name, box] of Object.entries(sizes)) {
      expect(box, name).not.toBeNull();
      expect(box.h, `${name} hauteur`).toBeGreaterThanOrEqual(MIN);
    }
  });

  test('les contrôles du mode cuisine atteignent la taille tactile minimale', async ({ page }) => {
    await page.goto('/recipes/curry-poulet-noix-coco/cook/');

    const pick = (sel) =>
      page.evaluate((s) => {
        const el = document.querySelector(s);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { w: r.width, h: r.height };
      }, sel);

    for (const sel of ['.step-speak', '.cook-tools .theme-toggle', '.voice-cmd', '.auto-speak', '.wake', '.substep-label']) {
      const box = await pick(sel);
      expect(box, sel).not.toBeNull();
      expect(box.h, `${sel} hauteur`).toBeGreaterThanOrEqual(MIN);
    }

    const activeTimer = page.locator('.cook-step.active .timer-btn.timer-toggle').first();
    for (let i = 0; i < 20 && (await activeTimer.count()) === 0; i += 1) {
      await page.locator('.cook-nav .next').click();
    }
    await expect(activeTimer).toBeVisible();
    const timerBox = await activeTimer.boundingBox();
    expect(timerBox).not.toBeNull();
    expect(timerBox.height, 'timer hauteur').toBeGreaterThanOrEqual(MIN);
  });

  test('le bouton de fermeture de la modale atteint la taille tactile minimale', async ({ page }) => {
    await page.goto('/recipes/poulet-tikka-masala/');
    await page.locator('.open-shopping-modal').click();
    const box = await page.locator('.modal-close-btn').boundingBox();
    expect(box.height).toBeGreaterThanOrEqual(MIN);
    expect(box.width).toBeGreaterThanOrEqual(MIN);
  });
});