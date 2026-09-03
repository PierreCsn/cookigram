import { expect } from '@playwright/test';
import { test } from './fixtures.js';

function channelToLum(value) {
  const c = value / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

function relativeLuminance(hex) {
  const cleaned = hex.replace('#', '');
  const r = parseInt(cleaned.slice(0, 2), 16);
  const g = parseInt(cleaned.slice(2, 4), 16);
  const b = parseInt(cleaned.slice(4, 6), 16);
  return 0.2126 * channelToLum(r) + 0.7152 * channelToLum(g) + 0.0722 * channelToLum(b);
}

function contrastRatio(hexA, hexB) {
  const l1 = relativeLuminance(hexA);
  const l2 = relativeLuminance(hexB);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

test.describe('Accessibilité (WCAG 2.2 AA) — Lot 3 #31', () => {
  test('le texte d\'accentuation atteint 4.5:1 sur crème et sur blanc en mode clair', async ({ page }) => {
    // Forcer le thème clair pour mesurer le jeton mobile de façon déterministe.
    await page.addInitScript(() => {
      const applyLight = () => {
        if (document.documentElement) {
          document.documentElement.setAttribute('data-theme', 'light');
        }
      };
      applyLight();
      document.addEventListener('DOMContentLoaded', applyLight);
    });
    await page.goto('/recipes/poulet-tikka-masala/');

    const tokens = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return {
        accentText: styles.getPropertyValue('--accent-text').trim(),
        cream: styles.getPropertyValue('--cream').trim(),
        card: styles.getPropertyValue('--card').trim(),
      };
    });

    const onCream = contrastRatio(tokens.accentText, tokens.cream);
    const onCard = contrastRatio(tokens.accentText, tokens.card);

    expect(tokens.accentText).toMatch(/^#[0-9a-f]{6}$/i);
    expect(onCream, `--accent-text sur crème (${tokens.accentText}/${tokens.cream})`).toBeGreaterThanOrEqual(4.5);
    expect(onCard, `--accent-text sur blanc (${tokens.accentText}/${tokens.card})`).toBeGreaterThanOrEqual(4.5);
  });

  test('un élément interactif affiche un anneau de focus visible :focus-visible au clavier', async ({ page }) => {
    await page.goto('/recipes/poulet-tikka-masala/');

    // Faire du clavier la source de focus effective (Tab) puis vérifier que
    // l'élément focalisé expose un outline visible via :focus-visible.
    for (let i = 0; i < 4; i += 1) {
      await page.keyboard.press('Tab');
    }

    const focusStyle = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const styles = getComputedStyle(el);
      return {
        tag: el.tagName,
        style: styles.outlineStyle,
        width: styles.outlineWidth,
        color: styles.outlineColor,
      };
    });

    expect(focusStyle, 'un élément doit recevoir le focus clavier').not.toBeNull();
    expect(focusStyle.style, `${focusStyle?.tag} outline-style`).not.toBe('none');
    expect(parseFloat(focusStyle.width), `${focusStyle?.tag} outline-width`).toBeGreaterThanOrEqual(2);
    expect(focusStyle.color, `${focusStyle?.tag} outline-color`).not.toBe('rgba(0, 0, 0, 0)');
  });

  test('prefers-reduced-motion neutralise les animations pulsantes', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/recipes/lasagnes-moussaka/cook/');

    const stepSpeak = page.locator('.step-speak').first();
    await expect(stepSpeak).toBeVisible();
    // Active l'état pulsant (indépendamment de l'API voix) pour vérifier la règle CSS.
    await stepSpeak.evaluate((el) => el.classList.add('speaking'));

    const duration = await stepSpeak.evaluate((el) => getComputedStyle(el).animationDuration);
    const iterations = await stepSpeak.evaluate((el) => getComputedStyle(el).animationIterationCount);

    // La règle globale @media (prefers-reduced-motion: reduce) force ~0.001ms / 1 itération.
    expect(parseFloat(duration)).toBeLessThanOrEqual(0.01);
    expect(iterations).toBe('1');
  });
});
