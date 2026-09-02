/**
 * Instant catalogue search, tag filtering, advanced tags panel, and empty state.
 */

/**
 * Normalizes text for search matching by stripping diacritics and lowercasing.
 *
 * @param {string} str
 * @returns {string}
 */
export const normalizeText = (str) =>
  (str || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

/**
 * Initializes catalogue search, chips, and advanced filter drawer.
 */
export const initCatalogueSearch = () => {
  const catalogueSection = document.querySelector('.catalogue');
  if (!catalogueSection) return;

  const searchInput = document.getElementById('recipe-search');
  const searchClear = document.querySelector('.search-clear');
  const chips = document.querySelectorAll('.filter-chips .chip');
  const cards = [...document.querySelectorAll('.recipe-card')];
  const countEl = document.querySelector('.recipes-count');
  const emptyState = document.querySelector('.empty-search');
  const resetSearchBtn = document.querySelector('.reset-search-btn');
  const filterChipsBar = document.querySelector('.filter-chips');

  if (filterChipsBar) {
    filterChipsBar.addEventListener(
      'wheel',
      (e) => {
        if (e.deltaY !== 0 && !e.shiftKey) {
          filterChipsBar.scrollLeft += e.deltaY;
          e.preventDefault();
        }
      },
      { passive: false }
    );
  }

  let activeTag = 'all';
  const activeAdvancedTags = new Set();

  const advancedToggleBtn = document.querySelector('.advanced-filter-toggle');
  const advancedPanel = document.getElementById('advanced-filters-panel');
  const advChips = document.querySelectorAll('.adv-chip');
  const clearAdvancedBtn = document.querySelector('.clear-advanced-btn');
  const advBadge = document.querySelector('.adv-badge');

  const updateAdvancedUI = () => {
    const count = activeAdvancedTags.size;
    if (advBadge) {
      advBadge.textContent = count;
      advBadge.hidden = count === 0;
    }
    if (clearAdvancedBtn) {
      clearAdvancedBtn.hidden = count === 0;
    }
  };

  if (advancedToggleBtn && advancedPanel) {
    advancedToggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const isExpanded = advancedToggleBtn.getAttribute('aria-expanded') === 'true';
      const nextExpanded = !isExpanded;
      advancedToggleBtn.setAttribute('aria-expanded', String(nextExpanded));
      advancedPanel.hidden = !nextExpanded;
      advancedPanel.classList.toggle('open', nextExpanded);
    });
  }

  advChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const tag = chip.dataset.advancedTag;
      if (activeAdvancedTags.has(tag)) {
        activeAdvancedTags.delete(tag);
        chip.classList.remove('active');
      } else {
        activeAdvancedTags.add(tag);
        chip.classList.add('active');
      }
      updateAdvancedUI();
      filterCatalogue();
    });
  });

  clearAdvancedBtn?.addEventListener('click', () => {
    activeAdvancedTags.clear();
    advChips.forEach((c) => {
      c.classList.remove('active');
    });
    updateAdvancedUI();
    filterCatalogue();
  });

  const filterCatalogue = () => {
    const rawQuery = searchInput?.value || '';
    const queryTokens = normalizeText(rawQuery).split(/\s+/).filter(Boolean);

    if (searchClear) {
      searchClear.hidden = rawQuery.length === 0;
    }

    let visibleCount = 0;

    cards.forEach((card) => {
      const title = normalizeText(card.dataset.title);
      const desc = normalizeText(card.dataset.description);
      const tags = normalizeText(card.dataset.tags);
      const ingredients = normalizeText(card.dataset.ingredients);

      const matchesTag =
        activeTag === 'all' || tags.includes(normalizeText(activeTag));
      const matchesAdvanced =
        activeAdvancedTags.size === 0 ||
        [...activeAdvancedTags].every((t) => tags.includes(normalizeText(t)));
      const fullText = `${title} ${desc} ${tags} ${ingredients}`;
      const matchesQuery =
        queryTokens.length === 0 ||
        queryTokens.every((token) => fullText.includes(token));

      const isVisible = matchesTag && matchesAdvanced && matchesQuery;
      card.style.display = isVisible ? '' : 'none';
      if (isVisible) visibleCount++;
    });

    if (countEl) {
      countEl.textContent = `${visibleCount} recette${visibleCount > 1 ? 's' : ''}`;
    }

    if (emptyState) {
      emptyState.hidden = visibleCount > 0;
    }
  };

  searchInput?.addEventListener('input', filterCatalogue);

  searchClear?.addEventListener('click', () => {
    if (searchInput) {
      searchInput.value = '';
      searchInput.focus();
      filterCatalogue();
    }
  });

  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      chips.forEach((c) => {
        c.classList.remove('active');
      });
      chip.classList.add('active');
      activeTag = chip.dataset.tag;
      filterCatalogue();
    });
  });

  resetSearchBtn?.addEventListener('click', () => {
    if (searchInput) searchInput.value = '';
    activeTag = 'all';
    chips.forEach((c) => {
      c.classList.toggle('active', c.dataset.tag === 'all');
    });
    activeAdvancedTags.clear();
    advChips.forEach((c) => {
      c.classList.remove('active');
    });
    updateAdvancedUI();
    filterCatalogue();
  });
};
