"use strict";

/**
 * Review's gauge. It recommends a lane. It does not publish.
 * Max decides what is marketing, a perk, or a sale.
 *
 * marketing: a free official app. The name and the link can be public.
 * perk: our teaching. Membership first.
 * sale: the same teaching, only if the publisher chooses to sell it.
 * hold: secrets, house files, another teacher's prices, or an app we do not own.
 */

const SECRET = /api[_-]?key|secret|token|password|credential|private key/i;
const HOUSE = /ARAGAMAGO_ARCHIVE|TELEGRAM_BOT_TOKEN|approval_id|pinecone/i;

function gaugeSection(section) {
  const id = section?.id || "";
  const text = JSON.stringify(section || {});
  const holds = [];
  if (section?.secrets || SECRET.test(text)) holds.push("secrets");
  if (section?.house_files || HOUSE.test(text)) holds.push("house files");
  if (section?.other_teachers_prices) holds.push("another teacher's prices");
  if (section?.resell_app) holds.push("a free app is not ours to sell");
  if (holds.length > 0) {
    return { id, lane: "hold", holds, sale_ok: false, reasons: holds };
  }
  if (section?.kind === "app" && section.free === true && section.url) {
    return {
      id,
      lane: "marketing",
      holds: [],
      sale_ok: false,
      reasons: [
        "Official free download. The name and the link can be public. The app is not a product we sell.",
      ],
    };
  }
  if (section?.kind === "teaching") {
    return {
      id,
      lane: "perk",
      holds: [],
      sale_ok: true,
      reasons: [
        "This is our teaching.",
        "Recommend it as a membership perk. The publisher may also sell the same teaching to people who are not members.",
      ],
    };
  }
  return {
    id,
    lane: "hold",
    holds: ["unknown kind"],
    sale_ok: false,
    reasons: ["Review cannot classify this."],
  };
}

function gaugeGuide(guide) {
  const sections = (guide?.sections || []).map(gaugeSection);
  const held = sections.filter((section) => section.lane === "hold");
  const base = {
    id: guide?.id || "",
    publisher_decides: true,
    publishes: false,
    sections,
  };
  if (held.length > 0) {
    return {
      ...base,
      recommended: "hold",
      also: [],
      split: { marketing: [], perk: [], sale: [], hold: held.map((section) => section.id) },
      reasons: ["A section is held. The guide stays in the room until that section is removed."],
    };
  }
  const perk = sections.some((section) => section.lane === "perk");
  return {
    ...base,
    recommended: perk ? "perk" : "marketing",
    also: perk ? ["marketing", "sale"] : [],
    split: {
      marketing: sections.filter((section) => section.lane === "marketing").map((section) => section.id),
      perk: sections.filter((section) => section.lane === "perk").map((section) => section.id),
      sale: sections.filter((section) => section.sale_ok).map((section) => section.id),
      hold: [],
    },
    reasons: perk
      ? [
          "The free apps can be named in public. We do not sell those apps.",
          "The illustrated order and the model settings are the perk for members in good standing.",
          "The same teaching can be sold to non-members if the publisher chooses. Review only recommends.",
          "The gauge does not publish. A cast still needs Baba's approval.",
        ]
      : ["Names and official links only. Nothing here is ours to sell."],
  };
}

module.exports = { gaugeSection, gaugeGuide };
