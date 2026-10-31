import test from "node:test";
import assert from "node:assert/strict";
import { once } from "node:events";

process.env.JARVIS_NO_LISTEN = "1";
process.env.JARVIS_ACCESS_CODE = "test-code";
process.env.JARVIS_SESSION_SECRET = "test-secret";

const { server } = await import("../server/index.js");

function listen() {
  server.listen(0, "127.0.0.1");
  return once(server, "listening").then(() => server.address().port);
}

async function httpJson(port, path, { method = "GET", token, body } = {}) {
  const res = await fetch(`http://127.0.0.1:${port}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return { status: res.status, data: await res.json() };
}

test("health, auth, chat, and dashboard", async (t) => {
  const port = await listen();
  t.after(() => server.close());

  const health = await httpJson(port, "/api/health");
  assert.equal(health.status, 200);
  assert.equal(health.data.service, "jarvis");

  const denied = await httpJson(port, "/api/dashboard");
  assert.equal(denied.status, 401);

  const badLogin = await httpJson(port, "/api/login", { method: "POST", body: { code: "nope" } });
  assert.equal(badLogin.status, 401);

  const login = await httpJson(port, "/api/login", { method: "POST", body: { code: "test-code" } });
  assert.equal(login.status, 200);
  const token = login.data.token;

  const chat = await httpJson(port, "/api/chat", {
    method: "POST",
    token,
    body: { text: "Aragamago status" },
  });
  assert.equal(chat.status, 200);
  assert.match(chat.data.reply, /Aragamago|mock/i);

  const dash = await httpJson(port, "/api/dashboard", { token });
  assert.equal(dash.status, 200);
  assert.ok(dash.data.tools.length >= 8);

  const page = await fetch(`http://127.0.0.1:${port}/`);
  assert.equal(page.status, 200);
  const html = await page.text();
  assert.match(html, /Hold to talk/);
});
