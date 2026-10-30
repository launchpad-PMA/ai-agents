import test from "node:test";
import assert from "node:assert/strict";
import { detectTools, handleUtterance } from "../server/orchestrator.js";
import { executeTool } from "../server/tools.js";

test("detects infrastructure tools from natural speech", () => {
  const names = detectTools("JARVIS, what is the RSS3 node 97 and Maxayauwi status?");
  assert.ok(names.includes("rss3.status"));
  assert.ok(names.includes("maxayauwi.health"));
});

test("privileged tools require authorization", async () => {
  const denied = await executeTool("agents.delegate", { confirm: false });
  assert.equal(denied.pendingAuthorization, true);
  const allowed = await executeTool("agents.delegate", { confirm: true, input: "maxayauwi" });
  assert.equal(allowed.ok, true);
  assert.equal(allowed.queued.status.includes("queued"), true);
});

test("social draft never claims it published", async () => {
  const draft = await executeTool("social.draft", { input: "node recovery" });
  assert.equal(draft.published, false);
});

test("utterance returns spoken mock reply", async () => {
  const result = await handleUtterance({ sessionId: "test", text: "Check Railway health" });
  assert.match(result.reply, /mock tools/i);
  assert.equal(result.tools[0].name, "railway.health");
});
