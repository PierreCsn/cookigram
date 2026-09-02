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
 * Controller class for an individual countdown timer element.
 */
export class RecipeTimer {
  constructor(element, onTimerComplete = null) {
    this.el = element;
    this.onTimerComplete = onTimerComplete;
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
  document.querySelectorAll('.timer').forEach((el) => {
    const timer = new RecipeTimer(el, onTimerComplete);
    activeTimers.push(timer);
  });
};
