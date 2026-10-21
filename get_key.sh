#!/usr/bin/env bash
# Create your own Touchstone Exchange API key.
#
#   ./get_key.sh                                  # against http://localhost:8000
#   TOUCHSTONE_API_URL=https://touchstone.example.com ./get_key.sh
#
# Run this yourself. The key it prints is shown once and never again, and nobody
# has to send a key to anyone else.
set -euo pipefail

BASE="${TOUCHSTONE_API_URL:-http://localhost:8000}"
BASE="${BASE%/}"
JAR="$(mktemp)"; trap 'rm -f "$JAR"' EXIT
jget() { python3 -c "import sys,json; d=json.load(sys.stdin); print(d$1)" 2>/dev/null || true; }

if ! curl -sf "$BASE/health" >/dev/null 2>&1; then
  echo "Cannot reach $BASE" >&2
  echo "Check the URL. Ask whoever runs the exchange for the right TOUCHSTONE_API_URL." >&2
  exit 2
fi
echo "Server: $BASE"

read -r -p "Email: " EMAIL
# -s keeps the password off the screen; it is never passed as an argument.
read -r -s -p "Password (at least 10 characters): " PASSWORD; echo
[ ${#PASSWORD} -ge 10 ] || { echo "Password must be at least 10 characters." >&2; exit 2; }

payload() { python3 -c 'import json,sys; print(json.dumps({"email":sys.argv[1],"password":sys.argv[2]}))' "$EMAIL" "$PASSWORD"; }

CODE=$(curl -s -o /tmp/touchstone_signup.$$ -w '%{http_code}' -c "$JAR" -X POST "$BASE/account/signup" \
  -H 'Content-Type: application/json' -d "$(payload)")
case "$CODE" in
  201) echo "Account created." ;;
  409) echo "Account already exists, logging in." ;;
  *)   echo "Signup failed (HTTP $CODE):" >&2; cat /tmp/touchstone_signup.$$ >&2; echo >&2
       rm -f /tmp/touchstone_signup.$$; exit 1 ;;
esac
rm -f /tmp/touchstone_signup.$$

# A fresh signup already logs us in. Only log in when the account existed already.
if [ "$CODE" = "409" ]; then
  CODE=$(curl -s -o /tmp/touchstone_login.$$ -w '%{http_code}' -c "$JAR" -X POST "$BASE/account/login" \
    -H 'Content-Type: application/json' -d "$(payload)")
  if [ "$CODE" != "200" ]; then
    echo "Login failed (HTTP $CODE):" >&2; cat /tmp/touchstone_login.$$ >&2; echo >&2
    rm -f /tmp/touchstone_login.$$; exit 1
  fi
  rm -f /tmp/touchstone_login.$$
fi
unset PASSWORD

# Creating a key is a cookie-authenticated write, so it needs the CSRF token the server stored
# on this session. It arrives in a readable cookie; echo it back in the header.
CSRF=$(awk '$6 == "touchstone_csrf" { print $7 }' "$JAR" | tail -1)
if [ -z "$CSRF" ]; then
  echo "No CSRF token in the session. Is the server up to date?" >&2
  exit 1
fi

NAME="${1:-$(hostname)-$(date +%Y%m%d)}"
CREATED=$(curl -s -b "$JAR" -X POST "$BASE/dashboard/keys" -H 'Content-Type: application/json' \
  -H "X-CSRF-Token: $CSRF" \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"scopes":["read"]}))' "$NAME")")
KEY=$(echo "$CREATED" | jget '["api_key"]')
if [ -z "$KEY" ]; then
  echo "Could not create a key:" >&2; echo "$CREATED" >&2; exit 1
fi

cat <<BANNER

  Your API key (shown once, copy it now):

      $KEY

  Add it to the shell you start Claude Code from:

      export TOUCHSTONE_API_KEY=$KEY
      export TOUCHSTONE_API_URL=$BASE

  Keep it secret. Anyone with this key can read your account.
  Lost it? Run this script again for a new one.

BANNER
