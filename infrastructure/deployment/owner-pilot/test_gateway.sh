#!/usr/bin/env bash
# CI-only synthetic verification; this does not touch the owner's VPS.
set -euo pipefail

config="$PWD/infrastructure/deployment/owner-pilot/Caddyfile"
image="caddy:2.11.7"
password="forestproof-ci-only-test-password"
container=""
upstream_pid=""

cleanup() {
  local result=$?
  if [[ $result -ne 0 && -n "$container" ]]; then docker logs "$container" >&2 || true; fi
  if [[ -n "$container" ]]; then docker rm -f "$container" >/dev/null 2>&1 || true; fi
  if [[ -n "$upstream_pid" ]]; then kill "$upstream_pid" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

# A missing hash must not create an unprotected gateway.
if docker run --rm --network none -v "$config:/etc/caddy/Caddyfile:ro" \
  "$image" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
  echo "Gateway accepted a missing password hash" >&2
  exit 1
fi

hash=$(docker run --rm --network none "$image" caddy hash-password --plaintext "$password")
python3 infrastructure/deployment/owner-pilot/mock_upstream.py >"$RUNNER_TEMP/forestproof-mock.log" 2>&1 &
upstream_pid=$!
container=$(docker run -d --rm --network host \
  -v "$config:/etc/caddy/Caddyfile:ro" \
  -e FORESTPROOF_OWNER_PASSWORD_HASH="$hash" \
  "$image" caddy run --config /etc/caddy/Caddyfile --adapter caddyfile)

ready=false
for _ in {1..40}; do
  if curl -sS --max-time 1 -o /dev/null http://127.0.0.1:18080/ 2>/dev/null; then
    ready=true
    break
  fi
  sleep 0.5
done
if [[ "$ready" != true ]]; then
  docker logs "$container" >&2 || true
  echo "Gateway did not start" >&2
  exit 1
fi

status() { curl -sS --max-time 5 -o /dev/null -w '%{http_code}' "$@"; }
expect_status() {
  local label="$1" wanted="$2" actual="$3"
  echo "$label: HTTP $actual (expected $wanted)"
  if [[ "$actual" != "$wanted" ]]; then exit 1; fi
}
expect_status "Unauthenticated home" 401 "$(status http://127.0.0.1:18080/)"
expect_status "Unauthenticated API" 401 "$(status http://127.0.0.1:18080/api/forestproof/cases)"
expect_status "Wrong password" 401 "$(status -u owner:wrong http://127.0.0.1:18080/)"
upstream_body=$(curl -sS --max-time 5 -u "owner:$password" http://127.0.0.1:18080/)
if [[ "$upstream_body" != "authorization=absent" ]]; then
  echo "Authenticated request failed or authorization reached upstream" >&2
  exit 1
fi

spoofed=$(status -u "owner:$password" -H 'Host: untrusted.example' http://127.0.0.1:18080/)
echo "Spoofed host: HTTP $spoofed"
if [[ "$spoofed" != 403 && "$spoofed" != 404 ]]; then exit 1; fi
expect_status "POST without origin" 403 "$(status -u "owner:$password" -X POST http://127.0.0.1:18080/api/forestproof/cases)"
expect_status "Cross-origin POST" 403 "$(status -u "owner:$password" -X POST -H 'Origin: https://untrusted.example' http://127.0.0.1:18080/api/forestproof/cases)"
expect_status "Same-origin POST" 200 "$(status -u "owner:$password" -X POST -H 'Origin: http://127.0.0.1:18080' http://127.0.0.1:18080/api/forestproof/cases)"

ss -lnt | grep -Eq '127\.0\.0\.1:18080[[:space:]]'
if ss -lnt | grep -Eq '(0\.0\.0\.0|\[::\]|\*):18080[[:space:]]'; then
  echo "Gateway is not loopback-only" >&2
  exit 1
fi
echo "Owner gateway checks passed with a synthetic password and loopback upstream."
