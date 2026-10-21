---
name: touchstone
description: Check Touchstone Exchange balances, token prices, account details and trade history. Use when the user asks what they hold, what a token is worth, whether their Touchstone Exchange API key works, or about past trades on the Touchstone exchange (tokens BTC, ETH, USDC).
---

# Touchstone Exchange

A small fake exchange used for testing agent integrations. Fake tokens (BTC, ETH, USDC), fake
balances, fixed prices, no blockchain. This skill is **read-only**: nothing it does can move money.

## Running commands

Every command is run through the bundled script with Bash:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/touchstone/scripts/touchstone.py" <command>
```

| Command | What it returns |
|---|---|
| `me` | Who the API key belongs to and which scopes it has. Use as a health check. |
| `prices` | The USD price of every token. |
| `balances` | What the user currently holds. |
| `trades --limit N` | Recent completed trades, newest first. N is 1-100, default 20. |

Each prints one line of compact JSON. Read it and answer the user in plain language — don't make
them read raw JSON unless they ask for it.

## Before anything else

The script needs `TOUCHSTONE_API_KEY` in its environment. If a command fails with `no_api_key`, tell the
user to run this in the shell they start their agent from, then restart it:

```bash
export TOUCHSTONE_API_KEY=tst_your_key_here
```

If the server isn't running locally, they also need `export TOUCHSTONE_API_URL=https://...`.
The default is `http://localhost:8000`.

## Safety rules

- **Never print the API key, and never ask the user to paste it into the conversation.** It belongs
  in the environment only. If you ever see a key in the transcript, tell the user to revoke it.
- The script reads the key from the environment by design. Never pass a key as a command-line
  argument — arguments leak into shell history and transcripts.
- This skill cannot trade. If the user asks to swap, buy or sell, say plainly that this version is
  read-only and no trading commands exist yet.

## Handling errors

Errors arrive as `{"error": {"code", "message", "hint"}}` on stderr. The `hint` is written for you —
read it and act on it rather than guessing or retrying blindly.

Common cases: `no_api_key` and `connection_failed` are setup problems (exit code 2) — tell the user
what to fix. `invalid_api_key` means the key is wrong, revoked or expired. `insufficient_scope`
means the key lacks the `read` scope; the user needs a new key.

For the full error list, rate limits and response shapes, read
[references/api.md](references/api.md) — only when you need that detail.
