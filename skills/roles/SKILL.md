---
name: roles
description: |-
  Use when: spawning a specialist subagent and need the role definition. Don't use when: you already know the role instructions or the task is self-contained.
---

# Agent Roles

This directory contains role definitions used when spawning specialist subagents. Each role file defines the persona, capabilities, and constraints for that specialist type.

## Available Roles

| Role         | File                   | When to Use                           |
| ------------ | ---------------------- | ------------------------------------- |
| Orchestrator | `team/ORCHESTRATOR.md` | COO coordination (you)                |
| Developer    | `team/DEVELOPER.md`    | Code, APIs, infrastructure            |
| Designer     | `team/DESIGNER.md`     | UI/UX, brand, visual assets           |
| Researcher   | `team/RESEARCHER.md`   | Market research, competitive analysis |
| QA           | `team/QA.md`           | Code review, quality assurance        |

## Usage

When spawning a subagent, reference the relevant role file:

```
sessions_spawn(
  task="Read team/DEVELOPER.md for your role. Then: [task description]",
  label="developer-[task]",
  model="anthropic/claude-sonnet-4-5"
)
```

## Notes

- Role definitions live in `team/` (not this directory) since they're core to the workspace
- This skill exists for discoverability in the ClawHub skill registry
- See `team/WORKFLOW.md` for the mandatory review process

---

## 📋 Standard Task Execution

### Step 1: Understand Requirements

- Read client brief or user request
- Clarify ambiguities
- Define success criteria

### Step 2: Break Down Task

- Identify subtasks
- Determine required specialists (developer, designer, researcher)
- Create execution plan

### Step 3: Assign to Specialists

```javascript
sessions_spawn(
  task="[Clear description, requirements, output path, skill to use]. VOICE RULES: Write like a human. No em dashes (use commas or periods). No rule of three. No 'serves as' / 'testament to' / 'landscape' / 'tapestry' / 'delve' / 'crucial' / 'pivotal' / 'fostering' / 'showcasing' / 'underscoring'. No 'It's not just X, it's Y' constructions. No promotional language ('vibrant', 'stunning', 'groundbreaking', 'nestled'). Use 'is/are/has' instead of 'serves as/stands as/boasts'. Vary sentence length. Have opinions. Be specific over vague. Read the humanizer skill at skills/humanizer/SKILL.md for the full pattern list.",
  label="[role]-[task-name]",
  model="[appropriate-model]"
)
```

### Step 4: ⛔ DELIVERY GATE — Specialist completes → Reviewers spawn IMMEDIATELY

DO NOT summarize for Randy. DO NOT send highlights. DO NOT pass Go.

```javascript
sessions_spawn(task="Review [file path]...", label="reviewer-1-[task]", model="openai-codex/gpt-5.3-codex")
sessions_spawn(task="Review [file path]...", label="reviewer-2-[task]", model="google-antigravity/gemini-3-pro-high")
```

Both reviewers must:
- Read the actual output file (not a summary)
- Critique independently (no access to each other's review)
- Use different models (architectural diversity catches different issues)
- Check for: missing requirements, factual errors, generic advice, scope creep, pricing reality
- **Check for AI voice patterns**: em dashes, rule of three, promotional language, vague attributions, "serves as" / "testament to" / "landscape", negative parallelisms ("not just X, it's Y"), sycophantic tone. Flag any section that reads like AI wrote it.

### Step 5: Synthesize Reviews

- Common issues (both flagged) → MUST FIX before delivery
- Single-reviewer issues → Fix if valid, note if subjective
- Contradictions → Spawn 3rd reviewer as tiebreaker
- Missing requirements → Send back to specialist with specific instructions

### Step 5.5: ⛔ HUMANIZER GATE — Mandatory before delivery

After reviews are synthesized and fixes applied, spawn one final agent:

```javascript
sessions_spawn(
  task="Read the humanizer skill at skills/humanizer/SKILL.md. Then read [deliverable path]. Apply ALL 24 humanizer patterns to remove AI voice. Rewrite sections that sound generated. Keep meaning intact. Add personality where it's flat. Save the humanized version to the SAME file (overwrite). List changes made at the bottom of your response.",
  label="humanizer-[task-name]",
  model="google-antigravity/claude-opus-4-6-thinking"
)
```

This is NOT optional. Every client-facing deliverable gets humanized before delivery.
Skip this step = same as skipping reviews. Unacceptable.

### Step 6: Final Delivery to Randy

ONLY after reviews are synthesized and issues resolved:
- Compile approved deliverables
- Present to Randy with review context ("reviewers flagged X, fixed Y, kept Z")
- Update client folder
- Commit and push
- Update DASHBOARD.md

---

## 📊 Model Selection Strategy

**Canonical reference is `team/WORKFLOW.md`.** This is a quick-reference copy.

| Tier | Model | Route | Best For |
|------|-------|-------|----------|
| **T1 Architect** | Codex 5.3 | `openai-codex/gpt-5.3-codex` | Architecture, complex code, DB, code review |
| **T2 Senior** | Opus 4.6 | `anthropic/claude-opus-4-6` | Strategy, orchestration, judgment |
| **T3 Fast Senior** | MiniMax M2.5 | `openrouter/minimax/minimax-m2.5` | Clear tasks, fast execution, reviews |
| **T4 Specialist** | Kimi K2.5 | `openrouter/moonshotai/kimi-k2.5` | Frontend, long-context, large writes |
| **Utility** | Gemini 2.5 Flash | `google/gemini-2.5-flash` | Cheap tasks, image gen, quick checks |
