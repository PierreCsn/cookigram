/**
 * Web Share API and clipboard copy with feedback.
 */

/**
 * Displays visual feedback on the share button.
 *
 * @param {HTMLElement} btn
 * @param {string} text
 */
export const showShareFeedback = (btn, text = '✓ Lien copié !') => {
  btn.classList.add('copied');
  const label = btn.querySelector('.share-label') || btn;
  const original = label.textContent;
  label.textContent = text;
  setTimeout(() => {
    btn.classList.remove('copied');
    label.textContent = original;
  }, 2000);
};

/**
 * Triggers native share or falls back to clipboard copying.
 *
 * @param {HTMLElement} btn
 */
export const shareRecipe = async (btn) => {
  const title = document.title || 'CookiGram';
  const desc =
    document.querySelector('.recipe-heading p')?.textContent ||
    'Découvrez cette recette sur CookiGram !';
  const url = window.location.href;

  if (navigator.share) {
    try {
      await navigator.share({ title, text: `${title} - ${desc}`, url });
      return;
    } catch (err) {
      if (err.name === 'AbortError') return;
    }
  }

  try {
    await navigator.clipboard.writeText(url);
    showShareFeedback(btn, '✓ Lien copié !');
  } catch (_) {
    const tempInput = document.createElement('input');
    tempInput.value = url;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    showShareFeedback(btn, '✓ Lien copié !');
  }
};

/**
 * Binds click events to all share buttons on the page.
 */
export const initShare = () => {
  document.querySelectorAll('.share-btn').forEach((btn) => {
    btn.addEventListener('click', () => shareRecipe(btn));
  });
};
