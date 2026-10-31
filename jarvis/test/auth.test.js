import test from "node:test";
import assert from "node:assert/strict";
import { signSession, verifySession } from "../server/auth.js";

test("session round-trip", () => {
  const token = signSession("secret", "baba");
  const session = verifySession(token, "secret");
  assert.equal(session.sub, "baba");
});

test("rejects bad signature", () => {
  const token = signSession("secret", "baba");
  assert.equal(verifySession(token, "other"), null);
});
