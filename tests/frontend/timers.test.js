import assert from "node:assert/strict";
import test, { describe } from "node:test";

import { getRemainingSeconds } from "../../static/js/modules/timers.js";

describe("Cooking timer persistence (#78)", () => {
  test("computes remaining seconds from an absolute deadline", () => {
    assert.equal(getRemainingSeconds(120_000, 60_000), 60);
    assert.equal(getRemainingSeconds(60_000, 60_001), 0);
    assert.equal(getRemainingSeconds(60_000, 59_499), 1);
  });

  test("never returns a negative value for an expired timer", () => {
    assert.equal(getRemainingSeconds(0, 10_000), 0);
  });
});
