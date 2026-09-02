/**
 * Recipe variant switching and URL parameter synchronization.
 */

export const initVariants = () => {
  const variantPicker = document.querySelector('.variant-picker');
  if (!variantPicker) return;

  const templates = [...document.querySelectorAll('template[data-variant]')];
  const cookGroups = [...document.querySelectorAll('[data-cook-variant]')];
  const validIds = new Set([
    ...templates.map((template) => template.dataset.variant),
    ...cookGroups.map((group) => group.dataset.cookVariant),
  ]);
  const params = new URLSearchParams(window.location.search);
  const requested = params.get('variant');
  const defaultId = variantPicker.dataset.defaultVariant;
  const selectedId = validIds.has(requested) ? requested : defaultId;

  if (requested && !validIds.has(requested)) {
    params.delete('variant');
    const query = params.toString();
    history.replaceState(
      null,
      '',
      `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`
    );
  }

  const template = templates.find((item) => item.dataset.variant === selectedId);
  if (template) {
    template.content.querySelectorAll('[data-fragment]').forEach((fragment) => {
      const target = document.querySelector(
        `[data-variant-target="${fragment.dataset.fragment}"]`
      );
      if (target) target.replaceChildren(...fragment.cloneNode(true).childNodes);
    });
  }
  cookGroups.forEach((group) => {
    group.hidden = group.dataset.cookVariant !== selectedId;
  });

  const select = variantPicker.querySelector('.variant-select');
  if (select) {
    select.value = selectedId;
    select.addEventListener('change', () => {
      const nextParams = new URLSearchParams(window.location.search);
      nextParams.set('variant', select.value);
      window.location.assign(
        `${window.location.pathname}?${nextParams}${window.location.hash}`
      );
    });
  }
  document.querySelector('.ingredient-list')?.setAttribute('data-variant', selectedId);
  const start = document.querySelector('.start-cooking');
  if (start) start.href = `cook/?variant=${encodeURIComponent(selectedId)}`;
  const cookPage = document.querySelector('.cook');
  if (cookPage) cookPage.dataset.variant = selectedId;
  const leave = document.querySelector('.leave-cook');
  if (leave) leave.href = `../?variant=${encodeURIComponent(selectedId)}`;
  document.documentElement.dataset.recipeVariant = selectedId;
};
