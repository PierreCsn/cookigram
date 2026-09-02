import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use) => {
    const errors = [];

    page.on('pageerror', (exception) => {
      errors.push(`[PageError] ${exception.message || exception}`);
    });

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (
          text.includes('net::ERR_FAILED') ||
          text.includes('net::ERR_INTERNET_DISCONNECTED')
        ) {
          return;
        }
        errors.push(`[ConsoleError] ${text}`);
      }
    });

    await use(page);

    expect(errors, `Des erreurs console ou des exceptions inattendues ont été détectées :\n${errors.join('\n')}`).toEqual([]);
  },
});

export { expect };
