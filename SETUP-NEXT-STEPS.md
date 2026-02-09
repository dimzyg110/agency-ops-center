# SETUP COMPLETE - NEXT STEPS

**Agency Ops Center** has been created at: `/tmp/agency-ops-center`

---

## ✅ **What Was Created**

### **Core Workspace Files**
- `README.md` - Full setup guide and repo overview
- `AGENTS.md` - Operating rules for orchestrator (8,941 bytes)
- `SOUL.md` - Orchestrator persona and boundaries (5,049 bytes)
- `TOOLS.md` - Tool conventions and workflows (5,366 bytes)
- `IDENTITY.md` - Agent identity (orchestrator)
- `USER.md` - User profile template
- `HEARTBEAT.md` - Heartbeat configuration (empty by default)
- `.gitignore` - Secrets, credentials, temp files excluded

### **Team Roles** (`team/`)
- `ORCHESTRATOR.md` - Main agent coordination role
- `DEVELOPER.md` - Code specialist role
- `DESIGNER.md` - UI/UX specialist role
- `RESEARCHER.md` - Research specialist role
- `QA.md` - Reviewer specialist role
- `WORKFLOW.md` - Review workflow (2+ reviewers required)

### **Skills** (`skills/`)
- `roles/developer/SKILL.md` - Full developer workflow (5,919 bytes)
- `roles/reviewer/SKILL.md` - Reviewer checklist
- `client-onboarding/SKILL.md` - Client onboarding workflow

### **Folder Structure**
- `clients/` - Client projects (empty, ready for you to add)
- `projects/` - Internal & experimental projects (empty)
- `templates/` - Reusable starters (empty)
- `research/` - General research (empty)
- `memory/` - Daily logs (empty)

### **Git Repository**
- Initialized with `main` branch
- First commit created: "Initial agency ops center setup"
- Git identity configured as "Agency Bot" (bot@agency.local - placeholder)

---

## 🚀 **NEXT STEPS (Manual)**

### **1. Push to GitHub**

**Option A: Create Repo via GitHub Web UI**

1. Go to https://github.com/new
2. Create a **private** repository named `agency-ops-center`
3. **DO NOT** initialize with README (repo already has files)
4. Copy the SSH URL

Then run:
```bash
cd /tmp/agency-ops-center
git remote add origin git@github.com:YOUR_USERNAME/agency-ops-center.git
git push -u origin main
```

---

**Option B: Use GitHub CLI (if authenticated)**

```bash
cd /tmp/agency-ops-center
gh auth login
gh repo create agency-ops-center --private --source . --remote origin --push
```

---

### **2. Clone to Your Workspace**

Once pushed to GitHub:

```bash
# On your OpenClaw machine
# BACKUP your existing workspace first (if needed)
mv /data/workspace /data/workspace-backup-$(date +%Y%m%d)

# Clone the new repo
git clone git@github.com:YOUR_USERNAME/agency-ops-center.git /data/workspace
cd /data/workspace
```

---

### **3. Configure Git Identity (IMPORTANT)**

**Setup separate GitHub account for the bot:**

1. Create new GitHub account (e.g., `your-agency-bot`)
2. Generate SSH key:
```bash
ssh-keygen -t ed25519 -C "bot@youragency.com" -f ~/.ssh/openclaw-bot
```

3. Add public key to GitHub (Settings → SSH Keys):
```bash
cat ~/.ssh/openclaw-bot.pub
```

4. Configure git in workspace:
```bash
cd /data/workspace
git config user.name "Your Agency Bot"
git config user.email "bot@youragency.com"
git config core.sshCommand "ssh -i ~/.ssh/openclaw-bot -F /dev/null"
```

5. Test:
```bash
git config user.email  # Should show bot email
```

---

### **4. Copy Your Existing Work**

From your backed-up workspace:

```bash
# Copy clients
cp -r /data/workspace-backup-*/clients/* /data/workspace/clients/

# Copy projects
cp -r /data/workspace-backup-*/projects/* /data/workspace/projects/

# Copy any other folders you need
# (decoded-research, cue, etc.)
```

Then organize them:
- Client work → `/data/workspace/clients/[client-name]/`
- Internal projects → `/data/workspace/projects/internal/[project]/`
- Experiments → `/data/workspace/projects/experimental/[project]/`

---

### **5. Update USER.md**

Edit `/data/workspace/USER.md` with your actual details:
```bash
cd /data/workspace
nano USER.md
```

Fill in:
- Your name
- Timezone
- Communication preferences

---

### **6. Configure OpenClaw**

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
        "allowFrom": {
          "discord": ["YOUR_DISCORD_ID"]
        },
        "commands": [
          { "pattern": "^(rm|mv|git reset|git merge|npm install)", "require": "always" }
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

---

### **7. Restart OpenClaw**

```bash
openclaw gateway restart
```

---

### **8. Test the Setup**

Ask the orchestrator:

```
Test: Spawn a developer subagent to create a simple hello world function
```

Expected:
- Orchestrator spawns developer
- Developer creates code
- Orchestrator spawns 2 reviewers
- Reviewers critique the code
- Orchestrator synthesizes feedback

If this works → setup is complete! 🎉

---

## 📂 **Current Location**

The repo is ready at: `/tmp/agency-ops-center`

**File count:** 20 files
**Total lines:** 1,749 lines of documentation and configuration

---

## 📖 **Key Documents to Read**

After cloning to your workspace:

1. `/data/workspace/README.md` - Repo overview
2. `/data/workspace/AGENTS.md` - Orchestrator operating rules
3. `/data/workspace/team/WORKFLOW.md` - Review workflow
4. `/data/workspace/AGENCY-OPS-CENTER-GUIDE.md` - Full architecture guide (if you copied it from backup)

---

## 🔒 **Security Reminders**

1. **Never commit secrets** - `.gitignore` is configured, but be careful
2. **Use bot GitHub account** - Not your personal account
3. **Client data isolation** - Each client gets their own folder
4. **Credentials outside workspace** - Store in `~/.openclaw/credentials/`

---

**Ready to push to GitHub and start using the ops center!**
