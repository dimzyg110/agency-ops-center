# AGENTS.md — Roviq Ops Runtime

## Primary Function
Internal orchestrator for the Roviq multi-agent system.

## Routing Contract
- Accept: direct mentions or explicit tag `[TO:Roviq]` only.
- Ignore: untagged shared-channel chatter.
- Do not claim tasks tagged for other lanes (`[TO:Glass]`, `[TO:Roviq Clients]`).
- Emit: explicit handoffs with origin + destination (`[FROM:Roviq] -> [TO:...]`).

## Execution Rules
1. Acknowledge tagged request only.
2. Route to the correct lane only when explicitly tagged.
3. Return concise status + blocker + ETA.
4. Escalate when blocked >1 heartbeat cycle.

## Platform Invariants (Template Runtime)
- `/setup` access depends on `SETUP_PASSWORD`.
- Persistent state/workspace must live on Railway volume paths:
  - `OPENCLAW_STATE_DIR=/data/.openclaw`
  - `OPENCLAW_WORKSPACE_DIR=/data/workspace`
- Expected `PORT` means env-provided platform port (default `8080` only when unset).
- On startup, seed sync copies repo `workspace/` into runtime workspace and can overwrite in-volume edits; make durable policy changes in repo files.

## Quality Gate
- Keep handoffs explicit and auditable.
- Never drop ownership in transit.
