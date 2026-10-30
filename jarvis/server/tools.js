/**
 * Typed tool catalog. Phase 1 uses mock adapters only.
 * Sensitive tools require explicit confirmation before they are marked approved.
 */

export const RISK = {
  read: "read",
  draft: "draft",
  privileged: "privileged",
};

export const TOOLS = [
  {
    name: "rss3.status",
    title: "RSS3 Node #97",
    risk: RISK.read,
    description: "Query RSS3 node discovery, indexing, and operator readiness.",
  },
  {
    name: "maxayauwi.health",
    title: "Maxayauwi",
    risk: RISK.read,
    description: "Ping the RSS3 comm agent health endpoints.",
  },
  {
    name: "aragamago.status",
    title: "Aragamago",
    risk: RISK.read,
    description: "Report Telegram bot deployment diagnosis without starting polling.",
  },
  {
    name: "railway.health",
    title: "Railway",
    risk: RISK.read,
    description: "Summarize known Railway host status from last public probes.",
  },
  {
    name: "linode.health",
    title: "Linode",
    risk: RISK.read,
    description: "Report RSS3 node host reachability.",
  },
  {
    name: "supabase.status",
    title: "Supabase",
    risk: RISK.read,
    description: "Check whether database credentials are configured (never return secrets).",
  },
  {
    name: "social.draft",
    title: "Social draft",
    risk: RISK.draft,
    description: "Prepare a Farcaster/Telegram post for approval. Does not publish.",
  },
  {
    name: "agents.delegate",
    title: "Delegate task",
    risk: RISK.privileged,
    description: "Queue work for Maxayauwi or Aragamago. Requires explicit authorization.",
  },
];

const MOCK_SNAPSHOT = {
  "rss3.status": {
    ok: false,
    source: "mock",
    node: 97,
    globalIndexing: "blocked",
    discovery: "unverified",
    giDns: "failed from this environment",
    linode: "web3.adbongo.io:8080 unreachable",
    note: "Live probe from Cloud Agent: gi.rss3.io did not resolve; Linode port 8080 refused.",
  },
  "maxayauwi.health": {
    ok: false,
    source: "mock",
    publicUrl: "https://rss3-comm-agent-production.up.railway.app",
    lastProbe: "HTTP 502 Application failed to respond",
    recommendation: "Inspect Railway logs for rss3-comm-agent-production. Do not redeploy without approval.",
  },
  "aragamago.status": {
    ok: false,
    source: "mock",
    publicUrl: "https://ai-agents-production-b0ef.up.railway.app",
    lastProbe: "HTTP 404 Application not found",
    polling: "code uses getUpdates; 409 conflict documented if two replicas poll",
    recommendation: "Repair in-repo bot, add /health, restore one Railway service after approval.",
  },
  "railway.health": {
    ok: false,
    source: "mock",
    services: [
      { name: "Maxayauwi", url: "rss3-comm-agent-production", status: "502" },
      { name: "Aragamago", url: "ai-agents-production-b0ef", status: "404" },
    ],
    dashboardAccess: "Railway MCP not signed in from this Cloud Agent; no deploy performed.",
  },
  "linode.health": {
    ok: false,
    source: "mock",
    host: "web3.adbongo.io",
    port: 8080,
    lastProbe: "connection refused",
  },
  "supabase.status": {
    ok: false,
    source: "mock",
    configured: Boolean(process.env.SUPABASE_URL),
    secretsPresent: false,
    note: "Prototype never prints keys. Connector exists in connectors/supabase_connector.py.",
  },
};

export function listTools() {
  return TOOLS.map(({ name, title, risk, description }) => ({
    name,
    title,
    risk,
    description,
  }));
}

export function getTool(name) {
  return TOOLS.find((tool) => tool.name === name) || null;
}

export async function executeTool(name, { confirm = false, input = "" } = {}) {
  const tool = getTool(name);
  if (!tool) {
    return { ok: false, error: "unknown_tool", name };
  }

  if (tool.risk === RISK.privileged && !confirm) {
    return {
      ok: false,
      pendingAuthorization: true,
      name,
      message: `${tool.title} is privileged. Say authorize ${tool.name} to run it.`,
    };
  }

  if (name === "social.draft") {
    const topic = String(input || "RSS3 Node 97 recovery").slice(0, 240);
    return {
      ok: true,
      name,
      risk: tool.risk,
      published: false,
      draft: {
        channel: "farcaster",
        text: `Baba, draft only — not posted.\n\nNode 97 watch: ${topic}. Maxayauwi health is 502; Aragamago Railway host is 404. No production changes until you approve.`,
      },
    };
  }

  if (name === "agents.delegate") {
    return {
      ok: true,
      name,
      risk: tool.risk,
      delegated: false,
      queued: {
        agent: String(input || "maxayauwi").slice(0, 40),
        status: "queued-for-approval-execution",
        note: "Mock queue only. Nothing was sent to Railway, Telegram, or Linode.",
      },
    };
  }

  return {
    ok: true,
    name,
    risk: tool.risk,
    result: MOCK_SNAPSHOT[name] || { ok: true, source: "mock" },
  };
}

export function toolsForPrompt() {
  return TOOLS.map((tool) => `${tool.name} (${tool.risk}): ${tool.description}`).join("\n");
}
