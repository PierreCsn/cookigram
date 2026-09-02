/**
 * Shopping list evaluation, aisle grouping, pantry staples, and Keep export.
 */

import { showToast } from './utils.js';

/**
 * Initializes the shopping evaluation modal and export actions.
 */
export const initShoppingModal = () => {
  const shoppingModal = document.getElementById('shopping-modal');
  const openModalBtn = document.querySelector('.open-shopping-modal');
  const closeModalBtn = shoppingModal?.querySelector('.modal-close-btn');
  const checklistEl = document.querySelector('.ingredient-list.checklist');

  const recipeSlug =
    checklistEl?.dataset.recipe ||
    document.querySelector('.cook')?.dataset.recipe ||
    '';
  const evalStorageKey = `cookigram:${recipeSlug}:shopping-eval`;
  const oldEvalStorageKey = `cookgram:${recipeSlug}:shopping-eval`;

  const getSavedEval = () => {
    try {
      const stored =
        localStorage.getItem(evalStorageKey) || localStorage.getItem(oldEvalStorageKey);
      return stored ? JSON.parse(stored) : null;
    } catch (_) {
      return null;
    }
  };

  const saveEval = (stateMap) => {
    localStorage.setItem(evalStorageKey, JSON.stringify(stateMap));
  };

  const updateModalCounters = () => {
    if (!shoppingModal) return;
    const toBuyChecked = shoppingModal.querySelectorAll('.to-buy-cb:checked').length;
    const staplesChecked = shoppingModal.querySelectorAll('.staple-cb:checked').length;
    const totalSelected = toBuyChecked + staplesChecked;

    const counterEl = shoppingModal.querySelector('.to-buy-counter');
    if (counterEl) {
      counterEl.textContent = `${toBuyChecked} article${toBuyChecked > 1 ? 's' : ''}`;
    }

    const statusCount = shoppingModal.querySelector('.active-count');
    if (statusCount) statusCount.textContent = totalSelected;

    const mainBtn = document.querySelector('.open-shopping-modal');
    if (mainBtn) mainBtn.textContent = `🛒 Évaluer la liste (${totalSelected})`;
  };

  // Restore saved evaluation checkbox states if available
  const savedEval = getSavedEval();
  if (savedEval && shoppingModal) {
    shoppingModal.querySelectorAll('.eval-item-cb').forEach((cb) => {
      const slug = cb.dataset.slug;
      if (slug && slug in savedEval) {
        cb.checked = Boolean(savedEval[slug]);
      }
    });
  }
  updateModalCounters();

  // Modal event listeners
  if (shoppingModal) {
    openModalBtn?.addEventListener('click', () => {
      shoppingModal.showModal();
    });

    closeModalBtn?.addEventListener('click', () => {
      shoppingModal.close();
    });

    shoppingModal.addEventListener('click', (e) => {
      if (e.target === shoppingModal) {
        shoppingModal.close();
      }
    });

    shoppingModal.querySelectorAll('.eval-item-cb').forEach((cb) => {
      cb.addEventListener('change', () => {
        const currentMap = {};
        shoppingModal.querySelectorAll('.eval-item-cb').forEach((c) => {
          if (c.dataset.slug) currentMap[c.dataset.slug] = c.checked;
        });
        saveEval(currentMap);
        updateModalCounters();
      });
    });

    shoppingModal.querySelector('.select-all-to-buy')?.addEventListener('click', () => {
      shoppingModal.querySelectorAll('.to-buy-cb').forEach((cb) => {
        cb.checked = true;
      });
      const currentMap = {};
      shoppingModal.querySelectorAll('.eval-item-cb').forEach((c) => {
        if (c.dataset.slug) currentMap[c.dataset.slug] = c.checked;
      });
      saveEval(currentMap);
      updateModalCounters();
    });

    shoppingModal.querySelector('.uncheck-all')?.addEventListener('click', () => {
      shoppingModal.querySelectorAll('.eval-item-cb').forEach((cb) => {
        cb.checked = false;
      });
      const currentMap = {};
      shoppingModal.querySelectorAll('.eval-item-cb').forEach((c) => {
        if (c.dataset.slug) currentMap[c.dataset.slug] = c.checked;
      });
      saveEval(currentMap);
      updateModalCounters();
    });
  }

  const generateShoppingText = (format = 'standard') => {
    const title = document.querySelector('h1')?.textContent.trim() || 'Recette';
    const portions = document.querySelector('.portion-summary')?.textContent.trim() || '';

    // Prioritize evaluated shopping modal data
    if (shoppingModal) {
      const checkedBoxes = [...shoppingModal.querySelectorAll('.eval-item-cb:checked')];
      if (checkedBoxes.length === 0) {
        return `🛒 Courses · ${title}${portions ? ` (${portions})` : ''}\n\nAucun article sélectionné à acheter.`;
      }

      // Format for Google Keep: 1 clean line per item, convertible to native Keep checkboxes!
      if (format === 'keep') {
        const lines = [];
        checkedBoxes.forEach((cb) => {
          const name = cb.dataset.name || '';
          const qty = cb.dataset.qty || '';
          lines.push(qty ? `${name} : ${qty}` : name);
        });
        return lines.join('\n');
      }

      // Standard copy/share format with unicode ballot box checkboxes (☐) and department grouping
      const byAisle = {};
      const staplesList = [];

      checkedBoxes.forEach((cb) => {
        const name = cb.dataset.name || '';
        const qty = cb.dataset.qty || '';
        const aisle = cb.dataset.aisle || 'Épicerie';
        const line = qty ? `${name} : ${qty}` : name;

        if (cb.classList.contains('staple-cb')) {
          staplesList.push(line);
        } else {
          byAisle[aisle] = byAisle[aisle] || [];
          byAisle[aisle].push(line);
        }
      });

      let text = `🛒 Courses · ${title}${portions ? ` (${portions})` : ''}\n\n`;

      const aisles = Object.keys(byAisle);
      if (aisles.length > 0) {
        aisles.forEach((aisle) => {
          text += `📍 Rayon ${aisle} :\n`;
          byAisle[aisle].forEach((item) => {
            text += `  ☐ ${item}\n`;
          });
          text += '\n';
        });
      }

      if (staplesList.length > 0) {
        text += '🧂 Fond de placard (à réapprovisionner) :\n';
        staplesList.forEach((item) => {
          text += `  ☐ ${item}\n`;
        });
        text += '\n';
      }

      text += `Lien : ${window.location.href}`;
      return text;
    }

    // Fallback: recipe page checklist
    if (checklistEl) {
      const items = [...checklistEl.querySelectorAll('.ingredient-item')];
      const toBuy = [];
      items.forEach((item) => {
        const name = item.querySelector('.ingredient-name')?.textContent.trim() || '';
        const qty = item.querySelector('strong')?.textContent.trim() || '';
        if (!name.toLowerCase().includes('eau')) {
          toBuy.push(qty ? `${name} : ${qty}` : name);
        }
      });

      if (format === 'keep') {
        return toBuy.join('\n');
      }

      let text = `🛒 Courses · ${title}${portions ? ` (${portions})` : ''}\n\n`;
      text += `À acheter :\n${toBuy.map((i) => `☐ ${i}`).join('\n')}\n\n`;
      text += `Lien : ${window.location.href}`;
      return text;
    }

    return '';
  };

  const copyShoppingList = async (format = 'standard') => {
    const text = generateShoppingText(format);
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (_) {
      const temp = document.createElement('textarea');
      temp.value = text;
      document.body.appendChild(temp);
      temp.select();
      document.execCommand('copy');
      document.body.removeChild(temp);
      return true;
    }
  };

  document.querySelectorAll('.copy-list').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await copyShoppingList('standard');
      showToast('📋 Liste de courses copiée (avec cases ☐) !');
    });
  });

  document.querySelectorAll('.keep-list').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await copyShoppingList('keep');
      window.open('https://keep.new', '_blank', 'noopener,noreferrer');
      showToast(
        '🟡 Liste copiée pour Keep ! Collez (Ctrl+V) puis cliquez sur ⋮ > « Afficher les cases à cocher »',
        6000
      );
    });
  });

  document.querySelectorAll('.share-list').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text = generateShoppingText('standard');
      const title = document.querySelector('h1')?.textContent.trim() || 'Courses';

      if (navigator.share) {
        try {
          await navigator.share({ title: `Courses · ${title}`, text });
          return;
        } catch (err) {
          if (err.name === 'AbortError') return;
        }
      }

      await copyShoppingList('standard');
      showToast('✓ Liste copiée pour partage !');
    });
  });
};
