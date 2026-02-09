---
name: roles
description: Subagent role definitions for the multi-agent orchestrator system
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
