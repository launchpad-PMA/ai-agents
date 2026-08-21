# 🧭 gemini.md — Project Constitution

> This is **law**. All data schemas, behavioral rules, and architectural invariants live here.
> Only updated when a schema changes, a rule is added, or architecture is modified.

---

## Data Schemas

> _To be defined after Discovery answers are received._

### Input Schema
```json
{}
```

### Output Schema
```json
{}
```

---

## Behavioral Rules

> _To be defined after Discovery answers are received._

### Aragamago North Star
The main goal of this automation is to merge Antigravity with OpenClaw to create **Aragamago**—Baba John’s trusted AI helper and Sacred Library Guardian. Aragamago operates with a fiduciary duty of care, prioritizing security, privacy, and sacred integrity while optimizing for efficiency and profit. 
Key directives include:
- Zero-Trust Inputs and Execution Quarantine
- No handling of seed phrases, private keys, or signing txs (Watcher/Proposer only)
- Defense against prompt injection and malware
- Strict compartmentalization of the Sacred Library (Public/Draft/Restricted)

---

## Architectural Invariants

1. **Secrets live in env vars or `ENV_PATH`, never hardcoded and never committed.** Local default is Codex `master.env`; Windows Antigravity can set `ENV_PATH`.
2. **Aragamago** is Python in `agents/aragamago/` (root `Dockerfile` / `railway.toml`). **Maxayauwi** is Node in `rss3-comm-agent/`.
3. **No handling of seed phrases, private keys, or signing txs** (Watcher/Proposer only).
4. **All intermediate files go to `.tmp/`.**
5. **Do not treat `divine-cleric` as a separate GitHub repo** until one exists under `launchpad-PMA`.

---

## Maintenance Log

| Date | Change | Author |
|------|--------|--------|
| 2026-03-09 | Project initialized, constitution created | System Pilot |
| 2026-08-14 | Recorded two git lineages; secrets via `runtime_env` / `ENV_PATH` | Cursor |
