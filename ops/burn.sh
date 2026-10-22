#!/usr/bin/env bash
# burn.sh - self-contained token burner. Tanpa SSH hop, paste di terminal mana saja.
# Butuh: bash, curl, python3. Default: 1 juta token input per request.

set -u

BASE_URL="${BASE_URL:-https://9router.haviq.dev/v1}"
API_KEY="${API_KEY:-sk-6b3ac6ef8e3b70c9-vr88tq-8a4cba7f}"
MODEL="${MODEL:-kl/deepseek-v4.1-flash}"
PROMPT_TOKENS="${PROMPT_TOKENS:-1000000}"
WORKERS="${WORKERS:-2}"
SLEEP="${SLEEP:-10}"
MAX_TOKENS="${MAX_TOKENS:-64}"
ROUNDS="${ROUNDS:-0}"
DURATION="${DURATION:-0}"
LOG_DIR="${LOG_DIR:-/tmp/token_burner}"

mkdir -p "$LOG_DIR"; rm -f "$LOG_DIR/limit.flag"
PAYLOAD="$LOG_DIR/payload.json"

PROMPT_TOKENS="$PROMPT_TOKENS" MODEL="$MODEL" MAX_TOKENS="$MAX_TOKENS" PAYLOAD="$PAYLOAD" python3 - <<'PYEOF'
import json, os
unit = ("Jelaskan secara sangat panjang dan mendetail topik berikut dari sudut teknis, "
        "historis, praktis, ekonomi, sosial, dan filosofis: ")
target = int(os.environ["PROMPT_TOKENS"]) * 4
content = unit * max(1, target // len(unit))
p = {"model": os.environ["MODEL"],
     "messages": [{"role": "user", "content": content}],
     "max_tokens": int(os.environ["MAX_TOKENS"]), "stream": False}
json.dump(p, open(os.environ["PAYLOAD"], "w"))
print(f"payload: model={p['model']} chars={len(content)} approx_tokens={len(content)//4}")
PYEOF

hit() {
  local out code
  out=$(curl -sS -w "\n%{http_code}" -X POST "$BASE_URL/chat/completions" \
    -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
    --max-time 300 --data-binary @"$PAYLOAD" 2>>"$LOG_DIR/err.log")
  code=$(printf '%s' "$out" | tail -n1)
  printf '%s' "$out" | head -n -1 >> "$LOG_DIR/resp.log"
  echo "$(date +%s) code=$code" >> "$LOG_DIR/codes.log"
  if [ "$code" = "429" ] || [ "$code" = "403" ]; then echo LIMIT >> "$LOG_DIR/limit.flag"; fi
}

worker() {
  local r=0
  while [ ! -f "$LOG_DIR/limit.flag" ]; do
    hit; r=$((r+1))
    [ "$ROUNDS" != "0" ] && [ "$r" -ge "$ROUNDS" ] && break
    [ "$DURATION" != "0" ] && [ $(( $(date +%s) - START )) -ge "$DURATION" ] && break
    sleep "$SLEEP"
  done
}

START=$(date +%s)
echo "burn start: $MODEL | workers=$WORKERS sleep=${SLEEP}s prompt_tokens=$PROMPT_TOKENS"
for ((w=1;w<=WORKERS;w++)); do worker & done
wait
echo "burn stop. requests=$(wc -l < "$LOG_DIR/codes.log" 2>/dev/null || echo 0). log: $LOG_DIR/"
