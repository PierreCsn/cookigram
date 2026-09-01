let installPrompt;
const installButton = document.querySelector('.install');
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event; if (installButton) installButton.hidden = false; });
installButton?.addEventListener('click', async () => { await installPrompt?.prompt(); installButton.hidden = true; });

if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register(`${document.body.dataset.prefix}sw.js`));

const formatScaled = value => {
  const rounded = Math.round(value * 100) / 100;
  return Number.isInteger(rounded) ? String(rounded) : String(rounded).replace('.', ',');
};

const scaleQuantity = (source, factor) => source.replace(/^(\s*)(\d+(?:[.,]\d+)?)/, (_, space, number) => `${space}${formatScaled(Number(number.replace(',', '.')) * factor)}`);
const scaleText = (source, factor) => source.replace(/\((\d+(?:[.,]\d+)?)\s*([^)]*)\)/g, (_, number, suffix) => `(${formatScaled(Number(number.replace(',', '.')) * factor)}${suffix ? ` ${suffix.trim()}` : ''})`);

const portionPicker = document.querySelector('.portion-picker');
if (portionPicker) {
  const base = Number(portionPicker.dataset.basePortions);
  const min = Number(portionPicker.dataset.min);
  const max = Number(portionPicker.dataset.max);
  const step = Number(portionPicker.dataset.step);
  const storageKey = `cookgram:${portionPicker.dataset.recipe}:portions`;
  let portions = Math.min(max, Math.max(min, Number(localStorage.getItem(storageKey) || base)));
  const renderPortions = () => {
    const factor = portions / base;
    portionPicker.querySelector('output').textContent = portions;
    document.querySelector('.portion-summary').textContent = `${portions} portion${portions > 1 ? 's' : ''}`;
    document.querySelectorAll('[data-scale-quantity]').forEach(node => node.textContent = scaleQuantity(node.dataset.scaleQuantity, factor));
    document.querySelectorAll('[data-scale-text]').forEach(node => node.textContent = scaleText(node.dataset.scaleText, factor));
    portionPicker.querySelector('[data-change="-1"]').disabled = portions <= min;
    portionPicker.querySelector('[data-change="1"]').disabled = portions >= max;
    localStorage.setItem(storageKey, portions);
  };
  portionPicker.querySelectorAll('[data-change]').forEach(button => button.addEventListener('click', () => {
    portions = Math.min(max, Math.max(min, portions + Number(button.dataset.change) * step));
    renderPortions();
  }));
  renderPortions();
}

const cook = document.querySelector('.cook');
if (cook) {
  const steps = [...document.querySelectorAll('.cook-step')];
  const key = `cookgram:${cook.dataset.recipe}:step`;
  let current = Math.min(Number(localStorage.getItem(key) || 0), steps.length - 1);
  if (cook.dataset.scalable === 'true') {
    const basePortions = Number(cook.dataset.basePortions);
    const portions = Number(localStorage.getItem(`cookgram:${cook.dataset.recipe}:portions`) || basePortions);
    const factor = portions / basePortions;
    document.querySelector('.cook-portions').textContent = `${portions} portion${portions > 1 ? 's' : ''}`;
    document.querySelectorAll('[data-scale-text]').forEach(node => node.textContent = scaleText(node.dataset.scaleText, factor));
  }
  const render = () => {
    steps.forEach((step, index) => step.classList.toggle('active', index === current));
    document.querySelector('.progress i').style.width = `${((current + 1) / steps.length) * 100}%`;
    document.querySelector('.prev').disabled = current === 0;
    document.querySelector('.next').textContent = current === steps.length - 1 ? 'Terminer ✓' : 'Suivant →';
    localStorage.setItem(key, current);
  };
  document.querySelector('.prev').addEventListener('click', () => { if (current) { current--; render(); } });
  document.querySelector('.next').addEventListener('click', () => { if (current < steps.length - 1) { current++; render(); } else { localStorage.removeItem(key); location.href = '../'; } });
  document.querySelectorAll('.timer').forEach(button => button.addEventListener('click', () => startTimer(button)));
  render();
}

function startTimer(button) {
  if (button.dataset.running) return;
  button.dataset.running = 'true';
  let remaining = Number(button.dataset.seconds);
  const label = button.querySelector('strong');
  const original = label.textContent;
  const tick = () => {
    const minutes = Math.floor(remaining / 60).toString().padStart(2, '0');
    const seconds = (remaining % 60).toString().padStart(2, '0');
    label.textContent = `${minutes}:${seconds}`;
    if (remaining-- > 0) return setTimeout(tick, 1000);
    label.textContent = 'Terminé !'; button.classList.add('done'); button.dataset.running = '';
    navigator.vibrate?.([200, 100, 200]);
    setTimeout(() => { label.textContent = original; button.classList.remove('done'); }, 5000);
  };
  tick();
}

let wakeLock;
document.querySelector('.wake')?.addEventListener('click', async event => {
  try {
    if (wakeLock) { await wakeLock.release(); wakeLock = null; }
    else wakeLock = await navigator.wakeLock.request('screen');
    event.currentTarget.setAttribute('aria-pressed', String(Boolean(wakeLock)));
  } catch (_) { event.currentTarget.title = 'Fonction non disponible sur ce navigateur'; }
});
