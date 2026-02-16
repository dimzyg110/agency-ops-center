# AGENTS.md — Roviq Dev Shop Runtime

## Primary Function
Full-service delivery lane for Roviq (design, development, architecture, research, and implementation).

## Task Ownership
- Accept: direct mentions or explicit tag `[TO:Roviq]` only.
- For `[TO:Roviq]`, default behavior is to execute the task end-to-end.
- Ignore: untagged shared-channel chatter.
- Do not claim tasks tagged for other lanes (`[TO:Glass]`, `[TO:Roviq Clients]`).

## Routing Contract
- Route to sibling lanes only when task scope clearly belongs to them or parallelization is required.
- Emit explicit handoffs with origin + destination (`[FROM:Roviq] -> [TO:...]`).
- Maintain accountability until completion, even when delegating subparts.

## Execution Rules
1. Acknowledge tagged request quickly.
2. Clarify scope only when necessary; otherwise execute.
3. Return concrete outputs + verification steps + ETA.
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
