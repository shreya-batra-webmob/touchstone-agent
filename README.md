# Touchstone Exchange agent plugin (read-only)

A Claude Code plugin that bundles one Agent Skill. The skill teaches the agent four read-only
commands against the Touchstone Exchange API: `me`, `prices`, `balances`, `trades`.

Read-only on purpose: there is no quote, swap or execute command here, so nothing this plugin
does can move money.

## What's in it

```
.claude-plugin/
├── marketplace.json     lets `marketplace add <org>/<repo>` find the plugin
└── plugin.json          the plugin manifest
get_key.sh               makes your own API key against the hosted API
skills/touchstone/
├── SKILL.md             what the agent loads when a task matches (~60 lines)
├── references/api.md    response shapes, error codes, limits (loaded only when needed)
└── scripts/touchstone.py    the CLI the agent runs. Standard library only, no pip install.
```

This repo is the **client half only**. The API it talks to lives in a separate, private repo and
is hosted; this plugin never contains any exchange logic.

**Why it's shaped this way.** At startup the agent loads only the skill's `name` and `description`
— about 100 tokens. It reads the full `SKILL.md` only when a task looks relevant, and
`references/api.md` only when it needs that detail. An MCP server would instead push every tool's
full schema into the model's context on every conversation.

## Install it (for teammates)

Ask whoever runs the exchange for the **API URL** before you start. Then:

### 1. Install the plugin

```bash
claude plugin marketplace add YOUR-ORG/YOUR-REPO
```

```bash
claude plugin install touchstone@touchstone-exchange
```

If the repo is private, make sure your `gh` CLI or git credentials can read it first.

### 2. Get your own API key

Open the portal in a browser and sign up:

```
https://touchstone.example.com/portal
```

Create a key with the **read** scope, then copy it — it is shown once and never again.

Prefer the terminal? `get_key.sh` ships with this plugin and does the same thing:

```bash
TOUCHSTONE_API_URL=https://touchstone.example.com ./get_key.sh
```

Either way, **nobody needs to send you a key** — you make your own, and it never travels through
chat or email. Lost it? Make a new one and revoke the old one in the portal.

### 3. Put the key in your environment

```bash
export TOUCHSTONE_API_KEY=tst_your_key_here
export TOUCHSTONE_API_URL=https://touchstone.example.com
```

**The key goes in the environment, never in a command-line argument** — arguments end up in shell
history, process lists and agent transcripts.

### 4. Start Claude Code from that same shell

This matters: the skill's script inherits the environment of the shell Claude Code was started
from. Export the variables first, then launch. Then ask:

- "What are my Touchstone Exchange balances?"
- "What's ETH worth on the Touchstone exchange?"
- "Is my Touchstone Exchange key working?"
- "Show me my recent Touchstone exchange trades"

To remove it again: `claude plugin uninstall touchstone@touchstone-exchange`

### Getting updates later

```bash
claude plugin marketplace update touchstone-exchange
```

## Running the API yourself instead

If you'd rather not depend on a hosted API, run the server project locally, then:

```bash
./get_key.sh
```

`TOUCHSTONE_API_URL` defaults to `http://localhost:8000`, so you can leave it unset.

Installing from a local checkout rather than git (note the `./` — a bare `.` is rejected):

```bash
claude plugin marketplace add ./
```

### Alternative: skip the plugin wrapper

The skill works on its own, without the marketplace:

```bash
mkdir -p ~/.claude/skills && cp -r skills/touchstone ~/.claude/skills/
```

One catch: `${CLAUDE_PLUGIN_ROOT}` only exists for installed plugins. Copied this way, point the
agent at `~/.claude/skills/touchstone/scripts/touchstone.py` instead.

## Try the CLI directly

Useful for checking your setup before involving an agent:

```bash
python3 ./skills/touchstone/scripts/touchstone.py me
```

```bash
python3 ./skills/touchstone/scripts/touchstone.py balances
```

Success prints one line of compact JSON and exits 0. Failures print
`{"error": {"code", "message", "hint"}}` to stderr and exit non-zero — `2` means it never reached
the server (bad setup), `1` means the server refused the request.

## Using it on claude.ai instead of Claude Code

Skills run in a sandbox there. The user has to enable code execution and add the API's domain to
their domain allowlist under **Settings → Capabilities**. A `localhost` server is not reachable
from that sandbox, so the API has to be on a public URL for this to work.

## Hosting the API for a team

Hosting is the server project's job, not this plugin's — see its `DEPLOY.md`. The short version:
HTTPS is mandatory because API keys ride in every request header, `TOUCHSTONE_ENV=prod` and a saved
`TOUCHSTONE_KEY_PEPPER` are required, and the per-IP rate limiter needs fixing or one person's bad
key will lock out the whole team.

## Not in this version

No trading. The server has a full quote → approve → execute flow with expiring, single-use,
idempotent quotes, but none of it is exposed here. Adding it means a `quote` command, an
`execute --confirmed` command, and a reference file with the approval rules — the safety-critical
part, which deserves its own pass.
