import { executeTool, getTool, toolsForPrompt } from "./tools.js";
import { addMemory, appendTurn, isMemoryEnabled, listMemories, recordAudit } from "./memory.js";

const TOOL_ALIASES = [
  { pattern: /\b(rss3|node 97|node #97)\b/i, name: "rss3.status" },
  { pattern: /\bmaxayauwi\b/i, name: "maxayauwi.health" },
  { pattern: /\baragamago\b/i, name: "aragamago.status" },
  { pattern: /\brailway\b/i, name: "railway.health" },
  { pattern: /\blinode\b/i, name: "linode.health" },
  { pattern: /\bsupabase\b/i, name: "supabase.status" },
  { pattern: /\b(draft|farcaster|cast|post)\b/i, name: "social.draft" },
  { pattern: /\b(delegate|assign|tell (max|the bot))\b/i, name: "agents.delegate" },
];

export function detectTools(text) {
  const found = [];
  for (const alias of TOOL_ALIASES) {
    if (alias.pattern.test(text) && !found.includes(alias.name)) found.push(alias.name);
  }
  if (/\bstatus\b|\bdashboard\b|\bhealth\b/i.test(text) && found.length === 0) {
    found.push("rss3.status", "maxayauwi.health", "aragamago.status", "railway.health");
  }
  return found;
}

export function wantsAuthorization(text) {
  return /\b(authorize|approved|do it|execute|confirm)\b/i.test(text);
}

function speakable(result) {
  if (!result) return "No result.";
  if (result.pendingAuthorization) return result.message;
  if (result.draft) return `Draft ready, not published. ${result.draft.text}`;
  if (result.queued) return `Queued for ${result.queued.agent}. Nothing was sent.`;
  if (result.result?.lastProbe) return `${result.name}: ${result.result.lastProbe}`;
  if (result.result?.note) return `${result.name}: ${result.result.note}`;
  return `${result.name} complete.`;
}

export async function handleUtterance({ sessionId, text, confirm = false }) {
  const utterance = String(text || "").trim();
  if (!utterance) {
    return { reply: "I am listening.", tools: [], spoken: "I am listening." };
  }

  if (/^remember\b/i.test(utterance)) {
    const item = addMemory(utterance.replace(/^remember\s*/i, ""));
    appendTurn(sessionId, { role: "user", text: utterance });
    const reply = `Stored memory ${item.id}.`;
    appendTurn(sessionId, { role: "assistant", text: reply });
    return { reply, spoken: reply, tools: [] };
  }

  const names = detectTools(utterance);
  const authorized = confirm || wantsAuthorization(utterance);
  const toolRuns = [];
  for (const name of names) {
    const spec = getTool(name);
    const run = await executeTool(name, {
      confirm: authorized,
      input: utterance,
    });
    toolRuns.push(run);
    recordAudit({
      type: "tool",
      name,
      risk: spec?.risk,
      authorized,
      ok: run.ok,
      pendingAuthorization: Boolean(run.pendingAuthorization),
    });
  }

  let reply;
  if (toolRuns.length) {
    const lines = toolRuns.map((run) => speakable(run));
    reply = `JARVIS mock tools.\n\n${lines.join("\n")}\n\nNo production systems were changed.`;
  } else {
    const memoryBlurb =
      isMemoryEnabled(sessionId) && listMemories().length
        ? ` I currently hold ${listMemories().length} memory note(s).`
        : "";
    reply = `I heard: "${utterance}". This prototype uses mock tools until you approve live credentials.${memoryBlurb} Try: RSS3 status, Maxayauwi, Aragamago, Railway, draft a cast, or remember this.`;
  }

  appendTurn(sessionId, { role: "user", text: utterance });
  appendTurn(sessionId, { role: "assistant", text: reply, tools: names });
  return {
    reply,
    spoken: reply.replace(/\n+/g, " "),
    tools: toolRuns,
    catalogHint: names.length ? undefined : toolsForPrompt(),
  };
}
