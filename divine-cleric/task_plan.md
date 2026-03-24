# 📋 B.L.A.S.T. Task Plan

## Status: 🟡 Awaiting Discovery Answers

---

## Protocol 0: Initialization
- [x] Create project directory structure
- [x] Initialize `task_plan.md`
- [x] Initialize `findings.md`
- [x] Initialize `progress.md`
- [x] Initialize `gemini.md` (Project Constitution)
- [ ] Discovery Questions answered by user

## Phase 1: B — Blueprint (Vision & Logic)
- [ ] North Star defined
- [ ] Integrations identified & keys confirmed
- [ ] Source of Truth established
- [ ] Delivery Payload specified
- [ ] Behavioral Rules documented
- [ ] JSON Data Schema defined in `gemini.md`
- [ ] Research completed (GitHub repos, resources)
- [ ] Blueprint approved by user

## Phase 2: L — Link (Connectivity)
- [ ] API connections tested
- [ ] `.env` credentials verified
- [ ] Handshake scripts built & passing

## Phase 3: A — Architect (3-Layer Build)
- [ ] Architecture SOPs written (`architecture/`)
- [ ] Navigation logic designed
- [ ] Tools built (`tools/`)
- [ ] All tools tested

## Phase 4: S — Stylize (Refinement & UI)
- [ ] Payload formatted for delivery
- [ ] UI/UX applied (if applicable)
- [ ] User feedback collected

## Phase 5: T — Trigger (Deployment)
- [ ] Cloud transfer complete
- [ ] Automation triggers configured
- [ ] Maintenance log finalized in `gemini.md`

---

# 🧠 Pinecone Memory Brain Implementation

## Status: ✅ COMPLETED

### What was implemented:

#### 1. Pinecone Connector (`connectors/pinecone_connector.py`)
- ✅ `query_brain(query, top_k, filter)` - Semantic search
- ✅ `upsert_to_brain(doc_id, text, metadata)` - Store memories
- ✅ `delete_from_brain(doc_id)` - Remove memories
- ✅ OpenAI embeddings (text-embedding-3-small, 512 dims)
- ✅ Direct host connection for speed

#### 2. Bot Integration (`agents/aragamago/bot.py`)
- ✅ Import brain connector on startup
- ✅ Query memory before AI reply (top 3 relevant memories)
- ✅ Include memory context in system prompt
- ✅ Save every user message + bot response to memory
- ✅ Timestamped doc IDs for ordering

### Environment Variables Needed (Railway):
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_INDEX_NAME` - Index name (default: aragamago-brain)
- `PINECONE_HOST` - Index host URL

### Index Requirements:
- Model: text-embedding-3-small
- Dimensions: 512
- Name: aragamago-brain

### How It Works:
1. User sends message
2. Bot queries Pinecone for relevant memories
3. Memories injected into AI system prompt
4. AI generates response with memory context
5. Both user message and bot response saved to memory
6. Future conversations can recall this context

### Next Steps:
- [ ] Test memory recall with follow-up questions
- [ ] Add memory search command (e.g., /remember [query])
- [ ] Implement conversation threading
- [ ] Add memory expiration/cleanup

---

# 🔊 Voice (TTS) Implementation

## Status: ✅ COMPLETED

### What was implemented:
- ✅ ElevenLabs TTS for voice replies
- ✅ ElevenLabs STT for voice message transcription
- ✅ OGG output format for Telegram compatibility
- ✅ Free tier model (eleven_flash_v2)
- ✅ Voice ID configurable via environment variable

### Environment Variables Needed (Railway):
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `ELEVENLABS_VOICE_ID` - Voice ID (default: pNInz6obpgnuMvtmW4fz)

---

# 📱 Telegram Bot Implementation

## Status: ✅ COMPLETED

### Features:
- ✅ Text message handling
- ✅ Voice message handling (transcription)
- ✅ Audio file handling
- ✅ AI responses via OpenRouter
- ✅ Butler personality (SOUL.md.txt)
- ✅ Memory brain integration
- ✅ Voice reply integration
