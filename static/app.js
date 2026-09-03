/**
 * CookiGram — Main frontend application entry point.
 * Orchestrates independently initialized, isolated feature modules.
 */

import { initCardVisuals } from './js/modules/card-visuals.js';
import { initChecklist } from './js/modules/checklist.js';
import { initCookMode, initSubsteps } from './js/modules/cook.js';
import { initOfflineSave } from './js/modules/offline-save.js';
import { initPortions } from './js/modules/portions.js';
import { initCatalogueSearch } from './js/modules/search.js';
import { initShare } from './js/modules/share.js';
import { initShoppingModal } from './js/modules/shopping.js';
import {
  initPwaInstall,
  initServiceWorker,
  initTheme,
} from './js/modules/theme.js';
import { initTimers } from './js/modules/timers.js';
import { initFeature } from './js/modules/utils.js';
import { initVariants } from './js/modules/variants.js';
import { initVoice } from './js/modules/voice.js';

// Global features (present on all pages)
initFeature('theme', initTheme);
initFeature('pwa-install', initPwaInstall);
initFeature('service-worker', () => {
  const prefix = document.body?.dataset?.prefix || '';
  initServiceWorker(prefix);
});

// Recipe page features
initFeature('variants', initVariants);
initFeature('share', initShare);
initFeature('portions', initPortions);
initFeature('checklist', initChecklist);
initFeature('shopping', initShoppingModal);
initFeature('offline-save', initOfflineSave);

// Catalogue page features
initFeature('search', initCatalogueSearch);
initFeature('card-visuals', initCardVisuals);

// Cook mode features
initFeature('cook', () => {
  initCookMode();
  initSubsteps();
});
initFeature('timers', () => initTimers());
initFeature('voice', initVoice);
