# Releasing a change to teammates

For whoever maintains this plugin. Teammates only need `README.md`.

## The one rule

**Claude Code decides whether to update by comparing version numbers, not file contents.**

If you change a file and push without bumping `version` in `.claude-plugin/plugin.json`, every
teammate who runs the update commands is told *"already at the latest version"* and keeps running
the old code. Nothing warns you. Their plugin is silently stale.

So: **every push that changes plugin behaviour needs a version bump.**

## Steps

1. Make your change.

2. Bump `version` in `.claude-plugin/plugin.json`:
   - patch (`0.2.0` → `0.2.1`) — wording, a bug fix, nothing teammates must act on
   - minor (`0.2.0` → `0.3.0`) — a new command, changed setup steps
   - major (`0.2.0` → `1.0.0`) — something that breaks an existing setup

3. Commit and push.

4. Verify it from a consumer's point of view, on your own machine:

   ```bash
   claude plugin marketplace update touchstone-exchange
   ```

   ```bash
   claude plugin update touchstone
   ```

   It must say `updated from <old> to <new>`. If it says *already at the latest version*, you
   forgot the bump — fix it and push again.

5. Tell teammates to run those same two commands, then restart Claude Code.

## Checking what's actually installed

The files that really run live here:

```bash
ls ~/.claude/plugins/cache/touchstone-exchange/touchstone/
```

One directory per installed version. If you're debugging "my change isn't showing up", look at the
file inside the *current* version directory — not the repo, and not
`~/.claude/plugins/marketplaces/`, which is only the fetched copy.

## If you're editing the plugin locally

Point the marketplace at your working folder instead of GitHub, so edits apply with no push and no
version bump:

```bash
claude plugin marketplace remove touchstone-exchange
```

```bash
cd ~/touchstone-agent && claude plugin marketplace add ./
```

```bash
claude plugin install touchstone@touchstone-exchange
```

A local-directory install reads straight from the folder. Switch back to the GitHub source before
testing what a teammate will actually get.

## Don't forget the API

The plugin is only the client. If you change the API's responses or error codes, update
`skills/touchstone/references/api.md` to match and release a new version — otherwise the agent is
working from stale documentation, which fails quietly rather than loudly.
