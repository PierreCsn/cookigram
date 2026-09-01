let installPrompt;
const installButton = document.querySelector('.install');
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event; if (installButton) installButton.hidden = false; });
installButton?.addEventListener('click', async () => { await installPrompt?.prompt(); installButton.hidden = true; });

if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register(`${document.body.dataset.prefix}sw.js`));

// --- Theme Management ---
const THEME_KEY = 'cookgram:theme';
const metaThemeColor = document.querySelector('meta[name="theme-color"]');

const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  const isDark = theme === 'dark';
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', isDark ? '#161514' : '#fff8ed');
  }
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.textContent = isDark ? '☀️' : '🌙';
    btn.setAttribute('aria-label', isDark ? 'Passer au thème clair' : 'Passer au thème sombre');
    btn.setAttribute('title', isDark ? 'Passer au thème clair' : 'Passer au thème sombre');
  });
};

const getInitialTheme = () => {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'dark' || saved === 'light') return saved;
  return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
};

let currentTheme = getInitialTheme();
applyTheme(currentTheme);

if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem(THEME_KEY)) {
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

document.querySelectorAll('.theme-toggle').forEach(btn => {
  btn.addEventListener('click', toggleTheme);
});

// --- Share Recipe ---
const showShareFeedback = (btn, text = '✓ Lien copié !') => {
  btn.classList.add('copied');
  const label = btn.querySelector('.share-label') || btn;
  const original = label.textContent;
  label.textContent = text;
  setTimeout(() => {
    btn.classList.remove('copied');
    label.textContent = original;
  }, 2000);
};

const shareRecipe = async (btn) => {
  const title = document.title || 'CookGram';
  const desc = document.querySelector('.recipe-heading p')?.textContent || 'Découvrez cette recette sur CookGram !';
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

document.querySelectorAll('.share-btn').forEach(btn => {
  btn.addEventListener('click', () => shareRecipe(btn));
});

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

// --- Web Audio & Sound synthesis ---
let audioCtx = null;
const getAudioContext = () => {
  try {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) audioCtx = new AudioContextClass();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  } catch (_) {
    return null;
  }
};

const playAlarmTone = (ctx, freq, startTime, duration = 0.22, gainVal = 0.3) => {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(freq, startTime);
  gain.gain.setValueAtTime(0.0001, startTime);
  gain.gain.exponentialRampToValueAtTime(gainVal, startTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(startTime);
  osc.stop(startTime + duration);
};

const playTimerChime = () => {
  const ctx = getAudioContext();
  if (!ctx) return;
  const t = ctx.currentTime;
  playAlarmTone(ctx, 784, t, 0.2, 0.25);
  playAlarmTone(ctx, 1046.5, t + 0.12, 0.2, 0.28);
  playAlarmTone(ctx, 1318.5, t + 0.24, 0.35, 0.3);

  playAlarmTone(ctx, 784, t + 0.55, 0.2, 0.25);
  playAlarmTone(ctx, 1046.5, t + 0.67, 0.2, 0.28);
  playAlarmTone(ctx, 1318.5, t + 0.79, 0.45, 0.3);
};

// --- Web Speech API ---
const formatSpeechText = (text) => {
  return text
    .replace(/\((\d+(?:[.,]\d+)?)\s*g\)/gi, '$1 grammes')
    .replace(/\((\d+(?:[.,]\d+)?)\s*kg\)/gi, '$1 kilogrammes')
    .replace(/\((\d+(?:[.,]\d+)?)\s*ml\)/gi, '$1 millilitres')
    .replace(/\((\d+(?:[.,]\d+)?)\s*cl\)/gi, '$1 centilitres')
    .replace(/\((\d+(?:[.,]\d+)?)\s*l\)/gi, '$1 litres')
    .replace(/\((\d+(?:[.,]\d+)?)\s*c\.?\s*à\s*s(?:oupe)?\.?\)/gi, '$1 cuillères à soupe')
    .replace(/\((\d+(?:[.,]\d+)?)\s*c\.?\s*à\s*c(?:afé)?\.?\)/gi, '$1 cuillères à café')
    .replace(/(\d+)\s*C\b/g, '$1 degrés')
    .replace(/(\d+)\s*min\b/gi, '$1 minutes')
    .replace(/(\d+)\s*s(?:ec)?\b/gi, '$1 secondes')
    .replace(/[#@^{}~]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
};

let isSpeaking = false;

const speak = (text, onEnd) => {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  isSpeaking = true;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'fr-FR';
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  const voices = window.speechSynthesis.getVoices();
  const frVoice = voices.find(v => v.lang && (v.lang.startsWith('fr') || v.lang.replace('_', '-').startsWith('fr')));
  if (frVoice) utterance.voice = frVoice;
  const finish = () => {
    isSpeaking = false;
    if (onEnd) onEnd();
  };
  utterance.onend = finish;
  utterance.onerror = finish;
  window.speechSynthesis.speak(utterance);
};

const stopSpeech = () => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  isSpeaking = false;
};

const playConfirmBeep = () => {
  const ctx = getAudioContext();
  if (!ctx) return;
  const t = ctx.currentTime;
  playAlarmTone(ctx, 880, t, 0.08, 0.2);
};

if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

class RecipeTimer {
  constructor(element) {
    this.el = element;
    this.totalSeconds = Number(element.dataset.seconds);
    this.remaining = this.totalSeconds;
    this.label = element.dataset.label || this.formatTime(this.totalSeconds);
    this.stepNum = element.dataset.stepNum || '1';

    this.statusEl = element.querySelector('.timer-status');
    this.displayEl = element.querySelector('.timer-display');
    this.toggleBtn = element.querySelector('.timer-toggle');
    this.toggleText = this.toggleBtn?.querySelector('i') || this.toggleBtn;
    this.resetBtn = element.querySelector('.timer-reset');

    this.intervalId = null;
    this.alarmLoopId = null;
    this.state = 'idle';

    this.init();
  }

  init() {
    this.toggleBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.handleToggle();
    });
    this.resetBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      this.reset();
    });
  }

  handleToggle() {
    getAudioContext();
    if (this.state === 'idle' || this.state === 'paused') {
      this.start();
    } else if (this.state === 'running') {
      this.pause();
    } else if (this.state === 'ringing') {
      this.stopAlarmAndReset();
    }
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
  }

  start() {
    this.state = 'running';
    this.el.classList.remove('paused', 'ringing');
    this.el.classList.add('running');
    if (this.statusEl) this.statusEl.textContent = 'En cours...';
    if (this.toggleText) this.toggleText.textContent = 'Pause ⏸';
    if (this.resetBtn) this.resetBtn.hidden = false;
    this.displayEl.textContent = this.formatTime(this.remaining);

    this.intervalId = setInterval(() => {
      this.remaining--;
      if (this.remaining <= 0) {
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.ring();
      } else {
        this.displayEl.textContent = this.formatTime(this.remaining);
      }
    }, 1000);
  }

  pause() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.state = 'paused';
    this.el.classList.remove('running');
    this.el.classList.add('paused');
    if (this.statusEl) this.statusEl.textContent = 'En pause';
    if (this.toggleText) this.toggleText.textContent = 'Reprendre ▶';
  }

  reset() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.stopAlarmOnly();
    this.state = 'idle';
    this.remaining = this.totalSeconds;
    this.el.classList.remove('running', 'paused', 'ringing');
    if (this.statusEl) this.statusEl.textContent = 'Minuteur';
    if (this.displayEl) this.displayEl.textContent = this.label;
    if (this.toggleText) this.toggleText.textContent = 'Démarrer';
    if (this.resetBtn) this.resetBtn.hidden = true;
  }

  ring() {
    this.state = 'ringing';
    this.el.classList.remove('running', 'paused');
    this.el.classList.add('ringing');
    if (this.statusEl) this.statusEl.textContent = 'Terminé !';
    if (this.displayEl) this.displayEl.textContent = '00:00';
    if (this.toggleText) this.toggleText.textContent = 'Arrêter ⏹';

    const playAlarmCycle = () => {
      playTimerChime();
      navigator.vibrate?.([300, 150, 300, 150, 600]);
    };

    playAlarmCycle();
    speak(`Minuteur de l'étape ${this.stepNum} terminé !`);

    let repeatCount = 0;
    this.alarmLoopId = setInterval(() => {
      repeatCount++;
      if (repeatCount >= 4) {
        this.stopAlarmOnly();
      } else {
        playAlarmCycle();
      }
    }, 2400);
  }

  stopAlarmOnly() {
    if (this.alarmLoopId) {
      clearInterval(this.alarmLoopId);
      this.alarmLoopId = null;
    }
    navigator.vibrate?.(0);
  }

  stopAlarmAndReset() {
    this.stopAlarmOnly();
    stopSpeech();
    this.reset();
  }
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

  const autoSpeakKey = 'cookgram:autospeak';
  const autoSpeakBtn = document.querySelector('.auto-speak');
  let autoSpeakEnabled = localStorage.getItem(autoSpeakKey) === 'true';
  if (autoSpeakBtn) {
    if (!('speechSynthesis' in window)) {
      autoSpeakBtn.hidden = true;
    } else {
      autoSpeakBtn.setAttribute('aria-pressed', String(autoSpeakEnabled));
      autoSpeakBtn.addEventListener('click', () => {
        getAudioContext();
        autoSpeakEnabled = !autoSpeakEnabled;
        autoSpeakBtn.setAttribute('aria-pressed', String(autoSpeakEnabled));
        localStorage.setItem(autoSpeakKey, String(autoSpeakEnabled));
        if (autoSpeakEnabled) {
          readActiveStep();
        } else {
          stopStepSpeaking();
        }
      });
    }
  }

  let activeSpeakingBtn = null;
  const stopStepSpeaking = () => {
    stopSpeech();
    if (activeSpeakingBtn) {
      activeSpeakingBtn.classList.remove('speaking');
      const label = activeSpeakingBtn.querySelector('.speak-label');
      const icon = activeSpeakingBtn.querySelector('.speak-icon');
      if (label) label.textContent = 'Écouter';
      if (icon) icon.textContent = '🔊';
      activeSpeakingBtn = null;
    }
  };

  const readActiveStep = () => {
    stopStepSpeaking();
    const activeStep = steps[current];
    if (!activeStep) return;
    const btn = activeStep.querySelector('.step-speak');
    const action = activeStep.querySelector('h1')?.textContent || '';
    const instruction = activeStep.querySelector('.instruction')?.textContent || '';
    const stepNum = current + 1;
    const textToSpeak = formatSpeechText(`Étape ${stepNum} sur ${steps.length}. ${action}. ${instruction}`);

    if (btn) {
      btn.classList.add('speaking');
      const label = btn.querySelector('.speak-label');
      const icon = btn.querySelector('.speak-icon');
      if (label) label.textContent = 'Arrêter';
      if (icon) icon.textContent = '⏹';
      activeSpeakingBtn = btn;
    }

    speak(textToSpeak, () => {
      if (btn && activeSpeakingBtn === btn) {
        btn.classList.remove('speaking');
        const label = btn.querySelector('.speak-label');
        const icon = btn.querySelector('.speak-icon');
        if (label) label.textContent = 'Écouter';
        if (icon) icon.textContent = '🔊';
        activeSpeakingBtn = null;
      }
    });
  };

  steps.forEach((step) => {
    const btn = step.querySelector('.step-speak');
    if (btn) {
      if (!('speechSynthesis' in window)) {
        btn.hidden = true;
      } else {
        btn.addEventListener('click', () => {
          getAudioContext();
          if (activeSpeakingBtn === btn) {
            stopStepSpeaking();
          } else {
            readActiveStep();
          }
        });
      }
    }
  });

  const timers = [...document.querySelectorAll('.timer')].map(el => new RecipeTimer(el));

  // --- Hands-Free Voice Control (Speech Recognition) ---
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const voiceCmdBtn = document.querySelector('.voice-cmd');
  const voiceFeedback = document.querySelector('.voice-feedback');
  const voiceFeedbackText = document.querySelector('.voice-feedback-text');
  let recognition = null;
  let voiceCmdActive = false;
  let feedbackTimeout = null;

  const defaultFeedbackHtml = 'Mains libres actif : dites <em>« Suivant »</em>, <em>« Précédent »</em>, <em>« Répéter »</em> ou <em>« Minuteur »</em>';

  const showVoiceFeedback = (message, isCommand = true) => {
    if (!voiceFeedback || !voiceFeedbackText) return;
    if (feedbackTimeout) clearTimeout(feedbackTimeout);
    voiceFeedbackText.innerHTML = message;
    if (isCommand) {
      voiceFeedback.classList.add('command-recognized');
      feedbackTimeout = setTimeout(() => {
        voiceFeedback.classList.remove('command-recognized');
        voiceFeedbackText.innerHTML = defaultFeedbackHtml;
      }, 1600);
    } else {
      voiceFeedback.classList.remove('command-recognized');
    }
  };

  const parseVoiceCommand = (rawText) => {
    const text = rawText.toLowerCase().trim();

    if (/\b(stop|arr[êe]t|arr[êe]te|tais-toi|silence|coupe|merci)\b/.test(text)) {
      return 'stop';
    }
    if (/\b(suivant|suivante|avanc|apr[èe]s|continuer|continues)\b/.test(text)) {
      return 'next';
    }
    if (/\b(pr[ée]c[ée]dent|pr[ée]c[ée]dente|retour|arri[èe]re|recul)\b/.test(text)) {
      return 'prev';
    }
    if (/\b(r[ée]p[èe]t|r[ée]p[èe]te|lis|lire|relis|relire|[ée]coute|[ée]couter|instruction)\b/.test(text)) {
      return 'repeat';
    }
    if (/\b(pause)\b/.test(text)) {
      return 'pause';
    }
    if (/\b(r[ée]initialis|reset|z[ée]ro)\b/.test(text)) {
      return 'reset';
    }
    if (/\b(minuteur|chrono|d[ée]marr|d[ée]marre|lanc|lance|top)\b/.test(text)) {
      return 'timer';
    }
    return null;
  };

  let lastCmdTime = 0;
  const executeVoiceCommand = (cmd) => {
    const now = Date.now();
    if (now - lastCmdTime < 700) return;
    lastCmdTime = now;
    playConfirmBeep();

    switch (cmd) {
      case 'next':
        showVoiceFeedback(`✓ Commande : <em>« Suivant »</em>`);
        document.querySelector('.next')?.click();
        break;
      case 'prev':
        showVoiceFeedback(`✓ Commande : <em>« Précédent »</em>`);
        document.querySelector('.prev')?.click();
        break;
      case 'repeat':
        showVoiceFeedback(`✓ Commande : <em>« Répéter »</em>`);
        readActiveStep();
        break;
      case 'timer': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer');
        if (timerEl) {
          showVoiceFeedback(`✓ Commande : <em>« Minuteur »</em>`);
          timerEl.querySelector('.timer-toggle')?.click();
        } else {
          showVoiceFeedback(`ℹ Aucun minuteur sur cette étape`);
        }
        break;
      }
      case 'pause': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer.running');
        if (timerEl) {
          showVoiceFeedback(`✓ Commande : <em>« Pause minuteur »</em>`);
          timerEl.querySelector('.timer-toggle')?.click();
        } else {
          showVoiceFeedback(`ℹ Aucun minuteur en cours`);
        }
        break;
      }
      case 'reset': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer');
        if (timerEl) {
          showVoiceFeedback(`✓ Commande : <em>« Réinitialiser »</em>`);
          timerEl.querySelector('.timer-reset')?.click();
        }
        break;
      }
      case 'stop':
        showVoiceFeedback(`✓ Commande : <em>« Arrêt »</em>`);
        stopStepSpeaking();
        timers.forEach(t => t.stopAlarmOnly());
        break;
    }
  };

  if (voiceCmdBtn) {
    if (!SpeechRecognition) {
      voiceCmdBtn.setAttribute('title', 'Reconnaissance vocale non disponible sur ce navigateur');
      voiceCmdBtn.disabled = true;
      voiceCmdBtn.style.opacity = '0.35';
    } else {
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      recognition.lang = 'fr-FR';

      recognition.onresult = (event) => {
        if (isSpeaking) return;
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const transcript = event.results[i][0].transcript;
          const cmd = parseVoiceCommand(transcript);
          if (cmd) {
            executeVoiceCommand(cmd);
            break;
          }
        }
      };

      recognition.onerror = (event) => {
        if (event.error === 'not-allowed') {
          voiceCmdActive = false;
          voiceCmdBtn.setAttribute('aria-pressed', 'false');
          if (voiceFeedback) voiceFeedback.hidden = true;
          alert("L'accès au microphone a été refusé. Veuillez l'autoriser pour utiliser la commande vocale mains libres.");
        }
      };

      recognition.onend = () => {
        if (voiceCmdActive) {
          try {
            recognition.start();
          } catch (_) {}
        }
      };

      voiceCmdBtn.addEventListener('click', () => {
        getAudioContext();
        voiceCmdActive = !voiceCmdActive;
        voiceCmdBtn.setAttribute('aria-pressed', String(voiceCmdActive));

        if (voiceCmdActive) {
          playConfirmBeep();
          if (voiceFeedback) {
            voiceFeedback.hidden = false;
            showVoiceFeedback(defaultFeedbackHtml, false);
          }
          try {
            recognition.start();
          } catch (_) {}
        } else {
          if (voiceFeedback) voiceFeedback.hidden = true;
          try {
            recognition.stop();
          } catch (_) {}
        }
      });
    }
  }

  const render = () => {
    stopStepSpeaking();
    steps.forEach((step, index) => step.classList.toggle('active', index === current));
    document.querySelector('.progress i').style.width = `${((current + 1) / steps.length) * 100}%`;
    document.querySelector('.prev').disabled = current === 0;
    document.querySelector('.next').textContent = current === steps.length - 1 ? 'Terminer ✓' : 'Suivant →';
    localStorage.setItem(key, current);
    if (autoSpeakEnabled) {
      readActiveStep();
    }
  };

  document.querySelector('.prev').addEventListener('click', () => {
    getAudioContext();
    if (current > 0) { current--; render(); }
  });
  document.querySelector('.next').addEventListener('click', () => {
    getAudioContext();
    if (current < steps.length - 1) {
      current++;
      render();
    } else {
      stopStepSpeaking();
      timers.forEach(t => t.stopAlarmOnly());
      if (voiceCmdActive && recognition) {
        voiceCmdActive = false;
        try { recognition.stop(); } catch (_) {}
      }
      localStorage.removeItem(key);
      location.href = '../';
    }
  });

  render();
}

let wakeLock;
document.querySelector('.wake')?.addEventListener('click', async event => {
  try {
    if (wakeLock) { await wakeLock.release(); wakeLock = null; }
    else wakeLock = await navigator.wakeLock.request('screen');
    event.currentTarget.setAttribute('aria-pressed', String(Boolean(wakeLock)));
  } catch (_) { event.currentTarget.title = 'Fonction non disponible sur ce navigateur'; }
});
