import crypto from "node:crypto";

const SESSION_TTL_MS = 12 * 60 * 60 * 1000;

export function expectedAccessCode() {
  return (process.env.JARVIS_ACCESS_CODE || "").trim();
}

export function signSession(secret, subject = "baba") {
  const issuedAt = Date.now();
  const payload = Buffer.from(JSON.stringify({ sub: subject, iat: issuedAt })).toString("base64url");
  const sig = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  return `${payload}.${sig}`;
}

export function verifySession(token, secret) {
  if (!token || !secret) return null;
  const [payload, sig] = String(token).split(".");
  if (!payload || !sig) return null;
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const data = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    if (Date.now() - Number(data.iat || 0) > SESSION_TTL_MS) return null;
    return data;
  } catch {
    return null;
  }
}

export function sessionSecret() {
  return (
    process.env.JARVIS_SESSION_SECRET ||
    process.env.JARVIS_ACCESS_CODE ||
    "jarvis-dev-only-not-for-production"
  );
}

export function readBearer(req) {
  const header = req.headers.authorization || "";
  if (header.startsWith("Bearer ")) return header.slice(7).trim();
  const cookie = req.headers.cookie || "";
  const match = cookie.match(/(?:^|; )jarvis_session=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}
