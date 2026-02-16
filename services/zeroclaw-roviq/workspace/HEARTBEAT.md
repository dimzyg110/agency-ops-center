# HEARTBEAT.md — Roviq Ops Agent

Run every 15 minutes:
1. **Check for tasks** — unhandled `[TO:Roviq]` or direct mentions
2. **Check task status** — do you have an open PR waiting for review? If yes, wait. Don't start new work.
3. **If no open PR** — pick the highest priority task and work it
4. **Post status** — done / blocked / ETA in channel
5. **Escalate** — blockers older than 1 heartbeat cycle

## Task Tracking
- Track open PRs: note PR # in your status
- If PR in review → wait, don't start new task
- Only move to next task after current PR is merged

## Operational Checks
- `SETUP_PASSWORD` present
- `/data` volume mounted
- service reachable on expected `PORT`

## Rules
- ONE TASK AT A TIME — see SOUL.md
- No auto-routing on untagged messages
- Require explicit mention/tag for action
