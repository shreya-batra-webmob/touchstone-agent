# Touchstone Exchange API reference (read-only commands)

Read this only when you need exact response shapes, error codes or limits.
Everything here is reached through the bundled script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/touchstone/scripts/touchstone.py" <command>
```

## Authentication

The script sends `Authorization: Bearer $TOUCHSTONE_API_KEY`. Keys look like `tst_` followed by 32
random characters and a 6-character checksum. A typo is rejected by the checksum before the server
even looks it up, so `invalid_api_key` on a freshly pasted key usually means it was copied short.

Keys carry scopes. All four commands here need the `read` scope. A key with only `trade` can call
`me` but nothing else.

## Commands and what they return

### `me`
```json
{"user_id":"usr_...","email":"you@example.com","key_id":"key_...","scopes":["read"]}
```
The cheapest way to check that the key, the network and the server are all working.

### `prices`
```json
{"currency":"USD","prices":{"BTC":"60000.00","ETH":"3000.00","USDC":"1.00"}}
```
Prices are fixed constants in this sandbox. They never move.

### `balances`
```json
{"balances":[{"token":"BTC","amount":"0.05"},{"token":"ETH","amount":"1.0"},{"token":"USDC","amount":"1000.00"}]}
```
A new account starts with 0.05 BTC, 1.0 ETH and 1000.00 USDC.

### `trades --limit N`
```json
{"trades":[{"trade_id":"trd_...","from":{"token":"ETH","amount":"0.1"},"to":{"token":"USDC","amount":"299.7"},"fee_usd":"0.30","executed_at":1792566538}]}
```
Newest first. `executed_at` is a Unix timestamp. An account that has never traded returns
`{"trades":[]}` — that is success, not an error.

## Amounts are strings, not numbers

Every amount is a decimal **string** (`"0.1"`, not `0.1`). This is deliberate: floating point
cannot represent most decimal money exactly. When you do arithmetic for the user, treat these as
exact decimals and don't introduce rounding the server didn't do.

## Error format

Every failure, without exception:

```json
{"error":{"code":"...","message":"...","hint":"..."}}
```

It goes to **stderr**, and the exit code is non-zero. The `hint` is written to be acted on.

| Code | Meaning | What to do |
|---|---|---|
| `no_api_key` | `TOUCHSTONE_API_KEY` not set (exit 2) | Ask the user to export it and restart the agent. |
| `connection_failed` | Server unreachable (exit 2) | Check the server is running and `TOUCHSTONE_API_URL` is right. |
| `missing_api_key` | No header reached the server | Usually the same fix as `no_api_key`. |
| `invalid_api_key` | Wrong, revoked or expired | Ask for a new key. Revoked and unknown look identical on purpose. |
| `insufficient_scope` | Key lacks the `read` scope | The user needs a key created with `read`. |
| `rate_limited` | Too many calls for this key | The script already retries with the server's `Retry-After`. If it still fails, wait and stop calling. |
| `too_many_auth_failures` | Too many bad keys from this address | Stop retrying. The key is wrong; fix it before calling again. |

## Rate limits and retries

The default limit is 60 requests per minute per key. The script retries only on network failures
and `429`, at most twice, honouring `Retry-After`. It never retries other 4xx errors, because
repeating an identical bad request cannot succeed and only burns the limit.

Don't loop commands. These responses are small and change rarely — call once and reuse what you got.

## What this skill cannot do

There are no commands to quote, swap, buy or sell. The write flow exists on the server but is not
exposed here. If the user asks to trade, tell them plainly that this version is read-only.
