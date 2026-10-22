#!/usr/bin/env bash
# Build 9router di VPS. Dijalankan detached, log ke /tmp/build9r.log
set -x
cd /home/ubuntu/9r-build || exit 1

npm config set registry https://registry.npmjs.org/
echo "registry: $(npm config get registry)"

rm -rf node_modules package-lock.json

echo "=== NPM INSTALL START $(date) ==="
npm install --no-audit --no-fund
install_rc=$?
echo "=== NPM INSTALL END rc=$install_rc $(date) ==="

if [ $install_rc -ne 0 ]; then
  echo "INSTALL FAILED"
  exit $install_rc
fi

echo "=== BUILD START $(date) ==="
NODE_OPTIONS=--max-old-space-size=4096 npm run build
build_rc=$?
echo "=== BUILD END rc=$build_rc $(date) ==="

exit $build_rc
