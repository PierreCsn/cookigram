/**
 * Guided Cook Mode wizard: steps navigation, keyboard controls,
 * substeps checklist, and hands-free voice command execution.
 */

import { scaleText } from './portions.js';
import { RecipeTimer, getAudioContext } from './timers.js';
import {
  formatSpeechText,
  hasSpeechSynthesis,
  isSpeaking,
  parseVoiceCommand,
  playConfirmBeep,
  speak,
  stopSpeech,
} from './voice.js';

export const initSubsteps = () => {
  const cook = document.querySelector('.cook');
  if (!cook) return;
  const steps = [...document.querySelectorAll('.cook-steps:not([hidden]) .cook-step')];

  const updateSubstepsProgress = (stepEl) => {
    const card = stepEl.querySelector('.substeps-card');
    if (!card) return;
    const items = [...card.querySelectorAll('.substep-item')];
    const checkedCount = items.filter((it) => it.classList.contains('checked')).length;
    const progressEl = card.querySelector('.substeps-progress');
    if (progressEl) {
      const total = items.length;
      progressEl.textContent = `${checkedCount} / ${total}${checkedCount === total && total > 0 ? ' ✓' : ''}`;
      progressEl.classList.toggle('all-done', checkedCount === total && total > 0);
    }
  };

  steps.forEach((stepEl) => {
    const card = stepEl.querySelector('.substeps-card');
    if (!card) return;
    const stepId = stepEl.dataset.stepId;
    const storageKey = `cookigram:${cook.dataset.recipe}:substeps:${stepId}`;

    let saved = [];
    try {
      saved = JSON.parse(
        localStorage.getItem(storageKey) || '[]'
      );
    } catch (_) {}
    const savedSet = new Set(saved);

    const items = card.querySelectorAll('.substep-item');
    items.forEach((item, idx) => {
      const cb = item.querySelector('.substep-checkbox');
      const isChecked = savedSet.has(idx);
      if (cb) cb.checked = isChecked;
      item.classList.toggle('checked', isChecked);

      cb?.addEventListener('change', () => {
        item.classList.toggle('checked', cb.checked);
        const currentCheckboxes = [...card.querySelectorAll('.substep-checkbox')];
        const newSaved = currentCheckboxes
          .map((c, i) => (c.checked ? i : null))
          .filter((v) => v !== null);
        localStorage.setItem(storageKey, JSON.stringify(newSaved));
        updateSubstepsProgress(stepEl);
      });
    });

    updateSubstepsProgress(stepEl);
  });

  steps.forEach((stepEl) => {
    const stepId = stepEl.dataset.stepId;
    stepEl.querySelectorAll('.parallel-operation').forEach((operation) => {
      const storageKey = `cookigram:${cook.dataset.recipe}:parallel:${stepId}:${operation.dataset.operationId}`;
      const checkbox = operation.querySelector('.parallel-checkbox');
      const checked = localStorage.getItem(storageKey) === 'true';
      if (checkbox) checkbox.checked = checked;
      operation.classList.toggle('checked', checked);
      checkbox?.addEventListener('change', () => {
        operation.classList.toggle('checked', checkbox.checked);
        localStorage.setItem(storageKey, String(checkbox.checked));
      });
    });
  });
};

export const initCookMode = () => {
  const cook = document.querySelector('.cook');
  if (!cook) return;

  const steps = [...document.querySelectorAll('.cook-steps:not([hidden]) .cook-step')];
  const key = `cookigram:${cook.dataset.recipe}:step-id`;
  const savedStepId = localStorage.getItem(key);
  const matchedStep = savedStepId
    ? steps.findIndex((step) => step.dataset.stepId === savedStepId)
    : -1;
  let current = matchedStep >= 0 ? matchedStep : 0;

  if (cook.dataset.scalable === 'true') {
    const basePortions = Number(cook.dataset.basePortions);
    const portions = Number(
      localStorage.getItem(`cookigram:${cook.dataset.recipe}:portions`) ||
        basePortions
    );
    const factor = portions / basePortions;
    const portionsDisplay = document.querySelector('.cook-portions');
    if (portionsDisplay) {
      portionsDisplay.textContent = `${portions} portion${portions > 1 ? 's' : ''}`;
    }
    document.querySelectorAll('[data-scale-text]').forEach((node) => {
      node.textContent = scaleText(node.dataset.scaleText, factor);
    });
  }

  const autoSpeakKey = 'cookigram:autospeak';
  const autoSpeakBtn = document.querySelector('.auto-speak');
  let autoSpeakEnabled = localStorage.getItem(autoSpeakKey) === 'true';

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
    const substepsTexts = [
      ...activeStep.querySelectorAll('.substep-text'),
    ].map((el) => el.textContent.trim());
    const stepNum = current + 1;

    const speechParts = [`Étape ${stepNum} sur ${steps.length}. ${action}.`];
    if (instruction) speechParts.push(instruction);
    if (substepsTexts.length > 0) {
      speechParts.push(substepsTexts.join('. '));
    }
    const textToSpeak = formatSpeechText(speechParts.join(' '));

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

  if (autoSpeakBtn) {
    if (!hasSpeechSynthesis) {
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

  steps.forEach((step) => {
    const btn = step.querySelector('.step-speak');
    if (btn) {
      if (!hasSpeechSynthesis) {
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

  const timers = [
    ...document.querySelectorAll('.cook-steps:not([hidden]) .timer'),
  ].map((el) => new RecipeTimer(el));

  // --- Speech Recognition ---
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  const voiceCmdBtn = document.querySelector('.voice-cmd');
  const voiceFeedback = document.querySelector('.voice-feedback');
  const voiceFeedbackText = document.querySelector('.voice-feedback-text');
  let recognition = null;
  let voiceCmdActive = false;
  let feedbackTimeout = null;

  const defaultFeedbackHtml =
    'Mains libres actif : dites <em>« Suivant »</em>, <em>« Précédent »</em>, <em>« Répéter »</em> ou <em>« Minuteur »</em>';

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

  let lastCmdTime = 0;
  const executeVoiceCommand = (cmd) => {
    const now = Date.now();
    if (now - lastCmdTime < 700) return;
    lastCmdTime = now;
    playConfirmBeep();

    switch (cmd) {
      case 'next':
        showVoiceFeedback('✓ Commande : <em>« Suivant »</em>');
        document.querySelector('.next')?.click();
        break;
      case 'prev':
        showVoiceFeedback('✓ Commande : <em>« Précédent »</em>');
        document.querySelector('.prev')?.click();
        break;
      case 'repeat':
        showVoiceFeedback('✓ Commande : <em>« Répéter »</em>');
        readActiveStep();
        break;
      case 'check': {
        const activeStep = steps[current];
        const nextUnchecked = activeStep?.querySelector(
          '.substep-item:not(.checked) .substep-checkbox'
        );
        if (nextUnchecked) {
          nextUnchecked.checked = true;
          nextUnchecked.dispatchEvent(new Event('change'));
          showVoiceFeedback('✓ Sous-étape validée');
        } else {
          showVoiceFeedback('ℹ Toutes les sous-étapes sont validées');
        }
        break;
      }
      case 'timer': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer');
        if (timerEl) {
          showVoiceFeedback('✓ Commande : <em>« Minuteur »</em>');
          timerEl.querySelector('.timer-toggle')?.click();
        } else {
          showVoiceFeedback('ℹ Aucun minuteur sur cette étape');
        }
        break;
      }
      case 'pause': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer.running');
        if (timerEl) {
          showVoiceFeedback('✓ Commande : <em>« Pause minuteur »</em>');
          timerEl.querySelector('.timer-toggle')?.click();
        } else {
          showVoiceFeedback('ℹ Aucun minuteur en cours');
        }
        break;
      }
      case 'reset': {
        const activeStep = steps[current];
        const timerEl = activeStep?.querySelector('.timer');
        if (timerEl) {
          showVoiceFeedback('✓ Commande : <em>« Réinitialiser »</em>');
          timerEl.querySelector('.timer-reset')?.click();
        }
        break;
      }
      case 'stop':
        showVoiceFeedback('✓ Commande : <em>« Arrêt »</em>');
        stopStepSpeaking();
        timers.forEach((t) => {
          t.stopAlarmOnly();
        });
        break;
    }
  };

  if (voiceCmdBtn) {
    if (!SpeechRecognition) {
      voiceCmdBtn.setAttribute(
        'title',
        'Reconnaissance vocale non disponible sur ce navigateur'
      );
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
          alert(
            "L'accès au microphone a été refusé. Veuillez l'autoriser pour utiliser la commande vocale mains libres."
          );
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
    steps.forEach((step, index) => {
      step.classList.toggle('active', index === current);
    });
    const progressEl = document.querySelector('.progress i');
    if (progressEl) {
      progressEl.style.width = `${((current + 1) / steps.length) * 100}%`;
    }
    const prevBtn = document.querySelector('.prev');
    if (prevBtn) prevBtn.disabled = current === 0;
    const nextBtn = document.querySelector('.next');
    if (nextBtn) {
      nextBtn.textContent =
        current === steps.length - 1 ? 'Terminer ✓' : 'Suivant →';
    }
    localStorage.setItem(key, steps[current]?.dataset.stepId || '');
    if (autoSpeakEnabled) {
      readActiveStep();
    }
  };

  document.querySelector('.prev')?.addEventListener('click', () => {
    getAudioContext();
    if (current > 0) {
      current--;
      render();
    }
  });

  document.querySelector('.next')?.addEventListener('click', () => {
    getAudioContext();
    if (current < steps.length - 1) {
      current++;
      render();
    } else {
      stopStepSpeaking();
      timers.forEach((t) => {
        t.stopAlarmOnly();
      });
      if (voiceCmdActive && recognition) {
        voiceCmdActive = false;
        try {
          recognition.stop();
        } catch (_) {}
      }
      localStorage.removeItem(key);
      location.href = '../';
    }
  });

  // Keyboard navigation (ArrowLeft / ArrowRight)
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowRight') {
      document.querySelector('.next')?.click();
    } else if (e.key === 'ArrowLeft') {
      document.querySelector('.prev')?.click();
    }
  });

  render();
};
