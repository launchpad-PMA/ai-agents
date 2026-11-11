#!/bin/sh
# Pull the local models from the Exit & Build stack onto the home machine.
# Run this where Ollama is installed. It does not start Telegram.
set -eu

echo "Pulling general, vision, and search models."
ollama pull qwen3.6:27b
ollama pull qwen3.8:27b
ollama pull nomic-embed-text

cat <<'EOF'

Point Aragamago at this machine with:

  OLLAMA_BASE_URL=http://127.0.0.1:11434
  AI_PROVIDER_ORDER=ollama,openrouter,gemini
  ARAGAMAGO_ARCHIVE=$HOME/aragamago/archive

Serve Ollama with a 64K context:

  OLLAMA_CONTEXT_LENGTH=64000 ollama serve

One Telegram poller only. Do not also connect Hermes to the same bot token.
EOF
