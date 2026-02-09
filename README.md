# Agency Ops Center

**OpenClaw Multi-Agent Operations Center for Digital Agency**

## What This Is

This repository serves as the **central operations workspace** for OpenClaw, coordinating:
- Client project management
- Internal R&D projects
- Research and analysis
- Multi-agent collaboration workflows
- Quality assurance through peer review

## Structure

```
agency-ops-center/
├── team/                 # Team role definitions
│   ├── ORCHESTRATOR.md   # Main agent (coordinator)
│   ├── DEVELOPER.md      # Developer specialist role
│   ├── DESIGNER.md       # Designer specialist role
│   ├── RESEARCHER.md     # Research specialist role
│   ├── QA.md            # QA/Reviewer role
│   └── WORKFLOW.md       # Review & collaboration workflow
│
├── skills/               # Reusable workflows & processes
│   ├── roles/           # Agent role skills
│   ├── client-onboarding/  # Client onboarding workflow
│   ├── project-setup/      # New project initialization
│   └── code-review/        # Code review checklist
│
├── clients/              # Client projects (add yours here)
│   └── [client-name]/
│       ├── BRIEF.md      # Project requirements
│       ├── roadmap.md    # Timeline & milestones
│       ├── research/     # Market/competitor research
│       └── deliverables/ # Final outputs
│
├── projects/             # Internal projects & R&D
│   ├── internal/        # Internal tools & platforms
│   └── experimental/    # Research & experiments
│
├── templates/            # Reusable project starters
│   └── [template-name]/ # SaaS starter, landing page, etc.
│
├── research/             # General research (not client-specific)
│
└── memory/               # Daily logs & long-term memory
    ├── YYYY-MM-DD.md    # Daily notes
    └── MEMORY.md        # Curated long-term memory
```

## Setup

### 1. Clone This Repo

```bash
git clone [YOUR_REPO_URL] /data/workspace
cd /data/workspace
```

### 2. Configure Git Identity

**Important:** This workspace should use a separate GitHub account (not your personal account).

```bash
# Generate SSH key for agency bot (if you haven't already)
ssh-keygen -t ed25519 -C "bot@youragency.com" -f ~/.ssh/openclaw-bot

# Add to GitHub (copy public key)
cat ~/.ssh/openclaw-bot.pub

# Configure git for this workspace
git config user.name "Agency Bot"
git config user.email "bot@youragency.com"
git config core.sshCommand "ssh -i ~/.ssh/openclaw-bot -F /dev/null"
```

### 3. Configure OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "workspace": "/data/workspace",
      "model": {
        "primary": "anthropic/claude-sonnet-4-5"
      },
      "subagents": {
        "model": "anthropic/claude-sonnet-4-5",
        "maxConcurrent": 8,
        "allowAgents": ["*"]
      }
    }
  },
  "tools": {
    "exec": {
      "approvals": {
        "enabled": true,
        "commands": [
          { "pattern": "^(rm|mv|git reset|git merge)", "require": "always" }
        ]
      }
    },
    "subagents": {
      "tools": {
        "deny": ["sessions_spawn", "gateway", "cron"]
      }
    }
  }
}
```

### 4. Restart OpenClaw

```bash
openclaw gateway restart
```

## Usage

### Orchestrator Mode (Main Agent)

You are the **orchestrator**. Your job is to:
1. Understand requirements
2. Break down tasks
3. Assign to specialists (via `sessions_spawn`)
4. Coordinate reviews (2-3 reviewers per task)
5. Synthesize feedback
6. Approve final deliverables

### Spawning Specialists

```javascript
// Spawn developer
sessions_spawn({
  task: "Build login page for Acme Corp based on design in /clients/acme/deliverables/login-design.md",
  label: "developer-login",
  model: "anthropic/claude-sonnet-4-5"
})

// Spawn designer
sessions_spawn({
  task: "Design landing page hero section for Acme Corp",
  label: "designer-hero",
  model: "google/gemini-3-pro"
})

// Spawn 2 reviewers (parallel)
sessions_spawn({
  task: "Review code in /clients/acme/deliverables/login.html using code-review skill",
  label: "reviewer-1",
  model: "anthropic/claude-sonnet-4-5"
})
sessions_spawn({
  task: "Review code in /clients/acme/deliverables/login.html using code-review skill",
  label: "reviewer-2",
  model: "google/gemini-3-pro"
})
```

### Review Workflow

**Every deliverable must be reviewed by 2+ independent agents.**

1. Specialist completes work
2. Spawn 2 reviewers (use different models for diversity)
3. Synthesize feedback
4. Approve or request changes
5. Repeat if needed

## Key Principles

### No Solo Work
- NEVER execute tasks yourself as orchestrator
- ALWAYS spawn specialists
- ALWAYS spawn reviewers
- Everything gets checked by 2-3 independent agents

### Skills Over Repetition
- Common workflows → Skills (`skills/*/SKILL.md`)
- Don't repeat instructions - load the skill

### Git Discipline
- Commit after each major change
- Clear commit messages
- Push regularly

### Client Isolation
- Each client gets their own folder
- Keep briefs, research, deliverables separate
- Never mix client data

## Adding New Content

### Add a Client

1. Create `/clients/[client-name]/`
2. Add `BRIEF.md` with requirements
3. Use `skills/client-onboarding/SKILL.md` workflow
4. Commit and push

### Add a Skill

1. Create `/skills/[skill-name]/SKILL.md`
2. Include YAML frontmatter with name/description
3. Write clear instructions
4. Test with a subagent spawn
5. Commit and push

### Add a Project

1. Create `/projects/internal/[project-name]/` or `/projects/experimental/[project-name]/`
2. Add README.md with project details
3. Commit and push

## Documentation

- **Full Setup Guide:** `/AGENCY-OPS-CENTER-GUIDE.md` (reference architecture)
- **Team Roles:** `/team/*.md`
- **Skills:** `/skills/*/SKILL.md`
- **Workflow:** `/team/WORKFLOW.md`

## Security

- **Never commit secrets** (API keys, credentials)
- **Use `.gitignore`** for sensitive files
- **Separate bot GitHub account** (not your personal account)
- **Read-only credentials** stored in `~/.openclaw/credentials/` (outside workspace)

---

**This is a living workspace. Update it as your team grows.**
