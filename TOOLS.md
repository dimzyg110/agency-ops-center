# TOOLS.md — Tool Conventions & Local Notes

---

## 🛠️ Tool Usage Rules

### Before EVERY `write` or `edit`:

1. Run `git status` to check for uncommitted changes
2. If file is modified → STOP and ask Randy
3. Show the diff before writing
4. Wait for confirmation
5. After writing → commit immediately

### GPT 5.3 Codex — CLI Only

- **GPT 5.3 Codex is NOT available via API.** Only through the Codex CLI (`codex exec`).
- Always run Codex CLI in the **background** so it doesn't block responses:
  ```bash
  codex exec --full-auto -m gpt-5.3-codex -C /path "task" 2>&1 &
  ```
- Use `background: true` on exec calls, then monitor with `process poll/log`.
- Codex CLI **cannot access GitHub** from sandbox (no network). After it writes files, the COO handles `git push` and `gh pr create`.
- Codex CLI may **time out on very large file generation** (ChatGPT Plus tier limits). Break large tasks into focused chunks if needed.
- For API-based subagents, use `openai/gpt-5.2-codex` instead (different model, works via API).

### Subagent Rate Limits

- **Max 2 subagents from the same provider at a time** (e.g., max 2 Antigravity agents concurrently)
- Stagger across providers when possible (Antigravity, NVIDIA, OpenAI Codex)
- Queue remaining tasks to run after the first batch completes

### GLASS — Approved Models (LOCKED)

Only 3 models touch GLASS. No exceptions unless Randy explicitly says otherwise:

| Role | Model | Access |
|------|-------|--------|
| Chief Architect / Backend | **GPT 5.3 Codex** | CLI only (`codex exec`) |
| Code Reviews / QA | **GPT 5.3 Codex** | CLI only (`codex exec`) |
| Frontend | **Kimi K2.5** | API subagent (`openrouter/moonshotai/kimi-k2.5`) |

- No Gemini, no GPT-5.2, no other models on GLASS work.
- Codex 5.3 = final authority on architecture, backend, AND code reviews.
- Kimi K2.5 = frontend only (`apps/web/`).

**Role prompts are MANDATORY.** Every GLASS agent spawn must include:
- Developer agents: `"Read /data/workspace/team/DEVELOPER.md for your role definition. Then: [task]"`
- Reviewer agents: `"Read /data/workspace/team/QA.md for your role definition. Then: [task]"`
- Codex CLI tasks: include the role context in the task prompt since it can read files directly.

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
