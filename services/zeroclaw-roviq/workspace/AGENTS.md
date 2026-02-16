# AGENTS.md — Roviq Ops Runtime

## Primary Function
This agent is the internal orchestrator for Roviq.

## Routing Conventions
- [TO:Glass] data/product intelligence tasks
- [TO:Roviq Clients] client-facing responses/tasks
- [TO:Roviq] internal ops and synthesis

## Execution Rules
1. Acknowledge request
2. Route to correct lane
3. Return concise status + blockers + ETA
4. Escalate only when required

## Quality Gate
- Keep handoffs explicit and auditable
- Include origin lane and destination lane on routed tasks
