/**
 * Web Audio sound synthesis and interactive cooking timers.
 */

let audioCtx = null;

/**
 * Returns or resumes the shared AudioContext.
 *
 * @returns {AudioContext | null}
 */
export const getAudioContext = () => {
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

/**
 * Synthesizes an alarm tone with exponential ramp.
 *
 * @param {AudioContext} ctx
 * @param {number} freq
 * @param {number} startTime
 * @param {number} duration
 * @param {number} gainVal
 */
export const playAlarmTone = (
  ctx,
  freq,
  startTime,
  duration = 0.22,
  gainVal = 0.3
) => {
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

/**
 * Plays a pleasant 3-note chime pattern twice.
 */
export const playTimerChime = () => {
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

/**
 * Calculates a countdown from an absolute wall-clock deadline.
 *
 * @param {number} targetTimestamp
 * @param {number} [now=Date.now()]
 * @returns {number}
 */
export const getRemainingSeconds = (targetTimestamp, now = Date.now()) =>
  Math.max(0, Math.round((Number(targetTimestamp) - now) / 1000));

/**
 * Controller class for an individual countdown timer element.
 */
export class RecipeTimer {
  constructor(element, onTimerComplete = null, onTimerUpdate = null) {
    this.el = element;
    this.onTimerComplete = onTimerComplete;
    this.onTimerUpdate = onTimerUpdate;
    this.totalSeconds = Number(element.dataset.seconds);
    this.remaining = this.totalSeconds;
    this.label = element.dataset.label || this.formatTime(this.totalSeconds);
    this.stepNum = element.dataset.stepNum || '1';
    this.recipeSlug = element.closest('.cook')?.dataset.recipe || '';
    this.timerId = element.dataset.timerId || `${this.stepNum}:${this.label}`;
    this.storageKey = this.recipeSlug
      ? `cookigram:timer:${this.recipeSlug}:${this.timerId}`
      : '';

    this.statusEl = element.querySelector('.timer-status');
    this.displayEl = element.querySelector('.timer-display');
    this.toggleBtn = element.querySelector('.timer-toggle');
    this.toggleText = this.toggleBtn?.querySelector('i') || this.toggleBtn;
    this.resetBtn = element.querySelector('.timer-reset');

    this.intervalId = null;
    this.alarmLoopId = null;
    this.state = 'idle';

    this.restore();
    this.init();
  }

  notifyUpdate() {
    if (typeof this.onTimerUpdate === 'function') this.onTimerUpdate(this);
  }

  persist() {
    if (!this.storageKey) return;
    localStorage.setItem(this.storageKey, JSON.stringify({
      step: Number(this.el.dataset.step || 0),
      label: this.label,
      duration: this.totalSeconds,
      remaining: this.remaining,
      targetTimestamp: this.targetTimestamp || null,
      status: this.state,
    }));
  }

  clearPersisted() {
    if (this.storageKey) localStorage.removeItem(this.storageKey);
  }

  restore() {
    if (!this.storageKey) return;
    let saved;
    try {
      saved = JSON.parse(localStorage.getItem(this.storageKey) || '');
    } catch (_) {
      return;
    }
    if (!saved || saved.duration !== this.totalSeconds) return;
    this.remaining = Math.max(0, Number(saved.remaining) || 0);
    this.targetTimestamp = Number(saved.targetTimestamp) || null;
    if (saved.status === 'running' && this.targetTimestamp) {
      this.state = this.targetTimestamp <= Date.now() ? 'ringing' : 'running';
      if (this.state === 'ringing') {
        queueMicrotask(() => this.ring());
      } else {
        this.el.classList.add('running');
        this.statusEl.textContent = 'En cours...';
        this.toggleText.textContent = 'Pause ⏸';
        this.resetBtn.hidden = false;
        this.displayEl.textContent = this.formatTime(this.remaining);
        this.scheduleTick();
      }
    } else if (saved.status === 'paused') {
      this.state = 'paused';
      this.el.classList.add('paused');
      this.statusEl.textContent = 'En pause';
      this.toggleText.textContent = 'Reprendre ▶';
      this.resetBtn.hidden = false;
      this.displayEl.textContent = this.formatTime(this.remaining);
    }
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
    const mins = Math.floor(seconds / 60)
      .toString()
      .padStart(2, '0');
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
    this.targetTimestamp = Date.now() + this.remaining * 1000;
    this.persist();
    this.displayEl.textContent = this.formatTime(this.remaining);
    this.notifyUpdate();
    this.scheduleTick();
  }

  scheduleTick() {
    if (this.intervalId) clearInterval(this.intervalId);
    this.intervalId = setInterval(() => {
      this.remaining = getRemainingSeconds(this.targetTimestamp);
      if (this.remaining <= 0) {
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.ring();
      } else {
        this.displayEl.textContent = this.formatTime(this.remaining);
        this.persist();
        this.notifyUpdate();
      }
    }, 1000);
  }

  pause() {
    if (this.targetTimestamp) {
      this.remaining = getRemainingSeconds(this.targetTimestamp);
    }
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.state = 'paused';
    this.el.classList.remove('running');
    this.el.classList.add('paused');
    if (this.statusEl) this.statusEl.textContent = 'En pause';
    if (this.toggleText) this.toggleText.textContent = 'Reprendre ▶';
    this.targetTimestamp = null;
    this.persist();
    this.notifyUpdate();
  }

  reset() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.stopAlarmOnly();
    this.state = 'idle';
    this.remaining = this.totalSeconds;
    this.targetTimestamp = null;
    this.el.classList.remove('running', 'paused', 'ringing');
    if (this.statusEl) this.statusEl.textContent = 'Minuteur';
    if (this.displayEl) this.displayEl.textContent = this.label;
    if (this.toggleText) this.toggleText.textContent = 'Démarrer';
    if (this.resetBtn) this.resetBtn.hidden = true;
    this.clearPersisted();
    this.notifyUpdate();
  }

  ring() {
    this.state = 'ringing';
    this.el.classList.remove('running', 'paused');
    this.el.classList.add('ringing');
    if (this.statusEl) this.statusEl.textContent = 'Terminé !';
    if (this.displayEl) this.displayEl.textContent = '00:00';
    if (this.toggleText) this.toggleText.textContent = 'Arrêter ⏹';
    this.targetTimestamp = null;
    this.persist();
    this.notifyUpdate();

    const playAlarmCycle = () => {
      playTimerChime();
      navigator.vibrate?.([300, 150, 300, 150, 600]);
    };

    playAlarmCycle();
    if (typeof this.onTimerComplete === 'function') {
      this.onTimerComplete(this.stepNum);
    }

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
    this.reset();
  }
}

export const activeTimers = [];

/**
 * Initializes all timer widgets in the page.
 *
 * @param {(stepNum: string) => void} [onTimerComplete]
 */
export const initTimers = (onTimerComplete = null) => {
  if (document.querySelector('.cook')) return;
  document.querySelectorAll('.timer').forEach((el) => {
    const timer = new RecipeTimer(el, onTimerComplete);
    activeTimers.push(timer);
  });
};
