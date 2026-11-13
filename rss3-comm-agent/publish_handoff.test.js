const test = require("node:test");
const assert = require("node:assert/strict");
const { preparePublication, receiptFromCast } = require("./publish_handoff");

test("an approved package becomes one Farcaster cast", () => {
  const result = preparePublication({
    approval_id: "appr-1",
    text: "The hall is open.",
    destinations: ["farcaster"],
    media: ["nas://clips/hall.mp4"],
    scheduled_at: "2026-11-12T15:00:00-06:00",
  });
  assert.equal(result.ok, true);
  assert.deepEqual(result.request, {
    method: "POST",
    path: "/api/farcaster/cast",
    body: { message: "The hall is open." },
  });
  assert.equal(result.receipt.status, "ready");
  assert.equal(result.receipt.approval_id, "appr-1");
  assert.equal(result.receipt.url, null);
});

test("Max refuses a destination he cannot post to", () => {
  const result = preparePublication({
    approval_id: "appr-2",
    text: "Hello",
    destinations: ["x"],
  });
  assert.equal(result.ok, false);
  assert.match(result.error, /cannot publish to x/);
});

test("YouTube is not a draft destination", () => {
  const result = preparePublication({
    approval_id: "appr-3",
    text: "Watch this",
    destinations: ["youtube"],
  });
  assert.equal(result.ok, false);
});

test("a cast without Baba's approval id is refused", () => {
  const result = preparePublication({
    text: "Hello",
    destinations: ["farcaster"],
  });
  assert.equal(result.ok, false);
});

test("a Neynar hash becomes a receipt and does not invent a url", () => {
  const receipt = receiptFromCast("appr-1", { cast: { hash: "0xabc" } });
  assert.equal(receipt.status, "published");
  assert.equal(receipt.cast_hash, "0xabc");
  assert.equal(receipt.url, null);
});
