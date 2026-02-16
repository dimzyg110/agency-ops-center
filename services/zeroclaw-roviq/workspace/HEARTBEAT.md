# HEARTBEAT.md — Roviq Ops Agent

Run every 15 minutes:
1. Check for unhandled tasks tagged `[TO:Roviq]` or direct mentions.
2. Process only direct mentions or `[TO:Roviq]` messages.
3. Claim only unowned `[TO:Roviq]` tasks; do not claim tags owned by other lanes.
4. Post concise status updates (done / blocked / ETA).
5. Escalate blockers older than 1 heartbeat cycle.

Operational checks:
- Confirm routing discipline is being followed (no auto-routing of untagged messages).
- If deployment issues are reported, verify setup/runtime prerequisites:
  - `SETUP_PASSWORD` present
  - `/data` volume mounted
  - service reachable on expected `PORT` (env-provided; default `8080` only when unset)

Rules:
- No auto-routing on untagged messages.
- Require explicit mention/tag for action.
