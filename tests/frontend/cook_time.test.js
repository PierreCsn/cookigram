import assert from "node:assert/strict";
import test, { describe } from "node:test";

import {
  calculateRemainingTimes,
  formatRemainingSpeech,
  formatRemainingTime,
} from "../../static/js/modules/cook.js";

describe("Cook Mode Remaining Time Helpers (#67)", () => {
  describe("calculateRemainingTimes", () => {
    test("calculates weighted remaining times with total recipe minutes and step timers", () => {
      // 7 steps: step 0 has 15m (900s), step 5 has 15m (900s), others manual.
      // total = 50m. timers = 30m. manual pool = 20m / 5 steps = 4m each.
      // step durations: [15, 4, 4, 4, 4, 15, 4].
      const steps = [
        { timerSeconds: 900 },
        { timerSeconds: 0 },
        { timerSeconds: 0 },
        { timerSeconds: 0 },
        { timerSeconds: 0 },
        { timerSeconds: 900 },
        { timerSeconds: 0 },
      ];
      const remaining = calculateRemainingTimes(steps, 50);
      assert.deepStrictEqual(remaining, [50, 35, 31, 27, 23, 19, 4]);
    });

    test("handles recipes where all steps are manual with total time", () => {
      // 4 steps, 20m total -> 5m each
      const steps = [
        { timerSeconds: 0 },
        { timerSeconds: 0 },
        { timerSeconds: 0 },
        { timerSeconds: 0 },
      ];
      const remaining = calculateRemainingTimes(steps, 20);
      assert.deepStrictEqual(remaining, [20, 15, 10, 5]);
    });

    test("falls back to step timers when total recipe time is missing", () => {
      const steps = [
        { timerSeconds: 600 }, // 10m
        { timerSeconds: 0 },   // fallback 2m
        { timerSeconds: 300 }, // 5m
      ];
      const remaining = calculateRemainingTimes(steps, null);
      assert.deepStrictEqual(remaining, [17, 7, 5]);
    });

    test("returns empty array when no duration is available", () => {
      const steps = [{ timerSeconds: 0 }, { timerSeconds: 0 }];
      const remaining = calculateRemainingTimes(steps, null);
      assert.deepStrictEqual(remaining, []);
      assert.deepStrictEqual(calculateRemainingTimes([], 50), []);
      assert.deepStrictEqual(calculateRemainingTimes(null, 50), []);
    });
  });

  describe("formatRemainingTime", () => {
    test("formats minutes under an hour", () => {
      assert.strictEqual(formatRemainingTime(45), "⏱ ~45 min");
      assert.strictEqual(formatRemainingTime(5), "⏱ ~5 min");
      assert.strictEqual(formatRemainingTime(1), "⏱ ~1 min");
    });

    test("formats hours and minutes", () => {
      assert.strictEqual(formatRemainingTime(60), "⏱ ~1 h");
      assert.strictEqual(formatRemainingTime(90), "⏱ ~1 h 30");
      assert.strictEqual(formatRemainingTime(65), "⏱ ~1 h 05");
      assert.strictEqual(formatRemainingTime(135), "⏱ ~2 h 15");
    });

    test("formats the last step compactly", () => {
      assert.strictEqual(formatRemainingTime(4, true), "⏱ ~4 min");
      assert.strictEqual(formatRemainingTime(1, true), "⏱ ~1 min");
    });

    test("handles edge cases gracefully", () => {
      assert.strictEqual(formatRemainingTime(0), "");
      assert.strictEqual(formatRemainingTime(-5), "");
      assert.strictEqual(formatRemainingTime(null), "");
      assert.strictEqual(formatRemainingTime(undefined), "");
    });
  });

  describe("formatRemainingSpeech", () => {
    test("formats spoken message for hands-free cooking", () => {
      assert.strictEqual(formatRemainingSpeech(35, false), "Environ 35 minutes restantes.");
      assert.strictEqual(formatRemainingSpeech(1, false), "Environ 1 minute restante.");
      assert.strictEqual(formatRemainingSpeech(60, false), "Environ 1 heure restante.");
      assert.strictEqual(formatRemainingSpeech(75, false), "Environ 1 heure et 15 minutes restantes.");
      assert.strictEqual(formatRemainingSpeech(4, true), "Dernière étape, environ 4 minutes restantes.");
    });
  });
});
