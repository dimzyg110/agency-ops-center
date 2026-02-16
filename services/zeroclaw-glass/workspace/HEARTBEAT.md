# HEARTBEAT.md — Glass Intelligence Agent

Run every 15 minutes:
1. **Load canonical tracker** — `services/zeroclaw/workspace/TASK-TRACKER.md`
2. **Recover active task on restart** — if any task owned by `@glass` is in active state, resume it immediately
3. **Apply state logic**
   - `PR_OPEN` / `IN_REVIEW` → wait, post status with PR age
   - `CHANGES_REQUESTED` → return to `IN_PROGRESS` immediately on the same task
   - no active task → claim highest-priority `UNCLAIMED` task assigned to `@glass`
4. **Work and update state** — keep `updated_at`, `pr_url`, and `blocker_reason` current
5. **Escalate by threshold**
   - blocker > 60 minutes → escalate
   - PR waiting review > 4 hours → escalate as stale PR

## Required State Machine
`UNCLAIMED → CLAIMED → IN_PROGRESS → PR_OPEN → IN_REVIEW → CHANGES_REQUESTED → APPROVED → MERGED → DONE`

Transition rules:
- Only valid transitions are allowed.
- No new task while one is in active states: `CLAIMED`, `IN_PROGRESS`, `PR_OPEN`, `IN_REVIEW`, `CHANGES_REQUESTED`.
- `CHANGES_REQUESTED` always returns to `IN_PROGRESS` for the same task.

## Task Tracking
- Source of truth: `services/zeroclaw/workspace/TASK-TRACKER.md`
- Include task ID + PR URL in every status update
- Do not mark done without merged PR + `DONE` state

## Operational Checks
- `SETUP_PASSWORD` exists
- `/data` volume attached
- service bound to expected `PORT`

## Rules
- ONE TASK AT A TIME — see SOUL.md
- Ignore untagged chatter
- No auto-routing from plain messages