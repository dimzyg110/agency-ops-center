# HEARTBEAT.md — Glass Intelligence Agent

Run every 15 minutes:
1. Check shared channel for `[TO:Glass]` or direct mention.
2. Respond only to explicitly tagged requests.
3. For unresolved data requests, post status + ETA.
4. Hand off outputs with explicit routing tags.
5. Escalate blockers older than 1 heartbeat cycle.

Operational checks:
- Confirm no untagged message was auto-claimed.
- If runtime/deploy concerns appear, verify:
  - `SETUP_PASSWORD` exists
  - `/data` volume is attached
  - service is bound to expected `PORT` (env-provided; default `8080` only when unset)

Rules:
- Ignore untagged chatter.
- No auto-routing from plain messages.
