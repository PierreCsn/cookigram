import { expect, test } from "./fixtures.js";

test.describe("Instruments de cuisine & Required equipment (#56)", () => {
  test("affiche les badges et icônes d'instruments sur la fiche recette", async ({ page }) => {
    await page.goto("/recipes/butter-chicken/");

    const applianceSection = page.locator(".appliance-required");
    await expect(applianceSection).toBeVisible();

    const badges = applianceSection.locator(".utensil-badge");
    await expect(badges).toHaveCount(5);

    // Vérifie la présence des icônes découpées
    const icons = applianceSection.locator(".utensil-icon");
    expect(await icons.count()).toBe(5);

    for (let i = 0; i < 5; i += 1) {
      const icon = icons.nth(i);
      await expect(icon).toBeVisible();
      const src = await icon.getAttribute("src");
      expect(src).toMatch(
        /\/assets\/icons\/utensils\/(casserole|poele|saladier|couteau|spatule|planche|plat-gratin|thermomix|moule|panier-vapeur|econome)\.webp/
      );
    }
  });

  test("affiche l'icône Thermomix et panier vapeur pour les recettes robot", async ({ page }) => {
    await page.goto("/recipes/curry-poulet-noix-coco/");

    const applianceSection = page.locator(".appliance-required");
    await expect(applianceSection).toBeVisible();

    const tmxIcon = applianceSection.locator(".utensil-badge:has-text('Thermomix') .utensil-icon");
    await expect(tmxIcon).toBeVisible();
    expect(await tmxIcon.getAttribute("src")).toContain("thermomix.webp");

    const varomaIcon = applianceSection.locator(".utensil-badge:has-text('Varoma') .utensil-icon");
    await expect(varomaIcon).toBeVisible();
    expect(await varomaIcon.getAttribute("src")).toContain("panier-vapeur.webp");
  });

  test("affiche le fallback texte/icône pour les instruments non répertoriés", async ({ page }) => {
    await page.goto("/recipes/cheesecake-japonais-extra-leger/");

    const applianceSection = page.locator(".appliance-required");
    await expect(applianceSection).toBeVisible();

    // Papier aluminium n'a pas d'icône spécifique -> fallback
    const fallbackBadge = applianceSection.locator(".utensil-badge.no-icon").first();
    await expect(fallbackBadge).toBeVisible();
    await expect(fallbackBadge.locator(".utensil-fallback-icon")).toHaveText("🍳");
    await expect(fallbackBadge).toContainText("Papier");
  });

  test("affiche les instruments requis en mode cuisine sans régression d'URL", async ({ page }) => {
    await page.goto("/recipes/butter-chicken/cook/");

    const cookAppliance = page.locator(".cook-appliance-required");
    await expect(cookAppliance).toBeVisible();

    const icons = cookAppliance.locator(".cook-utensil-icon");
    expect(await icons.count()).toBeGreaterThan(0);

    // Vérifie que l'image charge sans 404
    const firstIcon = icons.first();
    await expect(firstIcon).toBeVisible();
    const naturalWidth = await firstIcon.evaluate((img) => img.naturalWidth);
    expect(naturalWidth).toBeGreaterThan(0);
  });
});
