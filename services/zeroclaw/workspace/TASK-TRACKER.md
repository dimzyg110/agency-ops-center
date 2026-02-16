# TASK-TRACKER.md — Canonical Task State

Last updated: 2026-02-16 UTC
Owner: @roviq (queue integrity), all lanes (state updates)

## Purpose
Single source of truth for task ownership, progress state, PR linkage, and blockers across lanes.

## Required Fields
Each task entry must include:
- `task_id`
- `owner`
- `priority`
- `state`
- `pr_url`
- `updated_at`
- `blocker_reason`

## State Machine (Required)
`UNCLAIMED → CLAIMED → IN_PROGRESS → PR_OPEN → IN_REVIEW → CHANGES_REQUESTED → APPROVED → MERGED → DONE`

### Transition Rules
- Only move forward through valid transitions.
- `CHANGES_REQUESTED` must transition back to `IN_PROGRESS` on the same task (no task switching).
- `DONE` is terminal and requires merged PR evidence.
- One-task lock per lane: maximum one active task in states `CLAIMED`, `IN_PROGRESS`, `PR_OPEN`, `IN_REVIEW`, or `CHANGES_REQUESTED`.

## Task Table

| task_id | owner | priority | state | pr_url | updated_at (UTC) | blocker_reason |
|---|---|---|---|---|---|---|
| TASK-001 | @glass | P0 | UNCLAIMED |  | 2026-02-16T00:00:00Z |  |
| TASK-002 | @clients | P0 | UNCLAIMED |  | 2026-02-16T00:00:00Z |  |
| TASK-003 | @roviq | P0 | UNCLAIMED |  | 2026-02-16T00:00:00Z |  |

## Update Protocol
1. Claim task: set `owner`, set `state=CLAIMED`, update `updated_at`.
2. Start execution: set `state=IN_PROGRESS`.
3. Open PR: set `state=PR_OPEN`, add `pr_url`.
4. Review running: set `state=IN_REVIEW`.
5. If review asks changes: set `state=CHANGES_REQUESTED` then immediately back to `IN_PROGRESS` while applying fixes.
6. Approval: set `state=APPROVED`.
7. Merge complete: set `state=MERGED`, then `DONE` once post-merge checks/handoffs are complete.
8. If blocked at any state: fill `blocker_reason` and refresh `updated_at` every heartbeat until resolved.
