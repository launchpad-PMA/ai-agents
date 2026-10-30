import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { expectedAccessCode, readBearer, sessionSecret, signSession, verifySession } from "./auth.js";
import { handleUtterance } from "./orchestrator.js";
import { addMemory, getConversation, isMemoryEnabled, listAudit, listMemories, setMemoryEnabled } from "./memory.js";
import { executeTool, listTools } from "./tools.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(__dirname, "..", "public");
const PORT = Number(process.env.PORT || 8787);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".ico": "image/x-icon",
};

function send(res, code, body, headers = {}) {
  const payload = typeof body === "string" || Buffer.isBuffer(body) ? body : JSON.stringify(body);
  res.writeHead(code, {
    "Content-Type": typeof body === "string" ? "text/plain; charset=utf-8" : "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(payload);
}

function json(res, code, body) {
  send(res, code, body, { "Content-Type": "application/json; charset=utf-8" });
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
  } catch {
    return {};
  }
}

function requireAuth(req, res) {
  const session = verifySession(readBearer(req), sessionSecret());
  if (!session) {
    json(res, 401, { ok: false, error: "unauthorized" });
    return null;
  }
  return session;
}

async function createRealtimeSession() {
  const apiKey = (process.env.OPENAI_API_KEY || "").trim();
  if (!apiKey) {
    return {
      mode: "mock",
      model: "mock-jarvis",
      note: "OPENAI_API_KEY is not set. Using on-device speech plus mock tools. The key never leaves the server when present.",
    };
  }
  const response = await fetch("https://api.openai.com/v1/realtime/sessions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.OPENAI_REALTIME_MODEL || "gpt-4o-realtime-preview",
      voice: process.env.OPENAI_REALTIME_VOICE || "verse",
    }),
  });
  const data = await response.json();
  if (!response.ok) {
    return { mode: "mock", error: "openai_session_failed", status: response.status };
  }
  return { mode: "openai", session: data };
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath === "/") urlPath = "/index.html";
  const filePath = path.normalize(path.join(PUBLIC_DIR, urlPath));
  if (!filePath.startsWith(PUBLIC_DIR)) {
    json(res, 403, { ok: false, error: "forbidden" });
    return;
  }
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    json(res, 404, { ok: false, error: "not_found" });
    return;
  }
  const ext = path.extname(filePath);
  res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
  fs.createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);

    if (req.method === "GET" && url.pathname === "/api/health") {
      json(res, 200, {
        ok: true,
        service: "jarvis",
        mode: process.env.OPENAI_API_KEY ? "openai-ready" : "mock",
        authRequired: Boolean(expectedAccessCode()),
      });
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/login") {
      const body = await readBody(req);
      const expected = expectedAccessCode();
      if (expected && body.code !== expected) {
        json(res, 401, { ok: false, error: "invalid_code" });
        return;
      }
      const token = signSession(sessionSecret());
      json(res, 200, { ok: true, token, expiresInHours: 12 });
      return;
    }

    if (url.pathname.startsWith("/api/") && url.pathname !== "/api/login") {
      const session = requireAuth(req, res);
      if (!session) return;
      const sessionId = session.sub || "baba";

      if (req.method === "GET" && url.pathname === "/api/dashboard") {
        json(res, 200, {
          ok: true,
          tools: listTools(),
          memoryEnabled: isMemoryEnabled(sessionId),
          memories: listMemories(),
          history: getConversation(sessionId),
          audit: listAudit(),
          realtime: process.env.OPENAI_API_KEY ? "server-minted" : "mock",
        });
        return;
      }

      if (req.method === "POST" && url.pathname === "/api/chat") {
        const body = await readBody(req);
        const result = await handleUtterance({
          sessionId,
          text: body.text,
          confirm: Boolean(body.confirm),
        });
        json(res, 200, { ok: true, ...result, history: getConversation(sessionId) });
        return;
      }

      if (req.method === "POST" && url.pathname === "/api/transcribe") {
        const body = await readBody(req);
        json(res, 200, {
          ok: true,
          mode: "mock",
          text: body.hint || "Status of RSS3, Maxayauwi, and Aragamago.",
          note: "Mock transcription. Browser speech recognition is preferred on Galaxy Chrome.",
        });
        return;
      }

      if (req.method === "POST" && url.pathname === "/api/realtime/session") {
        const sessionPayload = await createRealtimeSession();
        json(res, 200, { ok: true, ...sessionPayload });
        return;
      }

      if (req.method === "POST" && url.pathname.startsWith("/api/tools/")) {
        const name = decodeURIComponent(url.pathname.replace("/api/tools/", ""));
        const body = await readBody(req);
        const result = await executeTool(name, {
          confirm: Boolean(body.confirm),
          input: body.input || "",
        });
        json(res, 200, result);
        return;
      }

      if (req.method === "POST" && url.pathname === "/api/memory") {
        const body = await readBody(req);
        if (typeof body.enabled === "boolean") {
          json(res, 200, { ok: true, memoryEnabled: setMemoryEnabled(sessionId, body.enabled) });
          return;
        }
        const item = addMemory(body.text || "", { pinned: Boolean(body.pinned) });
        json(res, 200, { ok: true, item, memories: listMemories() });
        return;
      }

      json(res, 404, { ok: false, error: "not_found" });
      return;
    }

    if (req.method === "GET") {
      serveStatic(req, res);
      return;
    }

    json(res, 405, { ok: false, error: "method_not_allowed" });
  } catch (error) {
    json(res, 500, { ok: false, error: "server_error", message: String(error.message || error) });
  }
});

if (process.env.JARVIS_NO_LISTEN !== "1") {
  server.listen(PORT, "0.0.0.0", () => {
    console.log(`JARVIS prototype listening on http://0.0.0.0:${PORT}`);
    console.log(`Mode: ${process.env.OPENAI_API_KEY ? "openai-ready" : "mock tools"}`);
  });
}

export { server };
