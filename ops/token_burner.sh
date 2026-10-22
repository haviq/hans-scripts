#!/usr/bin/env bash
# token_burner.sh - boroskan kuota lewat input besar, low-spam
# Default: kl/deepseek-v4.1-flash, ~1 juta token input per request, worker sedikit + jeda.

set -u

BASE_URL="${BASE_URL:-https://9router.haviq.dev/v1}"
API_KEY="${API_KEY:-sk-6b3ac6ef8e3b70c9-vr88tq-8a4cba7f}"
MODEL="${MODEL:-kl/deepseek-v4.1-flash}"
WORKERS="${WORKERS:-2}"          # jumlah request paralel (rendah = gak spam)
SLEEP="${SLEEP:-10}"             # jeda detik antar request per worker
PROMPT_TOKENS="${PROMPT_TOKENS:-1000000}"  # target token input per request (approx)
MAX_TOKENS="${MAX_TOKENS:-64}"   # output kecil, fokus input
ROUNDS="${ROUNDS:-0}"            # 0 = tak terbatas sampai limit/Ctrl-C
DURATION="${DURATION:-0}"        # 0 = durasi bebas, atau detik
LOG_DIR="${LOG_DIR:-/tmp/token_burner}"

mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR/limit.flag"

PAYLOAD="$LOG_DIR/payload.json"

# Bangun payload sekali (prompt besar) - pakai python biar aman untuk ukuran raksasa.
PROMPT_TOKENS="$PROMPT_TOKENS" MODEL="$MODEL" MAX_TOKENS="$MAX_TOKENS" PAYLOAD="$PAYLOAD" python3 - <<'PYEOF'
import json, os
unit = ("Jelaskan secara sangat panjang dan mendetail topik berikut dari sudut teknis, "
        "historis, praktis, ekonomi, sosial, dan filosofis: ")
target_chars = int(os.environ["PROMPT_TOKENS"]) * 4  # ~4 char/token
reps = max(1, target_chars // len(unit))
content = unit * reps
payload = {
    "model": os.environ["MODEL"],
    "messages": [{"role": "user", "content": content}],
    "max_tokens": int(os.environ["MAX_TOKENS"]),
    "stream": False,
}
with open(os.environ["PAYLOAD"], "w") as f:
    json.dump(payload, f)
print(f"payload built: model={payload['model']} chars={len(content)} approx_tokens={len(content)//4} file={os.environ['PAYLOAD']}")
PYEOF

hit() {
  local n=$1 out code
  out=$(curl -sS -w "\n%{http_code}" \
    -X POST "$BASE_URL/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    --max-time 300 \
    --data-binary @"$PAYLOAD" 2>>"$LOG_DIR/err.log")
  code=$(printf '%s' "$out" | tail -n1)
  printf '%s' "$out" | head -n -1 >> "$LOG_DIR/resp.log"
  echo "$(date +%s) worker=$n code=$code" >> "$LOG_DIR/codes.log"
  if [ "$code" = "429" ] || [ "$code" = "403" ]; then echo LIMIT >> "$LOG_DIR/limit.flag"; fi
}

worker() {
  local n=$1 round=0
  while [ ! -f "$LOG_DIR/limit.flag" ]; do
    hit "$n"
    round=$((round+1))
    if [ "$ROUNDS" != "0" ] && [ "$round" -ge "$ROUNDS" ]; then break; fi
    if [ "$DURATION" != "0" ] && [ $(( $(date +%s) - START )) -ge "$DURATION" ]; then break; fi
    sleep "$SLEEP"
  done
}

START=$(date +%s)
echo "burn start url=$BASE_URL model=$MODEL workers=$WORKERS sleep=${SLEEP}s prompt_tokens=$PROMPT_TOKENS max_tokens=$MAX_TOKENS rounds=$ROUNDS"
for ((w=1;w<=WORKERS;w++)); do worker "$w" & done
wait
echo "burn stop. requests: $(wc -l < "$LOG_DIR/codes.log" 2>/dev/null || echo 0). cek $LOG_DIR/"
