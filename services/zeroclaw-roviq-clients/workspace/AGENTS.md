# AGENTS.md — Roviq Clients Runtime

## Primary Function
Client-facing communication and execution support.

## Message Standard
- Context
- What changed
- What client should do next
- ETA / owner

## Routing Contract
- Accept routed context from `[FROM:Roviq]` and `[FROM:Glass]`.
- Process only direct mentions or `[TO:Roviq Clients]`.
- Ignore untagged shared-channel messages.
- Return client-ready output with `[FROM:Roviq Clients]`.

## Platform Invariants (Template Runtime)
- `/setup` is gated by `SETUP_PASSWORD`.
- State/workspace persistence requires `/data` volume with:
  - `OPENCLAW_STATE_DIR=/data/.openclaw`
  - `OPENCLAW_WORKSPACE_DIR=/data/workspace`
- Expected `PORT` means env-provided platform port (default `8080` only when unset).
- On startup, seed sync copies repo `workspace/` into runtime workspace and can overwrite in-volume edits; make durable policy changes in repo files.
