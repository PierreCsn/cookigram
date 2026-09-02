/**
 * Theme management, PWA installation, and Service Worker registration.
 */

export const THEME_KEY = 'cookigram:theme';
export const OLD_THEME_KEY = 'cookgram:theme';

/**
 * Applies the given theme ('dark' or 'light') to the document.
 *
 * @param {'dark' | 'light'} theme
 */
export const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  const isDark = theme === 'dark';
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', isDark ? '#161514' : '#fff8ed');
  }
  document.querySelectorAll('.theme-toggle').forEach((btn) => {
    btn.textContent = isDark ? '☀️' : '🌙';
    btn.setAttribute('aria-label', isDark ? 'Passer au thème clair' : 'Passer au thème sombre');
    btn.setAttribute('title', isDark ? 'Passer au thème clair' : 'Passer au thème sombre');
  });
};

/**
 * Determines the initial theme based on localStorage and OS preference.
 *
 * @returns {'dark' | 'light'}
 */
export const getInitialTheme = () => {
  const saved = localStorage.getItem(THEME_KEY) || localStorage.getItem(OLD_THEME_KEY);
  if (saved === 'dark' || saved === 'light') return saved;
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

/**
 * Initializes theme toggle listeners and system preference watchers.
 */
export const initTheme = () => {
  let currentTheme = getInitialTheme();
  applyTheme(currentTheme);

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(THEME_KEY) && !localStorage.getItem(OLD_THEME_KEY)) {
        currentTheme = e.matches ? 'dark' : 'light';
        applyTheme(currentTheme);
      }
    });
  }

  const toggleTheme = () => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, currentTheme);
    applyTheme(currentTheme);
  };

  document.querySelectorAll('.theme-toggle').forEach((btn) => {
    btn.addEventListener('click', toggleTheme);
  });
};

/**
 * Initializes PWA beforeinstallprompt handler and install button.
 */
export const initPwaInstall = () => {
  let installPrompt = null;
  const installButton = document.querySelector('.install');

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    installPrompt = event;
    if (installButton) installButton.hidden = false;
  });

  installButton?.addEventListener('click', async () => {
    await installPrompt?.prompt();
    installButton.hidden = true;
  });
};

/**
 * Registers the service worker with the site prefix.
 *
 * @param {string} prefix
 */
export const initServiceWorker = (prefix = '') => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register(`${prefix}sw.js`);
    });
  }
};
