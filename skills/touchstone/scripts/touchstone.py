#!/usr/bin/env python3
"""Touchstone Exchange CLI: the agent's hands. Read-only commands.

Standard library only, on purpose: no pip install, so it runs in any agent sandbox.

Configuration comes from the environment, never from arguments:
    TOUCHSTONE_API_KEY   required, looks like tst_...
    TOUCHSTONE_API_URL   optional, defaults to http://localhost:8000

The API key is deliberately NOT accepted as a command-line argument. Arguments end up in
shell history, process lists and agent transcripts; environment variables do not.

Output: one line of compact JSON on stdout, exit code 0.
Errors: {"error": {"code", "message", "hint"}} on stderr, non-zero exit code.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_URL = "http://localhost:8000"
TIMEOUT_SECONDS = 15
MAX_ATTEMPTS = 3          # the first try plus two retries
MAX_BACKOFF_SECONDS = 30

EXIT_API_ERROR = 1        # the server said no
EXIT_SETUP_ERROR = 2      # we never reached the server


def die(code, message, hint="", status=EXIT_API_ERROR):
    json.dump({"error": {"code": code, "message": message, "hint": hint}}, sys.stderr)
    sys.stderr.write("\n")
    sys.exit(status)


def get_api_key():
    key = os.environ.get("TOUCHSTONE_API_KEY", "").strip()
    if not key:
        die("no_api_key", "TOUCHSTONE_API_KEY is not set in the environment.",
            "In a terminal: add  export TOUCHSTONE_API_KEY=tst_...  to ~/.zshrc. In the Claude "
            "Desktop app: add it to the env block of ~/.claude/settings.json. Restart afterwards. "
            "Never ask the user to paste the key into the conversation.",
            EXIT_SETUP_ERROR)
    return key


def get_base_url():
    return os.environ.get("TOUCHSTONE_API_URL", DEFAULT_URL).rstrip("/")


def retry_delay(headers, attempt):
    """Honour Retry-After when the server sends it, otherwise back off gently."""
    raw = (headers.get("Retry-After") or "").strip() if headers else ""
    if raw.isdigit():
        return min(int(raw), MAX_BACKOFF_SECONDS)
    return min(2 ** (attempt - 1), MAX_BACKOFF_SECONDS)


def call(path, params=None):
    url = get_base_url() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Authorization": "Bearer " + get_api_key(),
               "Accept": "application/json",
               "User-Agent": "touchstone-cli/0.1"}

    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                error = json.loads(raw).get("error") or {}
            except ValueError:
                error = {}
            # 429 is the only status worth retrying. A 4xx means the request itself is wrong,
            # so repeating it unchanged would just waste the user's rate limit.
            if exc.code == 429 and attempt < MAX_ATTEMPTS:
                time.sleep(retry_delay(exc.headers, attempt))
                continue
            die(error.get("code") or "http_%d" % exc.code,
                error.get("message") or (raw[:200] or str(exc.reason)),
                error.get("hint") or "")

        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt < MAX_ATTEMPTS:
                time.sleep(retry_delay(None, attempt))
                continue
            reason = getattr(exc, "reason", exc)
            die("connection_failed", "Could not reach the Touchstone Exchange API at %s (%s)." % (get_base_url(), reason),
                "Check TOUCHSTONE_API_URL points at the Touchstone API and that you can reach it. "
                "Ask whoever runs the exchange for the right URL.",
                EXIT_SETUP_ERROR)


def emit(data):
    print(json.dumps(data, separators=(",", ":")))


def main():
    parser = argparse.ArgumentParser(
        prog="touchstone", description="Touchstone Exchange read-only CLI.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("me", help="Who this API key belongs to and what it may do. Use as a health check.")
    sub.add_parser("prices", help="Current price of every token, in USD.")
    sub.add_parser("balances", help="What the user holds.")
    trades = sub.add_parser("trades", help="Recent completed trades, newest first.")
    trades.add_argument("--limit", type=int, default=20, metavar="N",
                        help="How many to return, 1-100 (default 20).")

    args = parser.parse_args()

    if args.command == "me":
        emit(call("/v1/me"))
    elif args.command == "prices":
        emit(call("/v1/prices"))
    elif args.command == "balances":
        emit(call("/v1/balances"))
    elif args.command == "trades":
        if not 1 <= args.limit <= 100:
            die("invalid_limit", "--limit must be between 1 and 100.", "Try --limit 20.", EXIT_SETUP_ERROR)
        emit(call("/v1/trades", {"limit": args.limit}))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
