# TOOLS.md — Tool Conventions & Local Notes

---

## 🛠️ Tool Usage Rules

### Before EVERY `write` or `edit`:

1. Run `git status` to check for uncommitted changes
2. If file is modified → STOP and ask Randy
3. Show the diff before writing
4. Wait for confirmation
5. After writing → commit immediately

### GPT 5.3 Codex — OAuth Subagent

- **GPT 5.3 Codex is available via OAuth subscription** as `openai-codex/gpt-5.3-codex`.
- Auth profile: `openai-codex:default` with `mode: "oauth"` (configured in gateway).
- Use in subagent spawns: `model: "openai-codex/gpt-5.3-codex"`
- **NOT** `openai/o3` or `openai/gpt-5.3-codex` — those will fail with "model not allowed".
- Codex CLI (`codex exec`) is NOT installed in sandbox.
- For API-based subagents on different provider, use `openai/gpt-5.2-codex` (different model).

### Subagent Rate Limits

- **Max 2 subagents from the same provider at a time** (e.g., max 2 Antigravity agents concurrently)
- Stagger across providers when possible (Antigravity, NVIDIA, OpenAI Codex)
- Queue remaining tasks to run after the first batch completes

### Model Hierarchy (LOCKED — Randy approved)

| Tier | Model | Route | Use For |
|------|-------|-------|---------|
| **T1 Architect** | GPT 5.3 Codex | `openai-codex/gpt-5.3-codex` | Architecture, complex code, DB schema, code review |
| **T2 Senior** | Claude Opus 4.6 | `anthropic/claude-opus-4-6` | Strategy, orchestration, nuanced judgment |
| **T3 Fast Senior** | MiniMax M2.5 | `openrouter/minimax/minimax-m2.5` | Clear-scoped tasks, fast execution, reviews, research |
| **T4 Specialist** | Kimi K2.5 | `openrouter/moonshotai/kimi-k2.5` | Frontend, long-context, large file writes |
| **Imagen Only** | Gemini Imagen 3 | `google/gemini-2.0-flash-exp-image-generation` | Image generation ONLY — not for code/review/research |

**Rules:**
- T1 (Codex) = final authority on architecture and code reviews. Don't waste on simple tasks.
- T3 (MiniMax) = workhorse. Fast, smart, cheap. Use for anything with clear requirements.
- T4 (Kimi) = frontend and large writes. 256K context, 65K output.
- Specialist and reviewer MUST be different models.
- Don't use Opus for tasks MiniMax can handle.

**Canonical reference:** `team/WORKFLOW.md` has the full role→model mapping.

**Role prompts are MANDATORY.** Every agent spawn must include:
- Developer agents: `"Read /data/workspace/team/DEVELOPER.md for your role definition. Then: [task]"`
- Reviewer agents: `"Read /data/workspace/team/QA.md for your role definition. Then: [task]"`
- GLASS agents: `"Read /data/workspace/projects/glass/CONTRIBUTING.md first. Then: [task]"`

### GLASS Repo — Parallel Agent Isolation

Agents MUST NOT share the same working directory. Use **git worktrees** so each lane gets its own isolated checkout:

```
/data/workspace/projects/glass/src/   ← main (COO only)
/tmp/glass-backend/                   ← codex/backend-skeleton (Codex 5.3)
/tmp/glass-frontend/                  ← kimi/frontend-shell (Kimi K2.5)
/tmp/glass-platform/                  ← codex/platform-infra (Codex 5.3)
```

- **Never point two agents at the same directory.** Uncommitted files leak across branches.
- When spawning an agent, always specify `-C /tmp/glass-<lane>/` for Codex CLI or the full path in subagent task descriptions.
- COO handles all `git push` and `gh pr create` from main worktree after agent finishes.
- To add a new worktree: `git worktree add /tmp/glass-<lane> -b <branch> main`

### Safe Commands (No Approval Needed)

- `ls`, `cat`, `head`, `tail` (read files/directories)
- `git status`, `git log`, `git diff` (inspect git state)
- `pwd`, `whoami`, `date` (system info)
- Spawning subagents for defined tasks

### Ask First

- `rm`, `mv` (delete/move files)
- `npm install`, `pip install` (packages)
- Any command affecting `.env`, `secrets/`, or credentials
- Anything that leaves the machine (emails, posts)

---

## 🎯 Subagent Rules

### When to Spawn

- Tasks that take >5 minutes
- Specialized work (design, code, research)
- All deliverable creation

### Spawn Template

```javascript
sessions_spawn({
  task: "[Clear description]. Requirements: [specific]. Save to: [path]. Use skill: [skill-name].",
  label: "[role]-[task-name]",
  model: "[model-name]",
  cleanup: "delete",
});
```

### Always Specify

- **task**: What to do + where to save output
- **label**: Descriptive identifier
- **model**: Appropriate model for the role

---

## 📁 Client Folder Structure

Every client folder should follow:

```
clients/[client-name]/
├── BRIEF.md                # Project requirements & goals
├── roadmap.md              # Timeline & milestones
├── strategy/               # Strategy docs & plans
├── research/               # Market/competitor research
└── deliverables/           # Final outputs
```

---

## 🔐 Secrets & Credentials

### Never Touch

- `.env` files
- `secrets/` directory
- Anything with "API_KEY", "TOKEN", "SECRET"

### If Keys Need Updating

1. Tell Randy
2. Provide exact line to add/change
3. Wait for him to do it

---

## 📊 Tech Stack

| Tool                 | Status                     |
| -------------------- | -------------------------- |
| OpenAI API           | Active                     |
| Google Places API    | Active                     |
| Brave Search API     | Active                     |
| Resend (email)       | Configured, domain pending |
| Beehiiv (newsletter) | Partially set up           |
| GitHub Pages (sales) | Live                       |

---

## 📝 Local Notes

_Add environment-specific details here:_

```markdown
### Paths

- Workspace: /Users/randytorres/Projects/agency-ops-center
- Claude repo (archive): /Users/randytorres/Projects/claude

### SSH

- (add as needed)

### Voice/TTS

- (add as needed)
```
