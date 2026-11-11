# Local AI build

The Exit & Build talk at [freedomfarmers.com/ai/build](https://freedomfarmers.com/ai/build/) splits a private AI into three layers: the machine, the software, and the knowledge. This is Aragamago on that same shape. Buy links and prices stay on that page. This file is how the bot uses the stack.

Checked against that page on November 11, 2026.

## Layer 1. The machine

The graphics card's memory decides which models fit.

| Role | Spec from the talk |
|------|--------------------|
| Full build | RTX 5090, 32 GB. That holds a 27B model, about 17 GB on disk and about 20 GB in use with a 64K context |
| Smaller card | RTX 5060 Ti, 16 GB. The same 27B models still load, and part of the model spills into system memory, so answers are slower. An 8 GB card with the same name is too small |
| Mac | Mac mini, M5 Pro, 64 GB. Shared memory holds the models. It does not run NVIDIA CUDA |

Processor, 32 GB of DDR5-6000 memory, a 2 TB NVMe, motherboard, power supply, case, and cooler are on the talk page. Expect the full build around $9,000 to $10,000, most of it the graphics card. The cheaper routes on that page start near $2,000.

Power, solar, and the EcoFlow backup are house equipment. This repo does not change GPU power limits.

## Layer 2. The software

All of this is free.

| Piece | What Aragamago uses |
|-------|---------------------|
| Model runner | [Ollama](https://ollama.com) |
| General model | `qwen3.6:27b` at temperature 0.3 and a 64K context |
| Vision model | `qwen3.8:27b` |
| Search model | `nomic-embed-text` |
| Chief of staff | Aragamago. Telegram, Google tools, short chat memory, skills, and its own archive folder |
| Separate room | Maxayauwi. RSS3, Farcaster, and the public site. Its files and credentials stay there |

On the home machine:

```bash
sh tools/local_ai_up.sh
```

Then run the bot with:

```bash
OLLAMA_BASE_URL=http://127.0.0.1:11434 \
AI_PROVIDER_ORDER=ollama,openrouter,gemini \
ARAGAMAGO_ARCHIVE=$HOME/aragamago/archive \
python agents/aragamago/bot.py
```

Start Ollama itself with `OLLAMA_CONTEXT_LENGTH=64000`. Its own default context is too small for a tool-using agent.

Railway is unchanged. The default provider order is still OpenRouter, then OpenAI, then Gemini. Ollama runs only when `OLLAMA_BASE_URL` is set, and a photo uses the local vision model when `ollama` is first in `AI_PROVIDER_ORDER`.

Hermes Agent is the framework named in the talk for memory, skills, tools, and schedules. Aragamago is the agent that already holds the Telegram token. Keep it that way. A second Hermes process on the same token causes Telegram 409s.

## Where the rooms are going

The talk showed one chief of staff and separate agents. Each agent had its own knowledge, its own credentials, and its own boundary. That shape is the example. His roster is not ours, and those names are not created here.

Ours today:

| Room | What it holds |
|------|----------------|
| Aragamago | Chief of staff. Sacred library, tasks, calendar, Telegram |
| Maxayauwi | Comm agent. RSS3 node, Farcaster, public site |

A new room is added when Baba names it. It gets its own folder and its own credentials before it gets a prompt. The local models are shared infrastructure: every room may call Ollama on the house machine. Files and credentials do not cross.

The library can live on the NAS, one directory per room:

```text
$ARAGAMAGO_ARCHIVE/aragamago/
$ARAGAMAGO_ARCHIVE/maxayauwi/
```

Aragamago searches and writes only `aragamago/`. A note that starts with "remember that" or "save this" goes in that room's `inbox/`, and still updates Pinecone when the index is up. Chat turns are not written into the archive. If the archive has no room folders yet, notes stay in a single `inbox/` as before.

Skills live in `agents/aragamago/skills/`. A skill is included on a turn when the message contains one of its trigger words.

`/health` adds a `local` object: whether Ollama is configured, the three model names, whether an archive folder is set, and the active room id. It does not print the folder path.
