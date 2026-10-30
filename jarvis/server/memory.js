const conversations = new Map();
const memories = [];
const audit = [];

const MAX_TURNS = 40;

export function getConversation(sessionId) {
  if (!conversations.has(sessionId)) conversations.set(sessionId, []);
  return conversations.get(sessionId);
}

export function appendTurn(sessionId, turn) {
  const history = getConversation(sessionId);
  history.push({ ...turn, at: new Date().toISOString() });
  if (history.length > MAX_TURNS) history.splice(0, history.length - MAX_TURNS);
  return history;
}

export function listMemories() {
  return memories.slice(-50);
}

export function addMemory(text, { pinned = false } = {}) {
  const item = {
    id: `mem_${Date.now().toString(36)}`,
    text: String(text || "").slice(0, 2000),
    pinned: Boolean(pinned),
    at: new Date().toISOString(),
  };
  memories.push(item);
  return item;
}

export function setMemoryEnabled(sessionId, enabled) {
  const flagKey = `flag:${sessionId}`;
  conversations.set(flagKey, { memoryEnabled: Boolean(enabled) });
  return Boolean(enabled);
}

export function isMemoryEnabled(sessionId) {
  const flag = conversations.get(`flag:${sessionId}`);
  if (!flag) return true;
  return flag.memoryEnabled !== false;
}

export function recordAudit(entry) {
  audit.push({ ...entry, at: new Date().toISOString() });
  if (audit.length > 200) audit.splice(0, audit.length - 200);
  return entry;
}

export function listAudit() {
  return audit.slice(-100);
}
