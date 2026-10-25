#!/usr/bin/env bash
# 9router watchdog: restart the container when its health endpoint stops
# answering, and notify telegram so the outage is visible before someone opens
# the dashboard.
#
# Deliberately conservative: a single failed health check is NOT an outage (the
# container can be mid-restart, or the host briefly under load). It takes three
# consecutive failures with a short gap to trigger a restart, which filters out
# transient blips without delaying a real recovery by more than ~60s.
set -u

CONTAINER="9router-plinian"
HEALTH_URL="http://127.0.0.1:20131/api/health"
STATE_FILE="/var/lib/9router-watchdog/state"
LOG_FILE="/var/log/9router-watchdog.log"
MAX_FAILS=3

# Optional telegram notify. Set TG_TOKEN and TG_CHAT in /etc/9router-watchdog.env
TG_TOKEN=""
TG_CHAT=""
if [ -f /etc/9router-watchdog.env ]; then
  # shellcheck disable=SC1091
  . /etc/9router-watchdog.env
fi

mkdir -p "$(dirname "$STATE_FILE")"

log() {
  printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"
}

notify() {
  [ -z "$TG_TOKEN" ] || [ -z "$TG_CHAT" ] && return 0
  curl -s -o /dev/null --max-time 8 \
    "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
    -d "chat_id=${TG_CHAT}" \
    -d "text=$1" >/dev/null 2>&1 || true
}

fail_count=0
[ -f "$STATE_FILE" ] && fail_count=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
case "$fail_count" in (*[!0-9]*|'') fail_count=0 ;; esac

# A fast HTTP probe is the only signal that matters: the container can be up
# with the port bound and still fail every request, and it can be down with the
# process still running during a hung shutdown.
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$HEALTH_URL" 2>/dev/null || echo 000)

if [ "$code" = "200" ]; then
  if [ "$fail_count" -ge "$MAX_FAILS" ]; then
    log "recovered: health 200 after $fail_count failures"
    notify "✅ 9router recovered — health 200 after $fail_count failures"
  fi
  echo 0 > "$STATE_FILE"
  exit 0
fi

fail_count=$((fail_count + 1))
echo "$fail_count" > "$STATE_FILE"
log "health check failed (HTTP $code) — consecutive=$fail_count"

if [ "$fail_count" -lt "$MAX_FAILS" ]; then
  exit 0
fi

log "restarting container $CONTAINER (fail_count=$fail_count)"
if docker restart "$CONTAINER" >/dev/null 2>&1; then
  echo 0 > "$STATE_FILE"
  log "restart ok"
  notify "🔧 9router restarted — health was down for $fail_count checks (HTTP $code)"
else
  log "restart FAILED"
  notify "❌ 9router restart FAILED — manual intervention needed (HTTP $code)"
fi
