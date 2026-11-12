/**
 * Approved content package for Max.
 *
 * Hermes drafts. Baba approves. Max publishes. This file does not post.
 * The only destination Max's code can publish to is Farcaster, via
 * POST /api/farcaster/cast with { message }. YouTube is a live announcement
 * of a stream that already exists, not a place to upload a draft.
 */

const FARCASTER = "farcaster";

function preparePublication(pkg) {
  const approvalId = String(pkg?.approval_id || "").trim();
  const text = String(pkg?.text || "").trim();
  const destinations = Array.isArray(pkg?.destinations) ? pkg.destinations : [];
  if (!approvalId) {
    return { ok: false, error: "approval_id is required" };
  }
  if (!text) {
    return { ok: false, error: "text is required" };
  }
  if (destinations.length === 0) {
    return { ok: false, error: "at least one destination is required" };
  }
  const unknown = destinations.filter((name) => name !== FARCASTER);
  if (unknown.length > 0) {
    return {
      ok: false,
      error: "Max cannot publish to " + unknown.join(", "),
      supported: [FARCASTER],
    };
  }
  return {
    ok: true,
    request: {
      method: "POST",
      path: "/api/farcaster/cast",
      body: { message: text },
    },
    receipt: {
      approval_id: approvalId,
      destination: FARCASTER,
      status: "ready",
      scheduled_at: pkg.scheduled_at || null,
      media: Array.isArray(pkg.media) ? pkg.media : [],
      cast_hash: null,
      url: null,
    },
  };
}

function receiptFromCast(approvalId, cast) {
  const hash = cast?.cast?.hash || cast?.hash || null;
  return {
    approval_id: approvalId,
    destination: FARCASTER,
    status: hash ? "published" : "unconfirmed",
    cast_hash: hash,
    url: null,
  };
}

module.exports = { preparePublication, receiptFromCast, FARCASTER };
