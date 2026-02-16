# OpenClaw Setup Export

This folder snapshots the current operating setup used by the Roviq OpenClaw COO agent.

## Included

### `core/`
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `HEARTBEAT.md`
- `TOOLS.md`
- `IDENTITY.md`
- `MEMORY.md`

### `team/`
- `WORKFLOW.md`
- `ORCHESTRATOR.md`
- `DEVELOPER.md`
- `QA.md`
- `RESEARCHER.md`
- `DESIGNER.md`

## Purpose

Use this as a portable baseline to recreate the same operating style, role definitions, heartbeat behavior, and team workflow in another OpenClaw deployment.

## Notes

- This is a repo copy only. It does **not** include external secrets, auth profiles, or `.env` credentials.
- Keep secrets in your deployment platform secret manager.
- If you want a full infra pack (VPS bootstrap + service files), add it under `infra/` and keep this folder as the agent-ops layer.
