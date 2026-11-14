#!/usr/bin/env bash
# CI-only synthetic verification; this does not touch the owner's VPS.
set -euo pipefail

config="$PWD/infrastructure/deployment/owner-pilot/Caddyfile"
image="caddy:2.11.7"
password="forestproof-ci-only-test-password"
export FORESTPROOF_OWNER_SUBJECT="pilot-owner-ci"
export FORESTPROOF_OWNER_GATEWAY_TOKEN="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
identity_options=(-e FORESTPROOF_OWNER_SUBJECT -e FORESTPROOF_OWNER_GATEWAY_TOKEN)
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
  "${identity_options[@]}" -e FORESTPROOF_OWNER_GATEWAY_PORT=18080 -e FORESTPROOF_OWNER_WEB_PORT=13000 \
  "$image" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
  echo "Gateway accepted a missing password hash" >&2
  exit 1
fi

hash=$(docker run --rm --network none "$image" caddy hash-password --plaintext "$password")
if docker run --rm --network none -v "$config:/etc/caddy/Caddyfile:ro" \
  "${identity_options[@]}" -e FORESTPROOF_OWNER_PASSWORD_HASH="$hash" -e FORESTPROOF_OWNER_GATEWAY_PORT=18080 \
  "$image" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
  echo "Gateway accepted a missing web port" >&2
  exit 1
fi
if docker run --rm --network none -v "$config:/etc/caddy/Caddyfile:ro" \
  "${identity_options[@]}" -e FORESTPROOF_OWNER_PASSWORD_HASH="$hash" -e FORESTPROOF_OWNER_WEB_PORT=13000 \
  "$image" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
  echo "Gateway accepted a missing gateway port" >&2
  exit 1
fi
for missing in FORESTPROOF_OWNER_SUBJECT FORESTPROOF_OWNER_GATEWAY_TOKEN; do
  if docker run --rm --network none -v "$config:/etc/caddy/Caddyfile:ro" \
    "${identity_options[@]}" -e "$missing=" -e FORESTPROOF_OWNER_PASSWORD_HASH="$hash" \
    -e FORESTPROOF_OWNER_GATEWAY_PORT=18080 -e FORESTPROOF_OWNER_WEB_PORT=13000 \
    "$image" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1; then
    echo "Gateway accepted missing owner configuration" >&2
    exit 1
  fi
done
python3 infrastructure/deployment/owner-pilot/mock_upstream.py >"$RUNNER_TEMP/forestproof-mock.log" 2>&1 &
upstream_pid=$!
container=$(docker run -d --rm --network host \
  -v "$config:/etc/caddy/Caddyfile:ro" \
  "${identity_options[@]}" -e FORESTPROOF_OWNER_PASSWORD_HASH="$hash" \
  -e FORESTPROOF_OWNER_GATEWAY_PORT=18080 -e FORESTPROOF_OWNER_WEB_PORT=13000 \
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
expect_status "Wrong password" 401 "$(status -u "$FORESTPROOF_OWNER_SUBJECT:wrong" http://127.0.0.1:18080/)"
expect_status "Wrong owner identifier" 401 "$(status -u "other-owner:$password" http://127.0.0.1:18080/)"
upstream_body=$(curl -sS --max-time 5 -u "$FORESTPROOF_OWNER_SUBJECT:$password" \
  -H 'X-Forestproof-Owner-Subject: forged-owner' -H 'X-Forestproof-Owner-Gateway-Token: forged-token' \
  http://127.0.0.1:18080/)
if [[ "$upstream_body" != "identity verified" ]]; then
  echo "Gateway did not replace the synthetic identity headers or strip authorization" >&2
  exit 1
fi

spoofed=$(status -u "$FORESTPROOF_OWNER_SUBJECT:$password" -H 'Host: untrusted.example' http://127.0.0.1:18080/)
echo "Spoofed host: HTTP $spoofed"
if [[ "$spoofed" != 403 && "$spoofed" != 404 ]]; then exit 1; fi
expect_status "POST without origin" 403 "$(status -u "$FORESTPROOF_OWNER_SUBJECT:$password" -X POST http://127.0.0.1:18080/api/forestproof/cases)"
expect_status "Cross-origin POST" 403 "$(status -u "$FORESTPROOF_OWNER_SUBJECT:$password" -X POST -H 'Origin: https://untrusted.example' http://127.0.0.1:18080/api/forestproof/cases)"
expect_status "Same-origin POST" 200 "$(status -u "$FORESTPROOF_OWNER_SUBJECT:$password" -X POST -H 'Origin: http://127.0.0.1:18080' http://127.0.0.1:18080/api/forestproof/cases)"

ss -lnt | grep -Eq '127\.0\.0\.1:18080[[:space:]]'
if ss -lnt | grep -Eq '(0\.0\.0\.0|\[::\]|\*):18080[[:space:]]'; then
  echo "Gateway is not loopback-only" >&2
  exit 1
fi
echo "Owner gateway checks passed with a synthetic password and loopback upstream."
