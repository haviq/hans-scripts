#!/usr/bin/env bash
# start_tunnel.sh - jalanin cloudflared quick tunnel ke 9router (port 20128 lokal)
# Hasil: URL https://<random>.trycloudflare.com yang bisa diakses dari luar VPS.

pkill -f "cloudflared tunnel" 2>/dev/null
sleep 2
rm -f /tmp/cf9.log

setsid cloudflared tunnel --url http://localhost:20128 --no-autoupdate > /tmp/cf9.log 2>&1 < /dev/null &

echo "tunnel start dikirim, tunggu ~20s buat URL"
