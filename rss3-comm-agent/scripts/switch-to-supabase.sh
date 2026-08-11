#!/usr/bin/env bash
# Replace Railway Postgres with Supabase on the Linode RSS3 node.
#
# Usage:
#   SUPABASE_URI='postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres?sslmode=require' \
#     REMOTE=1 ./scripts/switch-to-supabase.sh
#
# Or put the URI in a file (one line, no trailing newline) and run:
#   REMOTE=1 ./scripts/switch-to-supabase.sh path/to/uri.txt
#
# Without REMOTE=1, prints the commands to run manually on the Linode.

set -euo pipefail
LINODE="${LINODE_HOST:-root@172.232.129.170}"
RSS3_DIR="${RSS3_DIR:-/home/babajohn33/rss3-node}"

if [[ -n "${1:-}" ]]; then
  SUPABASE_URI=$(cat "$1")
else
  SUPABASE_URI="${SUPABASE_URI:-}"
fi
if [[ -z "$SUPABASE_URI" ]]; then
  echo "Set SUPABASE_URI or pass a file path: $0 path/to/uri.txt"
  exit 1
fi

if [[ "${REMOTE:-}" == "1" ]]; then
  TMP_URI=$(mktemp)
  trap 'rm -f "$TMP_URI"' EXIT
  echo -n "$SUPABASE_URI" > "$TMP_URI"
  scp -q "$TMP_URI" "$LINODE:/tmp/supabase_uri.txt"
  ssh "$LINODE" "cd $RSS3_DIR && \
    cp config/config.yaml config/config.yaml.bak-\$(date +%Y%m%d) && \
    cp .env .env.bak-\$(date +%Y%m%d) && \
    URI=\$(cat /tmp/supabase_uri.txt | sed 's/\\\\/\\\\\\\\/g; s/&/\\\\&/g') && \
    sed -i \"s|uri: postgresql://postgres:[^@]*@trolley.proxy.rlwy.net:[^?]*/railway?sslmode=require|uri: \$URI|\" config/config.yaml && \
    sed -i \"s|agentdata_db_url: postgresql://postgres:[^@]*@trolley.proxy.rlwy.net:[^?]*/railway?sslmode=require|agentdata_db_url: \$URI|\" config/config.yaml && \
    sed -i \"s|DB_CONNECTION=postgresql://postgres:[^@]*@trolley.proxy.rlwy.net:[^?]*/railway?sslmode=require|DB_CONNECTION=\$URI|\" .env && \
    sed -i \"s|DATABASE_URI=postgresql://postgres:[^@]*@trolley.proxy.rlwy.net:[^?]*/railway?sslmode=require|DATABASE_URI=\$URI|\" .env && \
    rm -f /tmp/supabase_uri.txt && \
    echo 'Updated. Restarting stack.' && \
    docker-compose down && docker-compose up -d && \
    echo 'Verify:' && docker-compose ps && sleep 3 && docker-compose logs --tail=15 rss3_node_core"
else
  echo "To apply on Linode, run with REMOTE=1 (and SUPABASE_URI or a file with the URI):"
  echo "  SUPABASE_URI='<your-uri?sslmode=require>' REMOTE=1 $0"
  echo ""
  echo "Or run these manually on the server (ssh $LINODE):"
  echo "  cd $RSS3_DIR"
  echo "  export SUPABASE_URI='<paste-your-uri?sslmode=require>'"
  echo "  sed -i \"s|uri: postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|uri: \$SUPABASE_URI|\" config/config.yaml"
  echo "  sed -i \"s|agentdata_db_url: postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|agentdata_db_url: \$SUPABASE_URI|\" config/config.yaml"
  echo "  sed -i \"s|DB_CONNECTION=postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|DB_CONNECTION=\$SUPABASE_URI|\" .env"
  echo "  sed -i \"s|DATABASE_URI=postgresql://postgres:.*@trolley.proxy.rlwy.net:31631/railway?sslmode=require|DATABASE_URI=\$SUPABASE_URI|\" .env"
  echo "  docker-compose down && docker-compose up -d"
fi
