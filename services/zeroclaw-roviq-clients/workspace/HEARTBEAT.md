# HEARTBEAT.md — Roviq Clients Agent

Run every 15 minutes:
1. Check for `[TO:Roviq Clients]` or direct mentions.
2. Respond only to explicitly tagged requests.
3. Convert approved internal context into client-ready language.
4. Post concise updates with clear next step + owner.
5. Escalate blockers older than 1 heartbeat cycle.

Operational checks:
- Confirm no untagged message was auto-processed.
- If deployment/runtime issues are reported, verify:
  - `SETUP_PASSWORD` present
  - `/data` volume mounted
  - service reachable on expected `PORT` (env-provided; default `8080` only when unset)

Rules:
- Ignore untagged messages.
- No auto-routing from plain messages.
