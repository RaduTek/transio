#!/usr/bin/env bash
set -euo pipefail

# Default target URL (can be overridden by env: TARGET_URL=... ./run-kiosk.sh)
DEFAULT_TARGET_URL="http://192.168.1.50:5173"
TARGET_URL="${TARGET_URL:-$DEFAULT_TARGET_URL}"

# Optional overrides:
#   CHROME_BIN=/usr/bin/chromium
#   KIOSK_PROFILE_DIR=/var/lib/validator-kiosk/chrome-profile
CHROME_BIN="${CHROME_BIN:-}"
KIOSK_PROFILE_DIR="${KIOSK_PROFILE_DIR:-/var/lib/validator-kiosk/chrome-profile}"

log() { printf '[kiosk] %s\n' "$*"; }
die() { printf '[kiosk][error] %s\n' "$*" >&2; exit 1; }

# Extract origin (scheme + host + optional port), because SerialAllowAllPortsForUrls is origin-based.
ORIGIN="$(printf '%s' "$TARGET_URL" | sed -E 's#^(https?://[^/]+).*$#\1#')"
[[ "$ORIGIN" =~ ^https?:// ]] || die "TARGET_URL must start with http:// or https://"

# Resolve Chromium/Chrome binary
if [[ -z "$CHROME_BIN" ]]; then
  for c in chromium chromium-browser google-chrome-stable google-chrome; do
    if command -v "$c" >/dev/null 2>&1; then
      CHROME_BIN="$(command -v "$c")"
      break
    fi
  done
fi
[[ -n "$CHROME_BIN" ]] || die "No Chromium/Chrome binary found. Set CHROME_BIN explicitly."

# Determine policy directory for the detected browser
# - Chromium typically: /etc/chromium/policies/managed
# - Google Chrome typically: /etc/opt/chrome/policies/managed
POLICY_DIR="/etc/chromium/policies/managed"
if [[ "$CHROME_BIN" == *google-chrome* ]]; then
  POLICY_DIR="/etc/opt/chrome/policies/managed"
fi

POLICY_FILE="$POLICY_DIR/99-validator-serial-policy.json"

log "Using browser: $CHROME_BIN"
log "Target URL: $TARGET_URL"
log "Origin: $ORIGIN"
log "Policy file: $POLICY_FILE"

# Need root to write managed policy
if [[ "${EUID}" -ne 0 ]]; then
  die "Run as root (or via sudo) so managed policy can be written to $POLICY_DIR"
fi

mkdir -p "$POLICY_DIR"
mkdir -p "$KIOSK_PROFILE_DIR"

cat > "$POLICY_FILE" <<EOF
{
  "SerialAllowAllPortsForUrls": ["$ORIGIN"]
}
EOF

log "Wrote managed policy for WebSerial auto-grant."

# Build Chromium flags
FLAGS=(
  --kiosk
  --start-fullscreen
  --no-first-run
  --no-default-browser-check
  --disable-session-crashed-bubble
  --disable-infobars
  --user-data-dir="$KIOSK_PROFILE_DIR"
)

# If HTTP, bypass secure-context requirement for this origin only.
if [[ "$ORIGIN" == http://* ]]; then
  FLAGS+=(--unsafely-treat-insecure-origin-as-secure="$ORIGIN")
  log "Applied insecure-origin secure-context override for $ORIGIN"
fi

log "Launching kiosk..."
exec "$CHROME_BIN" "${FLAGS[@]}" "$TARGET_URL"