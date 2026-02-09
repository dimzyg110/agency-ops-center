# TOOLS.md — Tool Conventions & Local Notes

---

## 🛠️ Tool Usage Rules

### Before EVERY `write` or `edit`:

1. Run `git status` to check for uncommitted changes
2. If file is modified → STOP and ask Randy
3. Show the diff before writing
4. Wait for confirmation
5. After writing → commit immediately

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
