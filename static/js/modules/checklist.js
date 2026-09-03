/**
 * Recipe ingredients checklist with per-recipe and per-variant localStorage persistence.
 */

import { showToast } from './utils.js';

export const initChecklist = () => {
  const checklistEl = document.querySelector('.ingredient-list.checklist');
  if (!checklistEl) return;

  const recipeSlug = checklistEl.dataset.recipe || '';
  const variantId = checklistEl.dataset.variant || 'main';
  const storageKey = `cookigram:${recipeSlug}:${variantId}:checked`;

  const getSavedChecked = () => {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || '[]');
    } catch (_) {
      return [];
    }
  };

  const saveChecked = (checkedArray) => {
    localStorage.setItem(storageKey, JSON.stringify(checkedArray));
  };

  const updateItemState = (item, isChecked) => {
    item.classList.toggle('checked', isChecked);
    const cb = item.querySelector('.ingredient-checkbox');
    if (cb) cb.checked = isChecked;
  };

  const savedChecked = new Set(getSavedChecked());
  checklistEl.querySelectorAll('.ingredient-item').forEach((item) => {
    const cb = item.querySelector('.ingredient-checkbox');
    const name = cb?.dataset.name || '';
    const isChecked = savedChecked.has(name);
    updateItemState(item, isChecked);

    cb?.addEventListener('change', () => {
      const currentSaved = new Set(getSavedChecked());
      if (cb.checked) {
        currentSaved.add(name);
      } else {
        currentSaved.delete(name);
      }
      saveChecked([...currentSaved]);
      updateItemState(item, cb.checked);
    });
  });

  const resetBtn = document.querySelector('.reset-checklist');
  resetBtn?.addEventListener('click', () => {
    localStorage.removeItem(storageKey);
    checklistEl.querySelectorAll('.ingredient-item').forEach((item) => {
      updateItemState(item, false);
    });
    showToast('✓ Checklist réinitialisée');
  });
};
