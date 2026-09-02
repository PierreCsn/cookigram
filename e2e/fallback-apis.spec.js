import { expect, test } from './fixtures.js';

test.describe('Dégradation gracieuse sans API Web optionnelles', () => {
  test.beforeEach(async ({ page }) => {
    // Désactiver explicitement les APIs optionnelles dans la page
    await page.addInitScript(() => {
      delete window.SpeechRecognition;
      delete window.webkitSpeechRecognition;
      delete window.speechSynthesis;
      delete navigator.share;
      delete navigator.wakeLock;
    });
  });

  test('fiche recette: le partage fonctionne par repli sans navigator.share', async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: 'http://127.0.0.1:4173' });
    await page.goto('/recipes/lasagnes-moussaka/');

    const shareBtn = page.locator('.share-btn').first();
    await expect(shareBtn).toBeVisible();

    await shareBtn.click();
    await expect(shareBtn).toHaveClass(/copied/);
    await expect(shareBtn).toContainText('Lien copié');

    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    expect(clipboardText).toContain('/recipes/lasagnes-moussaka/');
  });

  test('mode cuisine: voix, synthèse et wake lock désactivés proprement', async ({ page }) => {
    await page.goto('/recipes/lasagnes-moussaka/cook/');

    // La reconnaissance vocale est désactivée
    const voiceBtn = page.locator('.voice-cmd');
    await expect(voiceBtn).toBeDisabled();
    await expect(voiceBtn).toHaveAttribute('title', /non disponible/);

    // Les boutons de synthèse vocale sont masqués
    await expect(page.locator('.auto-speak')).toBeHidden();
    const stepSpeakBtns = page.locator('.step-speak');
    for (let i = 0; i < await stepSpeakBtns.count(); i++) {
      await expect(stepSpeakBtns.nth(i)).toBeHidden();
    }

    // Le bouton Wake Lock se dégrade sans erreur
    const wakeBtn = page.locator('.wake');
    await expect(wakeBtn).toBeVisible();
    await wakeBtn.click();
    await expect(wakeBtn).toHaveAttribute('title', /non disponible/);
  });
});
