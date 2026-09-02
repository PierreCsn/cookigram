/**
 * Shared utility functions for CookiGram frontend.
 */

/**
 * Isolates each feature's initialization: an error in one feature must not
 * prevent subsequent features from executing.
 *
 * @param {string} label
 * @param {() => void} init
 */
export const initFeature = (label, init) => {
  try {
    init();
  } catch (err) {
    console.error(`[CookiGram] Initialisation « ${label} » impossible`, err);
  }
};

let toastTimer = null;

/**
 * Displays a non-blocking toast notification.
 *
 * @param {string} message - HTML or text content to display.
 * @param {number} duration - Duration in milliseconds before hiding.
 */
export const showToast = (message, duration = 3200) => {
  const toastEl = document.querySelector('.toast');
  if (!toastEl) return;
  if (toastTimer) clearTimeout(toastTimer);
  toastEl.innerHTML = message;
  toastEl.hidden = false;
  requestAnimationFrame(() => toastEl.classList.add('visible'));
  toastTimer = setTimeout(() => {
    toastEl.classList.remove('visible');
    setTimeout(() => {
      toastEl.hidden = true;
    }, 300);
  }, duration);
};
