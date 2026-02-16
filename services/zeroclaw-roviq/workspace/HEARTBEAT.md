# HEARTBEAT.md — Roviq Ops Agent

Run every 15 minutes:
1. Check shared Discord channel for unhandled tagged requests.
2. Process only messages that explicitly tag a bot or include [TO:...].
3. If unowned tagged tasks exist, claim and route.
4. Post concise status or blocker update.
5. Escalate only if blocked >1 cycle.

Rules:
- No auto-routing on untagged messages.
- Require explicit mention/tag for action.
