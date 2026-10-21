# Touchstone Exchange — Claude Code plugin

Ask Claude Code about your Touchstone Exchange account in plain English:

> "What are my Touchstone balances?"

It answers by calling the Touchstone API for you. **Read-only** — it can look things up, but it
cannot trade, move or spend anything.

Setup takes about 5 minutes. Follow the steps in order.

---

## Before you start

You need three things:

| | How to check |
|---|---|
| **Claude Code** installed | `claude --version` prints a version |
| **Python 3** installed | `python3 --version` prints 3.8 or higher |
| **Access to this repo** | You can open it on GitHub without a 404 |

If the repo 404s, ask Shreya for read access — it's private.

You also need the **API address**:

```
https://touchstone.example.com
```
---

## Step 1 — Install the plugin

Run these two commands anywhere:

```bash
claude plugin marketplace add shreya-batra-webmob/touchstone-agent
```

```bash
claude plugin install touchstone@touchstone-exchange
```

Check it worked:

```bash
claude plugin list
```

You should see `touchstone@touchstone-exchange` with **Status: ✔ enabled**.

<details>
<summary>It said "Repository not found"</summary>

Your git can't read the private repo. Test with:

```bash
ssh -T git@github.com
```

It should greet you by username. If it doesn't, add an SSH key to your GitHub account, then ask
Shreya to confirm you have access to the repo.
</details>

---

## Step 2 — Get your own API key

Open the portal in your browser:

```
https://touchstone.example.com/portal
```

1. Type your email and a password of **at least 10 characters**.
2. Click **Create account**. (Don't press Enter — that tries to log in, and you don't have an
   account yet.)
3. You'll land on the dashboard. Under **Create a key**, give it a name like `laptop`, leave the
   **read** scope ticked, and click **Create key**.
4. Your key appears once, starting with `tst_`. Click **Copy**.

**Copy it now — you cannot see it again.** If you lose it, make another one and revoke the old one
from the same page.

Nobody needs to send you a key. You make your own, and it never travels through chat or email.

---

## Step 3 — Put the key in your shell

Open a terminal and run these two lines, pasting your key into the first:

```bash
export TOUCHSTONE_API_KEY=tst_paste_your_key_here
```

```bash
export TOUCHSTONE_API_URL=https://touchstone.example.com
```

To avoid redoing this every time, add both lines to the end of `~/.bashrc` (or `~/.zshrc` if you
use zsh), then run `source ~/.bashrc`.

> Keep the key in the environment like this. Never paste it into a chat, a command argument, or a
> file you commit — arguments and chat transcripts get stored and shared.

---

## Step 4 — Start Claude Code from that same terminal

```bash
claude
```

**This matters.** The plugin reads the key from the terminal Claude Code was launched from. If you
set the variables in one window and start Claude Code in another, it won't find them.

Already had Claude Code open? Quit it and start it again from the terminal where you ran step 3.

---

## Step 5 — Try it

Ask any of these:

- *What are my Touchstone balances?*
- *What's ETH worth on the Touchstone exchange?*
- *Is my Touchstone API key working?*
- *Show me my recent Touchstone trades*

A new account starts with 0.05 BTC, 1.0 ETH and 1000.00 USDC, and no trades. An empty trade list is
normal, not an error.

If Claude doesn't seem to use the plugin, say **"Touchstone"** in your question — that's the word
that tells it which tool to reach for.

---

## If something goes wrong

First, check the key is actually in this terminal:

```bash
echo "${TOUCHSTONE_API_KEY:0:8}... ${TOUCHSTONE_API_URL}"
```

It should print `tst_...` and the API address. Blank means step 3 didn't stick in this window.

Then run the plugin's own script — it prints the real error:

```bash
python3 "$(find ~/.claude/plugins -name touchstone.py | head -1)" me
```

| What you see | What it means | Fix |
|---|---|---|
| `no_api_key` | The key isn't in this terminal's environment | Redo step 3, then restart Claude Code from that same terminal |
| `connection_failed` | Can't reach the API | Check `TOUCHSTONE_API_URL`. On a work network you may need the VPN |
| `invalid_api_key` | Key is wrong, revoked or expired | Make a new key (step 2). A short copy-paste is the usual cause |
| `insufficient_scope` | Key has no **read** scope | Make a new key with **read** ticked |
| `rate_limited` | Too many requests for one key | Wait a minute. It retries on its own |
| Claude ignores the plugin | It didn't match your wording | Say "Touchstone" in the question |

Still stuck? Send Shreya the exact error text — it says what's wrong and how to fix it.

---

## Updating and removing

Get the latest version:

```bash
claude plugin marketplace update touchstone-exchange
```

Remove it:

```bash
claude plugin uninstall touchstone@touchstone-exchange
```

Lost or leaked your key? Revoke it in the portal and create a new one. Revoking is instant and
affects only that one key — nobody else is disturbed.

---

## What it can and can't do

**Can:** show your balances, token prices, who your key belongs to, and your past trades.

**Can't:** trade, swap, buy, sell, or move anything. There is no command for it in this plugin, so
it can't happen by accident. If you ask Claude to trade, it will say it isn't available.

---

## Running it locally instead

Only needed if the API isn't hosted yet, or you want your own private sandbox.

Clone the server repo (`touchstone-api`), then:

```bash
pip install -r requirements.txt && uvicorn server.main:app --port 8000
```

The portal is then at `http://localhost:8000/portal`, and you can skip `TOUCHSTONE_API_URL` — it
defaults to `http://localhost:8000`.

Prefer the terminal to the portal? This plugin also ships `get_key.sh`, which does the same job:

```bash
./get_key.sh
```

---

## For the curious: how it works

```
.claude-plugin/
├── marketplace.json     lets `claude plugin marketplace add` find the plugin
└── plugin.json          the plugin manifest
get_key.sh               makes an API key from the terminal
skills/touchstone/
├── SKILL.md             what Claude reads when your question matches
├── references/api.md    error codes and response shapes (read only when needed)
└── scripts/touchstone.py    the script Claude runs. Python standard library only
```

Claude loads the skill in three stages, so it costs almost nothing until you need it: the name and
one-line description at startup (~100 tokens), the full `SKILL.md` only when a question matches,
and `references/api.md` only when it needs that detail. All the exchange logic lives behind the
API — this repo is just the client.

Using claude.ai in a browser rather than Claude Code? Skills run in a sandbox there, so you must
enable code execution and add the API's domain to your allowlist under **Settings → Capabilities**.
A `localhost` address won't work from that sandbox.
