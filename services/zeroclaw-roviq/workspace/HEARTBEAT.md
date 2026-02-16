# HEARTBEAT.md — Roviq Ops Agent

Run every 15 minutes:
1. **Load canonical tracker** — `services/zeroclaw/workspace/TASK-TRACKER.md`
2. **Recover active task on restart** — if any task owned by `@roviq` is in active state, resume it immediately
3. **Apply state logic**
   - `PR_OPEN` / `IN_REVIEW` → wait, track review SLA and PR age
   - `CHANGES_REQUESTED` → return to `IN_PROGRESS` immediately on the same task
   - no active task → claim highest-priority `UNCLAIMED` task assigned to `@roviq`
4. **Enforce queue hygiene** — one-task lock per lane, clear owners, fresh timestamps
5. **Escalate by threshold**
   - blocker > 60 minutes → escalate
   - PR waiting review > 4 hours → escalate as stale PR

## Required State Machine
`UNCLAIMED → CLAIMED → IN_PROGRESS → PR_OPEN → IN_REVIEW → CHANGES_REQUESTED → APPROVED → MERGED → DONE`

Transition rules:
- Only valid transitions are allowed.
- No new task while one is in active states: `CLAIMED`, `IN_PROGRESS`, `PR_OPEN`, `IN_REVIEW`, `CHANGES_REQUESTED`.
- `CHANGES_REQUESTED` always returns to `IN_PROGRESS` for the same task.

## Review Protocol
- Reviews must follow `team/QA.md` format.
- Ensure reviewer assignment immediately after `PR_OPEN`.
- Track and escalate review SLA breaches.

## Task Tracking
- Source of truth: `services/zeroclaw/workspace/TASK-TRACKER.md`
- Include task ID + PR URL in every status update
- Do not mark done without merged PR + `DONE` state

## Operational Checks
- `SETUP_PASSWORD` present
- `/data` volume mounted
- service reachable on expected `PORT`

## Rules
- ONE TASK AT A TIME — see SOUL.md
- No auto-routing on untagged messages
- Require explicit mention/tag for action