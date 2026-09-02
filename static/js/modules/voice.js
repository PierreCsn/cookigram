/**
 * Speech synthesis, hands-free voice recognition commands, and screen Wake Lock.
 */

import { getAudioContext, playAlarmTone } from './timers.js';
import { showToast } from './utils.js';

/**
 * Normalizes culinary abbreviations and symbols for natural text-to-speech pronunciation.
 *
 * @param {string} text
 * @returns {string}
 */
export const formatSpeechText = (text) => {
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

export let isSpeaking = false;
export const hasSpeechSynthesis =
  typeof window !== 'undefined' &&
  'speechSynthesis' in window &&
  Boolean(window.speechSynthesis);

let speechUnavailable = false;

export const markSpeechUnavailable = (notify) => {
  if (speechUnavailable) return;
  speechUnavailable = true;
  document
    .querySelectorAll('.step-speak, .auto-speak')
    .forEach((btn) => {
      btn.hidden = true;
    });
  if (notify) showToast('⚠️ Synthèse vocale indisponible sur cet appareil');
};

/**
 * Speaks text aloud in French using SpeechSynthesis.
 *
 * @param {string} text
 * @param {() => void} [onEnd]
 */
export const speak = (text, onEnd) => {
  if (!hasSpeechSynthesis) return;
  const start = () => {
    window.speechSynthesis.resume();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'fr-FR';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const frVoice = voices.find(
      (v) =>
        v.lang &&
        (v.lang.startsWith('fr') || v.lang.replace('_', '-').startsWith('fr'))
    );
    if (frVoice) utterance.voice = frVoice;
    const finish = () => {
      isSpeaking = false;
      if (onEnd) onEnd();
    };
    utterance.onend = finish;
    utterance.onerror = (errorEvent) => {
      const code = errorEvent?.error || '';
      if (code !== 'interrupted' && code !== 'canceled') {
        markSpeechUnavailable(true);
      }
      finish();
    };
    window.speechSynthesis.speak(utterance);
  };
  window.speechSynthesis.cancel();
  isSpeaking = true;
  setTimeout(start, 0);
};

export const stopSpeech = () => {
  if (hasSpeechSynthesis) {
    window.speechSynthesis.cancel();
  }
  isSpeaking = false;
};

export const playConfirmBeep = () => {
  const ctx = getAudioContext();
  if (!ctx) return;
  const t = ctx.currentTime;
  playAlarmTone(ctx, 880, t, 0.08, 0.2);
};

/**
 * Parses spoken text into an identified command token.
 *
 * @param {string} rawText
 * @returns {'stop' | 'next' | 'prev' | 'repeat' | 'pause' | 'reset' | 'timer' | 'check' | null}
 */
export const parseVoiceCommand = (rawText) => {
  const text = String(rawText || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

  if (/\b(stop|arret|arrete|tais-toi|silence|coupe|merci)\b/.test(text)) {
    return 'stop';
  }
  if (/\b(suivant|suivante|avanc|apres|continuer|continues)\b/.test(text)) {
    return 'next';
  }
  if (/\b(precedent|precedente|retour|arriere|recul)\b/.test(text)) {
    return 'prev';
  }
  if (
    /\b(repet|repete|lis|lire|relis|relire|ecoute|ecouter|instruction)\b/.test(
      text
    )
  ) {
    return 'repeat';
  }
  if (/\b(pause)\b/.test(text)) {
    return 'pause';
  }
  if (/\b(reinitialis|reset|zero)\b/.test(text)) {
    return 'reset';
  }
  if (/\b(minuteur|chrono|demarr|demarre|lanc|lance|top)\b/.test(text)) {
    return 'timer';
  }
  if (/\b(fait|faite|valide|validee|coche|cochee)\b/.test(text)) {
    return 'check';
  }
  return null;
};


/**
 * Initializes speech synthesis voice watching and screen Wake Lock.
 */
export const initVoice = () => {
  if (hasSpeechSynthesis) {
    const watchSpeechVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      if (voices.length > 0) {
        if (speechUnavailable) {
          speechUnavailable = false;
          document
            .querySelectorAll('.step-speak, .auto-speak')
            .forEach((btn) => {
              btn.hidden = false;
            });
        }
        return;
      }
      if (!speechUnavailable) {
        setTimeout(() => {
          if (window.speechSynthesis.getVoices().length === 0) {
            markSpeechUnavailable(false);
          }
        }, 2000);
      }
    };
    window.speechSynthesis.onvoiceschanged = watchSpeechVoices;
    watchSpeechVoices();
  }

  // Wake Lock button
  let wakeLock = null;
  document.querySelector('.wake')?.addEventListener('click', async (event) => {
    const btn = event.currentTarget;
    try {
      if (wakeLock) {
        await wakeLock.release();
        wakeLock = null;
      } else {
        wakeLock = await navigator.wakeLock.request('screen');
      }
      btn?.setAttribute('aria-pressed', String(Boolean(wakeLock)));
    } catch (_) {
      if (btn) btn.title = 'Fonction non disponible sur ce navigateur';
    }
  });
};
