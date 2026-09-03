/**
 * Catalog card visuals: smooth skeleton shimmer while lazy images load,
 * then a discreet fade-in once each image is decoded.
 */

/**
 * Marks a card visual as "loaded": stops the shimmer and reveals the image
 * (or the monogram) with a soft 0.25s fade.
 *
 * @param {HTMLElement} visual
 */
const markLoaded = (visual) => {
  if (visual.classList.contains('is-loaded')) return;
  const img = visual.querySelector('img');
  if (img) img.classList.add('is-loaded');
  visual.classList.add('is-loaded');
};

/**
 * Initializes the loading states of every catalog card visual. Cards already
 * rendered before this runs (e.g. cached images) are resolved immediately.
 */
export const initCardVisuals = () => {
  const visuals = document.querySelectorAll('.card-visual');
  if (!visuals.length) return;

  visuals.forEach((visual) => {
    const img = visual.querySelector('img');

    if (!img || img.complete) {
      markLoaded(visual);
      return;
    }

    const reveal = () => {
      markLoaded(visual);
      img.removeEventListener('load', reveal);
      img.removeEventListener('error', reveal);
    };

    img.addEventListener('load', reveal);
    img.addEventListener('error', reveal);

    if (typeof img.decode === 'function') {
      img.decode().then(reveal).catch(() => {
        /* decode() peut rejeter si l'image est perturbée : on retombe sur load/error */
      });
    }
  });
};
