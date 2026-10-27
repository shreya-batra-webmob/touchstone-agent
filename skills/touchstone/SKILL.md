---
name: touchstone
description: Check Touchstone Exchange balances, token prices, account details and trade history. Use when the user asks what they hold, what a token is worth, whether their Touchstone Exchange API key works, or about past trades on the Touchstone exchange (tokens BTC, ETH, USDC).
---

# Touchstone Exchange

A small fake exchange used for testing agent integrations. Fake tokens (BTC, ETH, USDC), fake
balances, fixed prices, no blockchain. This skill is **read-only**: nothing it does can move money.

## Running commands

The CLI is `scripts/touchstone.py`, inside this skill's own directory — the path your agent gave
you when it loaded this file. Substitute that directory wherever `<skill-dir>` appears:

```bash
python3 <skill-dir>/scripts/touchstone.py <command>
```

Not sure of the directory? Find it once, then reuse it:

```bash
find ~/.claude ~/.agents ~/.codex ~/.cursor ~/.config -name touchstone.py 2>/dev/null | head -1
```

(Don't hardcode a vendor-specific variable here. Several different agents install this skill, and
each puts it somewhere different.)

| Command | What it returns |
|---|---|
| `me` | Who the API key belongs to and which scopes it has. Use as a health check. |
| `prices` | The USD price of every token. |
| `balances` | What the user currently holds. |
| `trades --limit N` | Recent completed trades, newest first. N is 1-100, default 20. |

Each prints one line of compact JSON. Read it and answer the user in plain language — don't make
them read raw JSON unless they ask for it.

## Questions that need more than one command

If answering needs two or more commands, or any arithmetic, **write one short Python script that
does the whole job and prints only the answer.** Don't run the commands one at a time and work it
out yourself.

Two reasons. Each raw JSON response you read costs context you don't need to spend. And money
arithmetic done in code with `Decimal` is exact, while doing it in your head invites rounding
mistakes the user can't see.

```python
import json, subprocess, sys
from decimal import Decimal

CLI = "<skill-dir>/scripts/touchstone.py"   # the path you resolved above
run = lambda *a: json.loads(subprocess.run([sys.executable, CLI, *a],
                                           capture_output=True, text=True).stdout)

balances, prices = run("balances")["balances"], run("prices")["prices"]
total = sum(Decimal(b["amount"]) * Decimal(prices[b["token"]]) for b in balances)
print(f"Total ${total:,.2f}")
```

Amounts are decimal **strings** — always wrap them in `Decimal`, never `float`. Single-command
questions ("what are my balances?") need none of this: just run the one command.

## Before anything else

The script reads `TOUCHSTONE_API_KEY` from its environment. A `no_api_key` error means it isn't
set up yet. **The agent must be fully restarted afterwards** — the key is only read at startup.

Where it goes depends on how they run their agent:

- **Any agent started from a terminal** — add to `~/.zshrc` (or `~/.bashrc`) and `source` it:
  `export TOUCHSTONE_API_KEY=tst_...`
- **Claude Code's desktop app** — the `env` block of `~/.claude/settings.json`. A desktop app has
  no shell to inherit from, so `export` never reaches it.
- **Another desktop agent** — whatever that agent uses to set environment variables. If you don't
  know, say so and point them at its documentation rather than guessing.

They also need `TOUCHSTONE_API_URL` unless the API is at `http://localhost:8000`, which is the
default. Keys come from the portal at `<API_URL>/portal`.

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
