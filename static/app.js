let installPrompt;
const installButton = document.querySelector('.install');
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event; if (installButton) installButton.hidden = false; });
installButton?.addEventListener('click', async () => { await installPrompt?.prompt(); installButton.hidden = true; });

if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register(`${document.body.dataset.prefix}sw.js`));

const cook = document.querySelector('.cook');
if (cook) {
  const steps = [...document.querySelectorAll('.cook-step')];
  const key = `cookgram:${cook.dataset.recipe}:step`;
  let current = Math.min(Number(localStorage.getItem(key) || 0), steps.length - 1);
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
