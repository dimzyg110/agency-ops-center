# ROLES.md — Subagent Role Selection Guide

> When spawning a subagent, use this guide to select the right role.
> Each role has a specific skillset — match the task to the role.

---

## Role Quick Reference

| Task Type | Role | File | When to Use |
|-----------|------|------|-------------|
| **Code / Dev** | Developer | `team/DEVELOPER.md` | Building features, fixes, API endpoints, DB changes |
| **Design / UI** | Designer | `team/DESIGNER.md` | Visual design, layouts, components, brand alignment |
| **Research** | Researcher | `team/RESEARCHER.md` | Market analysis, competitor intel, data investigation |
| **Review / QA** | QA | `team/QA.md` | Evaluating deliverables, code reviews, compliance checks |
| **Planning** | Orchestrator | `team/ORCHESTRATOR.md` | Strategy docs, roadmaps, prioritization |
| **Full execution** | See notes | — | If task spans multiple roles, spawn lead and coordinate |

---

## Detailed Role Guidelines

### 🧑‍💻 Developer — `team/DEVELOPER.md`

**Use for:**
- Writing code (any language)
- Database schema changes
- API endpoint creation
- Bug fixes
- Script creation
- Infrastructure changes
- Git/PR work

**Not for:**
- Design decisions (use Designer)
- Content writing (use appropriate content skill)
- Research (use Researcher)

---

### 🎨 Designer — `team/DESIGNER.md`

**Use for:**
- UI/UX layouts
- Visual components
- Brand alignment checks
- Design system work
- Graphics creation
- Content visual review

**Not for:**
- Code implementation (use Developer)
- Strategy (use Orchestrator)

---

### 🔍 Researcher — `team/RESEARCHER.md`

**Use for:**
- Market analysis
- Competitor research
- Data investigation
- Industry trends
- Customer discovery
- Feasibility studies

**Not for:**
- Code (use Developer)
- Design (use Designer)

---

### ✅ QA / Reviewer — `team/QA.md`

**Use for:**
- Code reviews
- Design reviews
- Content reviews
- Compliance checks
- Quality assessment

**Model requirement:** Must use DIFFERENT model than the creator.

---

### 🧠 Orchestrator — `team/ORCHESTRATOR.md`

**Use for:**
- Strategy documents
- Roadmaps
- Sprint planning
- Prioritization
- Process design

---

## Spawn Template

When spawning a subagent, always include the role reference:

```javascript
sessions_spawn({
  task: "[Clear description]. Read /data/workspace/team/[ROLE].md for your role definition. Then: [task]",
  label: "[role]-[task-name]",
  model: "[appropriate-model]",
});
```

### Model Selection

| Role | Recommended Models (in order) |
|------|-------------------------------|
| Developer | T1: Codex → T3: MiniMax → T4: Kimi |
| Designer | T4: Kimi → T3: MiniMax |
| Researcher | T3: MiniMax → T2: Opus |
| QA / Reviewer | T3: MiniMax (different from creator) |
| Orchestrator | T2: Opus → T3: MiniMax |

---

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Spawning Developer for research | Spawn Researcher |
| Spawning Designer for code | Spawn Developer |
| Using same model for create + review | Use DIFFERENT model for QA |
| Generic task without role reference | Include "Read team/XXX.md" in task |
| Spawning without a clear deliverable | Specify output file/location in task |

---

## File Locations

All role files are in `/data/workspace/team/`:
- `/data/workspace/team/DEVELOPER.md`
- `/data/workspace/team/DESIGNER.md`
- `/data/workspace/team/RESEARCHER.md`
- `/data/workspace/team/QA.md`
- `/data/workspace/team/ORCHESTRATOR.md`
- `/data/workspace/team/WORKFLOW.md`
