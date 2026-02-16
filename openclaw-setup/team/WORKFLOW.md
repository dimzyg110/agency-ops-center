# TEAM WORKFLOW

_The end-to-end pipeline for how work moves through the system. This is the single source of truth._

---

## The Pipeline

Every piece of work follows this pipeline. No shortcuts, no skipping steps.

```
REQUEST → DECOMPOSE → ASSIGN → EXECUTE → REVIEW → INTEGRATE → DELIVER
   │          │           │         │          │          │          │
   │          │           │         │          │          │          └─ Client/project updated
   │          │           │         │          │          └─ Commit, push, update dashboard
   │          │           │         │          └─ 2 independent reviewers, different models
   │          │           │         └─ Specialist builds deliverable
   │          │           └─ Orchestrator spawns specialist with precise task prompt
   │          └─ Orchestrator breaks into atomic tasks with dependencies
   └─ User request or client brief arrives
```

---

## Stage Details

### 1. REQUEST

**Input:** User message, client brief, or orchestrator-identified task
**Gate:** Requirements are clear enough to decompose

If requirements are ambiguous:

- Ask the user for clarification (don't guess on scope)
- Reference the client brief at `clients/[name]/BRIEF.md` for context
- Check `DASHBOARD.md` for current priorities

### 2. DECOMPOSE

**Owner:** Orchestrator
**Gate:** Every subtask has clear success criteria and an assigned specialist type

The orchestrator:

- Maps the dependency graph
- Identifies the critical path
- Sizes each task (S/M/L)
- Determines parallel vs. sequential execution

See [ORCHESTRATOR.md](file:///Users/randytorres/Projects/agency-ops-center/team/ORCHESTRATOR.md) → Cognitive Architecture for the full decomposition protocol.

### 3. ASSIGN

**Owner:** Orchestrator
**Gate:** Task prompt includes role context, specific deliverable, constraints, output path, and skill reference

```javascript
sessions_spawn({
  task: "[Full task prompt — see ORCHESTRATOR.md for template]",
  label: "[role]-[client]-[task]",
  model: "[selected model]",
});
```

### 4. EXECUTE

**Owner:** Specialist (Developer, Designer, Researcher)
**Gate:** Output matches the format specified in the respective role file

The specialist:

- Reads the full task prompt and referenced skill files
- Executes the work within scoped constraints
- Saves deliverable to the specified path
- Produces a structured output summary

**If blocked:** Specialist documents the blocker in their output and returns. Don't spin — flag it.

### 5. REVIEW

**Owner:** 2 independent QA agents (different models)
**Gate:** Both reviews submitted with severity-classified issues and scores

```javascript
// Always spawn 2 reviewers in parallel, always different models
sessions_spawn({
  task: "Review [deliverable path]. Original brief: [brief summary]. Use QA role standards.",
  label: "reviewer-1",
  model: "anthropic/claude-sonnet-4-5",
});

sessions_spawn({
  task: "Review [deliverable path]. Original brief: [brief summary]. Use QA role standards.",
  label: "reviewer-2",
  model: "openrouter/minimax/minimax-m2.5",
});
```

Reviewers follow the severity taxonomy and scoring rubric in [QA.md](file:///Users/randytorres/Projects/agency-ops-center/team/QA.md).

### 6. INTEGRATE

**Owner:** Orchestrator
**Gate:** All critical issues resolved, deliverable approved

The orchestrator:

1. Reads both reviews
2. Synthesizes feedback (see decision framework in ORCHESTRATOR.md)
3. Either approves, requests changes, or rejects
4. If approved: commits, pushes, updates client folder and DASHBOARD.md

### 7. DELIVER

**Owner:** Orchestrator
**Gate:** Deliverable is in the correct location, committed via PR, and dashboard is updated

- Client work → saved to `clients/[name]/deliverables/`
- Internal work → saved to `projects/internal/[project]/`
- GLASS code → **must go through PR on feature branch** (see `projects/glass/CONTRIBUTING.md`)
- CH web → **must go through PR on feature branch** (Randy merges via Netlify preview)
- Update `DASHBOARD.md` with completion status

---

## Git Integration (Mandatory for Code)

All code changes follow the PR workflow defined in project-level CONTRIBUTING.md files:

- **GLASS**: `projects/glass/CONTRIBUTING.md` — feature branches, worktree isolation, conventional commits, 2-reviewer gate
- **CH Web**: Feature branches only, never push to master, Netlify preview for review

### Agent Spawn Protocol for Code Tasks

Every agent working on code MUST:
1. Read the project's CONTRIBUTING.md before starting
2. Work on a feature branch (never main/master)
3. Use an isolated worktree (`/tmp/[project]-[label]/`)
4. Write PR notes (`PR-NOTES-[branch].md`)
5. Push branch only — **COO handles merge after review**

### Code Review Flow
```
Agent completes → Pushes branch → Writes PR notes
         ↓
COO spawns 2 reviewers (different models)
         ↓
Reviewers read diff + PR notes → Write reviews
         ↓
COO synthesizes → Approve / Request Changes / Reject
         ↓
COO merges to main (only after approval)
```

---

## Model Selection Strategy

Use model diversity to catch different failure modes. This is the **canonical reference** — don't duplicate this table elsewhere.

### Model Hierarchy (LOCKED — Randy approved)

| Tier | Model | Route | Best For | Cost |
|------|-------|-------|----------|------|
| **T1 — Architect** | GPT 5.3 Codex | `openai-codex/gpt-5.3-codex` | Architecture, complex code, DB design, code review | OAuth (free) |
| **T2 — Senior** | Claude Opus 4.6 | `anthropic/claude-opus-4-6` | Strategy, orchestration, nuanced judgment, long writes | $5/$25 |
| **T3 — Fast Senior** | MiniMax M2.5 | `openrouter/minimax/minimax-m2.5` | Clear-scoped tasks, fast execution, reviews, research | $1/$4 |
| **T4 — Specialist** | Kimi K2.5 | `openrouter/moonshotai/kimi-k2.5` | Frontend, long-context reads, large file writes | $0.60/$2.50 |
| **Imagen Only** | Gemini 2.0 Flash (Image Gen) | `google/gemini-2.0-flash-exp-image-generation` | Image generation ONLY via Imagen 3 | — |

### Role → Model Assignment

| Role | Primary | Fallback | Why |
|------|---------|----------|-----|
| **Orchestrator (COO)** | Opus 4.6 | Codex 5.3 | Best at planning, coordination, judgment |
| **Architect / Complex Code** | Codex 5.3 | Opus 4.6 | Strongest code quality and system design |
| **Developer (clear tasks)** | MiniMax M2.5 | Kimi K2.5 | Fast, smart, good for well-scoped work |
| **Developer (frontend)** | Kimi K2.5 | MiniMax M2.5 | Best at React/CSS, large file output |
| **Researcher** | MiniMax M2.5 | Kimi K2.5 | Fast synthesis, 1M context window |
| **Reviewer 1** | Codex 5.3 | Opus 4.6 | Strict, architectural perspective |
| **Reviewer 2** | MiniMax M2.5 | Kimi K2.5 | Different architecture, catches different issues |
| **Designer** | MiniMax M2.5 | Kimi K2.5 | Layout + component design |
| **Humanizer** | MiniMax M2.5 | Opus 4.6 | Fast, good at natural language |
| **Image Gen** | Gemini Imagen 3 | — | `gemini-2.0-flash-exp-image-generation` API only |
| **Tiebreaker** | whichever model wasn't used by R1/R2 | — | Must be different from both reviewers |

### Rules
- **Specialist and reviewer MUST be different models.** Architectural diversity catches different failures.
- **T1 (Codex) for anything that touches architecture, DB schema, or system design.** Don't waste it on copy or simple components.
- **T3 (MiniMax) for anything with clear requirements.** It's fast and cheap — use it as the workhorse.
- **T4 (Kimi) for frontend and large file writes.** 256K context, 65K output via OpenRouter.
- **Don't use Opus for tasks MiniMax can handle.** Save the expensive model for judgment calls.

---

## Quality Gates Summary

| Stage     | Gate                            | What Blocks Progression                     |
| --------- | ------------------------------- | ------------------------------------------- |
| Request   | Requirements exist              | Ambiguous or missing requirements           |
| Decompose | All tasks have success criteria | Vague task definitions                      |
| Assign    | Task prompt is complete         | Missing context, path, or constraints       |
| Execute   | Output matches role format      | Incomplete or misformatted deliverables     |
| Review    | 2 independent reviews submitted | Missing reviews or single-reviewer approval |
| Integrate | Zero critical issues            | Any 🔴 Critical issue unresolved            |
| Deliver   | Committed and tracked           | Deliverable not in correct location         |

---

## Failure Modes & Recovery

### Specialist is stuck (2x estimated time, no output)

1. Check session logs
2. If blocked on requirements → send clarification via `sessions_send`
3. If technical blocker → kill session, simplify task, respawn
4. If repeated failures → escalate to Randy (task may need human intervention)

### Reviewers disagree

1. Is it subjective (style preference)? → Orchestrator decides, document rationale
2. Is it objective (one is wrong)? → Side with evidence
3. Genuinely ambiguous? → Spawn tiebreaker reviewer (different model from both)
4. Still unclear? → Escalate to Randy with both positions

### Requirements were wrong

1. Stop all active specialists on the affected task
2. Document what was wrong and what was learned
3. Go back to DECOMPOSE with corrected requirements
4. Don't patch — restart cleanly

### Quality keeps failing (3+ revision cycles)

Red flag. This means one of:

- Task is too big → decompose further
- Requirements are unclear → go back to user
- Skill file is outdated → update the skill
- Wrong specialist type → reassign

---

## Cycle Time Targets

| Task Type                             | Target                 | Escalation Trigger |
| ------------------------------------- | ---------------------- | ------------------ |
| **S task** (simple fix, copy change)  | 15-20 min total        | > 40 min           |
| **M task** (new component, report)    | 30-60 min total        | > 2 hours          |
| **L task** (system feature, strategy) | 2-4 hours total        | > 8 hours          |
| **Review cycle**                      | 10-15 min per reviewer | > 30 min           |

These are wall-clock times from assignment to approved deliverable (including review). If a cycle exceeds the escalation trigger, the orchestrator must diagnose why.

---

## Communication Protocols

### Orchestrator → Specialist

Use the task prompt template in ORCHESTRATOR.md. Be specific, not conversational.

### Orchestrator → Reviewer

Provide: path to deliverable, brief summary of original task, and any specific concerns to focus on.

### Specialist → Orchestrator (via output)

Use the output format defined in the role file. Include: what was built, files changed, how to verify, assumptions, and open questions.

### Reviewer → Orchestrator (via output)

Use the review format in QA.md. Include: scores, verdict, severity-classified issues, and strengths.

### Anyone → Randy (escalation)

Use the escalation format in ORCHESTRATOR.md. Include: decision needed, context, options, and recommendation.

---

**This pipeline runs every task. The discipline IS the quality. Skip a step, and you're gambling with Randy's reputation and client trust.**
