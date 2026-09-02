/**
 * Offline recipe download: lets users explicitly save a recipe for offline use.
 *
 * On recipe pages, a "save for offline" button appears. When clicked, it
 * caches the current page, its image, and the cook-mode page so the recipe
 * is available even if the service worker precache was cleared.
 */

const SAVE_KEY = 'cookigram:saved-recipes';

/**
 * Returns the set of saved recipe slugs from localStorage.
 *
 * @returns {Set<string>}
 */
export const getSavedRecipes = () => {
  try {
    const parsed = JSON.parse(localStorage.getItem(SAVE_KEY) || '[]');
    return new Set(Array.isArray(parsed) ? parsed : []);
  } catch {
    return new Set();
  }
};

/**
 * Persists the set of saved recipe slugs to localStorage.
 *
 * @param {Set<string>} slugs
 */
const persistSaved = (slugs) => {
  localStorage.setItem(SAVE_KEY, JSON.stringify([...slugs]));
};

/**
 * Determines the cache name used by the active service worker.
 *
 * @returns {Promise<string|null>}
 */
const getCacheName = async () => {
  if (!('caches' in self)) return null;
  const keys = await caches.keys();
  return keys.find((k) => k.startsWith('cookigram-')) || null;
};

/**
 * Caches a list of URLs into the service worker cache.
 *
 * @param {string[]} urls
 */
const cacheUrls = async (urls) => {
  const cacheName = await getCacheName();
  if (!cacheName) return;
  const cache = await caches.open(cacheName);
  await Promise.allSettled(
    urls.map(async (url) => {
      try {
        const response = await fetch(url);
        if (response?.ok) {
          await cache.put(url, response);
        }
      } catch {
        /* offline or network error — skip silently */
      }
    }),
  );
};

/**
 * Computes the URLs needed to make a recipe fully available offline.
 *
 * @param {string} slug
 * @param {string} prefix
 * @returns {string[]}
 */
const recipeOfflineUrls = (slug, prefix) => {
  const base = `${prefix}recipes/${slug}/`;
  const urls = [base];
  const cookBase = `${prefix}recipes/${slug}/cook/`;
  urls.push(cookBase);
  const img = document.querySelector('.plate img');
  if (img?.src) {
    const imgPath = new URL(img.getAttribute('src'), document.baseURI).pathname;
    urls.push(imgPath.startsWith('/') ? `.${imgPath}` : imgPath);
  }
  return urls;
};

/**
 * Updates the button state based on whether the recipe is saved.
 *
 * @param {HTMLButtonElement} btn
 * @param {boolean} saved
 */
const updateButton = (btn, saved) => {
  btn.classList.toggle('offline-saved', saved);
  btn.dataset.saved = String(saved);
  btn.innerHTML = saved
    ? '<span class="offline-save-icon">✓</span><span class="offline-save-label">Disponible hors ligne</span>'
    : '<span class="offline-save-icon">⬇</span><span class="offline-save-label">Télécharger hors ligne</span>';
  btn.setAttribute(
    'aria-label',
    saved ? 'Cette recette est disponible hors ligne' : 'Télécharger cette recette pour une utilisation hors ligne',
  );
};

/**
 * Handles the click on the offline-save button.
 *
 * @param {MouseEvent} event
 * @param {string} slug
 * @param {string} prefix
 */
const handleSave = async (event, slug, prefix) => {
  const btn = /** @type {HTMLButtonElement} */ (event.currentTarget);
  if (btn.disabled) return;
  btn.disabled = true;

  const saved = getSavedRecipes();

  if (saved.has(slug)) {
    saved.delete(slug);
    persistSaved(saved);
    updateButton(btn, false);
    btn.disabled = false;
    return;
  }

  btn.innerHTML =
    '<span class="offline-save-icon">⏳</span><span class="offline-save-label">Téléchargement…</span>';

  const urls = recipeOfflineUrls(slug, prefix);
  await cacheUrls(urls);

  saved.add(slug);
  persistSaved(saved);
  updateButton(btn, true);
  btn.disabled = false;

  const { showToast } = await import('./utils.js');
  showToast('✓ Recette disponible hors ligne');
};

/**
 * Initializes the offline-save button on recipe pages.
 * Tolerant to absence: does nothing if no [data-offline-slug] element exists.
 */
export const initOfflineSave = () => {
  const btn = document.querySelector('.offline-save-btn');
  if (!btn) return;

  const slug = btn.dataset.offlineSlug;
  const prefix = document.body?.dataset?.prefix || '';
  if (!slug) return;

  const saved = getSavedRecipes();
  updateButton(btn, saved.has(slug));

  btn.addEventListener('click', (e) => handleSave(e, slug, prefix));
};
