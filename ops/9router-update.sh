#!/usr/bin/env bash
# 9router-update.sh - auto update 9router docker kalau registry punya versi baru.
# Data aman: volume /root/.9router tetap dipakai saat recreate.
set -euo pipefail

IMAGE="decolua/9router:latest"
NAME="9router"
LOG="/home/ubuntu/9router-update.log"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(ts) $*" | tee -a "$LOG"; }

# digest image yang sedang dipakai container
running_digest=$(sudo docker inspect "$NAME" --format '{{.Image}}' 2>/dev/null || echo none)

# pull versi terbaru
sudo docker pull "$IMAGE" >/dev/null 2>&1 || { log "pull gagal, skip"; exit 0; }
new_digest=$(sudo docker inspect --format '{{.Id}}' "$IMAGE" 2>/dev/null || echo none)

if [ "$running_digest" = "$new_digest" ]; then
  log "sudah terbaru ($new_digest), tidak ada perubahan"
  exit 0
fi

log "versi baru terdeteksi: $running_digest -> $new_digest"

# recreate container, volume /root/.9router dipertahankan
sudo docker stop "$NAME" >/dev/null
sudo docker rm "$NAME" >/dev/null
sudo docker run -d --name "$NAME" --restart unless-stopped -p 127.0.0.1:20128:20128 -v /root/.9router:/app/data "$IMAGE" >/dev/null

sleep 8
if sudo docker ps --filter "name=^${NAME}$" --filter status=running -q | grep -q .; then
  log "update sukses, container jalan"
else
  log "PERINGATAN: container tidak running setelah update, cek manual"
fi