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

## Step 3 — Put your key in Claude Code's settings file

This is the one method that works everywhere — terminal **and** the desktop app, on every OS.

You are adding an `env` block to `settings.json`. Claude Code reads it at startup and passes those
values to the plugin.

### Where the file is

| OS | Path |
|---|---|
| **macOS** | `~/.claude/settings.json` |
| **Linux** | `~/.claude/settings.json` |
| **Windows** | `C:\Users\<your-name>\.claude\settings.json` |

If the folder or file doesn't exist yet, create it:

**macOS / Linux**
```bash
mkdir -p ~/.claude && touch ~/.claude/settings.json
```

**Windows (PowerShell)**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude" | Out-Null
```

### Open it

**macOS**
```bash
open -e ~/.claude/settings.json
```

**Linux**
```bash
nano ~/.claude/settings.json
```

**Windows (PowerShell)**
```powershell
notepad "$env:USERPROFILE\.claude\settings.json"
```

### What to add

If the file is **empty**, paste exactly this, with your own key and the API address:

```json
{
  "env": {
    "TOUCHSTONE_API_KEY": "tst_paste_your_key_here",
    "TOUCHSTONE_API_URL": "https://touchstone.example.com"
  }
}
```

If the file **already has settings in it**, add `env` alongside what's there — don't replace the
file. For example, if it currently looks like this:

```json
{
  "model": "claude-opus-5",
  "theme": "dark"
}
```

it should end up like this (note the comma after `"dark"`):

```json
{
  "model": "claude-opus-5",
  "theme": "dark",
  "env": {
    "TOUCHSTONE_API_KEY": "tst_paste_your_key_here",
    "TOUCHSTONE_API_URL": "https://touchstone.example.com"
  }
}
```

> ⚠️ **`env` goes at the top level.** Not inside `pluginConfigs`, not inside `permissions`. A key
> in the wrong block is silently ignored — the plugin will just say `no_api_key` and you'll have no
> idea why.

### Check the file is still valid JSON

One missing comma breaks **all** your Claude Code settings, not just this plugin. Verify before you
restart:

**macOS / Linux**
```bash
python3 -m json.tool ~/.claude/settings.json > /dev/null && echo "valid JSON"
```

**Windows (PowerShell)**
```powershell
Get-Content "$env:USERPROFILE\.claude\settings.json" | ConvertFrom-Json | Out-Null; "valid JSON"
```

If it prints an error, fix the spot it names — usually a missing or extra comma.

### Lock the file down

Your key sits in this file in plain text, so stop other accounts on the machine reading it:

**macOS / Linux**
```bash
chmod 600 ~/.claude/settings.json
```

**Windows (PowerShell)**
```powershell
icacls "$env:USERPROFILE\.claude\settings.json" /inheritance:r /grant:r "$env:USERNAME:(R,W)"
```

> **Keep it in your home folder — never in a project's `.claude/settings.json`.** That one gets
> committed to git. And never paste the key into a chat, a command argument, or a ticket: command
> arguments end up in shell history and chat transcripts are stored.
>
> If it does leak, it's not a crisis — revoke it in the portal and make a new one. Takes seconds
> and affects nobody else.

### Prefer the terminal? (optional, terminal-only)

If you only ever run `claude` from a terminal, a shell profile works too — add to `~/.zshrc` or
`~/.bashrc`, then `source` it:

```bash
export TOUCHSTONE_API_KEY=tst_paste_your_key_here
export TOUCHSTONE_API_URL=https://touchstone.example.com
```

This does **not** reach the desktop app — it has no shell to inherit from. If you use both, use the
settings file.

---

## Step 4 — Fully restart Claude Code

The key is only read at **startup**, so this won't work until you restart.

- **Desktop app (macOS)** — ⌘Q. Closing the window is not enough.
- **Desktop app (Windows)** — quit from the system tray, not just the window ✕.
- **Terminal** — quit Claude Code and start it again. If you used the shell-profile method, start
  it from the terminal where you set the variables.

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

**The quickest check: ask Claude *"Is my Touchstone API key working?"*** — it runs the check and
shows you the exact error.

If you're on the terminal setup, you can also confirm the key is in that shell:

```bash
echo "${TOUCHSTONE_API_KEY:0:8}... ${TOUCHSTONE_API_URL}"
```

It should print `tst_...` and the API address. Blank means step 3 didn't stick in this window.
(On the desktop app this will print blank even when things are fine — the key lives in
`~/.claude/settings.json`, not in your shell.)

To see the raw error yourself:

```bash
python3 "$(find ~/.claude/plugins -name touchstone.py | head -1)" me
```

| What you see | What it means | Fix |
|---|---|---|
| `no_api_key` | Claude Code can't see the key | Redo step 3 for **your** setup, then fully restart Claude Code. Desktop app users: check `~/.claude/settings.json` is valid JSON |
| `connection_failed` | Can't reach the API | Check `TOUCHSTONE_API_URL`. On a work network you may need the VPN |
| `invalid_api_key` | Key is wrong, revoked or expired | Make a new key (step 2). A short copy-paste is the usual cause |
| `insufficient_scope` | Key has no **read** scope | Make a new key with **read** ticked |
| `rate_limited` | Too many requests for one key | Wait a minute. It retries on its own |
| Claude ignores the plugin | It didn't match your wording | Say "Touchstone" in the question |

Still stuck? Send Shreya the exact error text — it says what's wrong and how to fix it.

---

## Getting updates

When a new version is released, run **both** commands. The first fetches the latest release
info, the second actually installs it:

```bash
claude plugin marketplace update touchstone-exchange
```

```bash
claude plugin update touchstone
```

Then **restart Claude Code** — it tells you to when the update lands.

Check which version you're on any time with `claude plugin list`.

> Running only the first command looks like it worked — it says "Successfully updated
> marketplace" — but leaves the plugin itself untouched. You need both.

---

## Removing it

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
