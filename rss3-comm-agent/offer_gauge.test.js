const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { gaugeGuide, gaugeSection } = require("./offer_gauge");
const { SOVEREIGN_GUIDE } = require("./sovereign_guide");

const draft = path.join(__dirname, "drafts", "sovereign-first-downloads");

test("the house guide is a perk, and the free apps are not for sale", () => {
  const result = gaugeGuide(SOVEREIGN_GUIDE);
  assert.equal(result.recommended, "perk");
  assert.equal(result.publisher_decides, true);
  assert.equal(result.publishes, false);
  assert.deepEqual(result.also, ["marketing", "sale"]);
  assert.deepEqual(result.split.marketing, ["mint", "ollama", "obsidian"]);
  assert.deepEqual(result.split.perk, ["models", "stay-home"]);
  assert.deepEqual(result.split.sale, ["models", "stay-home"]);
  assert.deepEqual(result.split.hold, []);
  for (const id of ["mint", "ollama", "obsidian"]) {
    const section = result.sections.find((item) => item.id === id);
    assert.equal(section.lane, "marketing");
    assert.equal(section.sale_ok, false);
  }
});

test("secrets, house files, and another teacher's prices are held", () => {
  assert.equal(gaugeSection({ id: "leak", kind: "teaching", note: "TELEGRAM_BOT_TOKEN=abc" }).lane, "hold");
  assert.equal(gaugeSection({ id: "prices", kind: "app", free: true, url: "https://example.com", other_teachers_prices: true }).lane, "hold");
  assert.equal(gaugeSection({ id: "resale", kind: "app", free: true, url: "https://ollama.com", resell_app: true }).lane, "hold");
  const held = gaugeGuide({
    id: "bad",
    sections: [{ id: "mint", kind: "app", free: true, url: "https://linuxmint.com", secrets: true }],
  });
  assert.equal(held.recommended, "hold");
  assert.equal(held.publishes, false);
  assert.deepEqual(held.split.hold, ["mint"]);
});

test("the handout matches the catalog and is not a public page", () => {
  const html = fs.readFileSync(path.join(draft, "guide.html"), "utf8");
  const offer = fs.readFileSync(path.join(draft, "OFFER.md"), "utf8");
  assert.equal(html.includes("/public/"), false);
  for (const section of SOVEREIGN_GUIDE.sections) {
    assert.match(html, new RegExp(section.title));
  }
  for (const model of SOVEREIGN_GUIDE.sections.find((section) => section.id === "models").models) {
    assert.match(html, new RegExp(model.replace(".", "\\.")));
  }
  for (const banned of ["TELEGRAM_BOT_TOKEN", "ARAGAMAGO_ARCHIVE", "approval_id", "$9,000", "freedomfarmers"]) {
    assert.equal(html.includes(banned), false, banned);
  }
  assert.match(html, /linuxmint\.com/);
  assert.match(html, /ollama\.com\/download/);
  assert.match(html, /obsidian\.md/);
  assert.match(offer, /perk/);
  assert.match(offer, /does not publish/);
  assert.match(offer, /Max/);
  for (const name of ["sovereign-cover.jpg", "sovereign-mint.jpg", "sovereign-ollama.jpg", "sovereign-models.jpg", "sovereign-notes.jpg"]) {
    assert.match(html, new RegExp(name));
    assert.equal(fs.existsSync(path.join(draft, "assets", name)), true);
  }
});
