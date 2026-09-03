import assert from 'node:assert/strict';
import test, { describe } from 'node:test';

import { normalizeText, parseDurationMinutes } from '../../static/js/modules/search.js';
import {
  formatSpeechText,
  parseVoiceCommand,
} from '../../static/js/modules/voice.js';

describe('Frontend Pure Helper Unit Tests', () => {
  describe('normalizeText (Search & Filtering)', () => {
    test('removes accents, converts to lowercase and trims', () => {
      assert.strictEqual(normalizeText('Échalote'), 'echalote');
      assert.strictEqual(normalizeText('PÂTES'), 'pates');
      assert.strictEqual(normalizeText('  Coupé en morceaux  '), 'coupe en morceaux');
      assert.strictEqual(normalizeText(''), '');
      assert.strictEqual(normalizeText(null), '');
    });
  });

  describe('parseDurationMinutes (Duration Parsing)', () => {
    test('parses minute-only strings', () => {
      assert.strictEqual(parseDurationMinutes('35 min'), 35);
      assert.strictEqual(parseDurationMinutes('10 min'), 10);
      assert.strictEqual(parseDurationMinutes('45min'), 45);
    });

    test('parses hour-only strings', () => {
      assert.strictEqual(parseDurationMinutes('1 h'), 60);
      assert.strictEqual(parseDurationMinutes('2 h'), 120);
    });

    test('parses combined hours and minutes', () => {
      assert.strictEqual(parseDurationMinutes('1 h 10 min'), 70);
      assert.strictEqual(parseDurationMinutes('1 h 30 min'), 90);
    });

    test('handles empty or invalid duration tokens gracefully', () => {
      assert.strictEqual(parseDurationMinutes(''), null);
      assert.strictEqual(parseDurationMinutes(null), null);
      assert.strictEqual(parseDurationMinutes(undefined), null);
      assert.strictEqual(parseDurationMinutes('inconnu'), null);
    });
  });

  describe('formatSpeechText (Voice Synthesis Text Normalizer)', () => {
    test('expands mass and volume abbreviations in parentheses to full words', () => {
      assert.strictEqual(
        formatSpeechText("Ajouter du beurre (50 g) et de l'eau (200 ml)"),
        "Ajouter du beurre 50 grammes et de l'eau 200 millilitres"
      );
      assert.strictEqual(
        formatSpeechText('Verser la crème (20 cl)'),
        'Verser la crème 20 centilitres'
      );
    });

    test('expands spoons and units', () => {
      assert.strictEqual(
        formatSpeechText("Huile (2 c. à soupe) et sel (1 c. à café)"),
        "Huile 2 cuillères à soupe et sel 1 cuillères à café"
      );
    });

    test('replaces temperatures and time units', () => {
      assert.strictEqual(
        formatSpeechText('Cuire à 180 C pendant 25 min et 30 s'),
        'Cuire à 180 degrés pendant 25 minutes et 30 secondes'
      );
    });
  });

  describe('parseVoiceCommand (Speech Recognition Command Parser)', () => {
    test('recognizes navigation keywords', () => {
      assert.strictEqual(parseVoiceCommand('étape suivante'), 'next');
      assert.strictEqual(parseVoiceCommand('continuer'), 'next');
      assert.strictEqual(parseVoiceCommand('précédent s’il vous plaît'), 'prev');
      assert.strictEqual(parseVoiceCommand('retour en arrière'), 'prev');
    });

    test('recognizes repeat / listen commands', () => {
      assert.strictEqual(parseVoiceCommand('répète'), 'repeat');
      assert.strictEqual(parseVoiceCommand('relire l’instruction'), 'repeat');
    });

    test('recognizes timer and validation commands', () => {
      assert.strictEqual(parseVoiceCommand('lance le minuteur'), 'timer');
      assert.strictEqual(parseVoiceCommand('c’est fait'), 'check');
      assert.strictEqual(parseVoiceCommand('validé'), 'check');
    });

    test('recognizes stop and pause commands', () => {
      assert.strictEqual(parseVoiceCommand('stop'), 'stop');
      assert.strictEqual(parseVoiceCommand('silence'), 'stop');
      assert.strictEqual(parseVoiceCommand('pause'), 'pause');
    });

    test('returns null for unrelated phrases', () => {
      assert.strictEqual(parseVoiceCommand('bonjour comment ça va'), null);
      assert.strictEqual(parseVoiceCommand(''), null);
    });
  });
});
