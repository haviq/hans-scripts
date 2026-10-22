#!/usr/bin/env bash
# prd-studio-backup.sh - backup harian database PRD Studio.
# Simpan 14 backup terakhir, hapus yang lebih lama.
set -euo pipefail

DB="/home/ubuntu/prdstudio/data/prd.db"
DEST="/home/ubuntu/prdstudio-backups"
KEEP=14

mkdir -p "$DEST"
stamp=$(date '+%Y%m%d_%H%M%S')
out="$DEST/prd-$stamp.db"

# sqlite3 .backup kalau ada (aman walau DB sedang dipakai), kalau tidak copy biasa
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$DB" ".backup '$out'"
else
  cp "$DB" "$out"
fi

gzip -f "$out"

# hapus backup lama
ls -1t "$DEST"/prd-*.db.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

echo "$(date '+%Y-%m-%d %H:%M:%S') backup ok: $out.gz ($(ls -1 "$DEST"/prd-*.db.gz 2>/dev/null | wc -l) total)"
