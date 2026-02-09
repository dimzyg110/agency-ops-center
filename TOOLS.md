# TOOLS.md - Tool Conventions

**This file documents how tools are used in this workspace.**

---

## 🔒 **FILE MODIFICATION PROTOCOL**

### **Before EVERY `write` or `edit`:**
1. Run `git status` to check for uncommitted changes
2. If file is modified → STOP and ask user
3. Show the diff before writing
4. Wait for confirmation
5. After writing → commit immediately

### **Git Workflow:**
```bash
# Always check first
git status

# If clean, proceed with edits
# After editing, commit immediately
git add .
git commit -m "Clear description of changes"
git push
```

---

## 🛠️ **EXEC APPROVALS**

### **High-Risk Commands (ALWAYS ASK FIRST)**
- `rm` (delete files)
- `mv` (move/rename files)
- `git reset` (undo commits)
- `git merge` (merge branches) - **BLOCKED**
- `npm install` / `pip install` (install packages)
- Any command affecting `.env` or `secrets/`

### **Approval Format:**
```markdown
**Command:** `npm install express`
**Purpose:** Install Express.js for Acme Corp API backend
**Impact:** Adds dependency to package.json
**Safe to proceed?** (yes/no)
```

### **Safe Commands (No Approval Needed)**
- `ls`, `cat`, `head`, `tail` (read files/directories)
- `git status`, `git log`, `git diff` (inspect git state)
- `pwd`, `whoami`, `date` (system info)

---

## 🎯 **SUBAGENT RULES**

### **When to Spawn Subagents**
- Tasks that take >5 minutes
- Specialized work (design, code, research)
- Tasks requiring different expertise than orchestration

### **When NOT to Spawn**
- Simple questions (just answer)
- Tasks you can verify in <1 minute
- Status checks (`/subagents list`, `/status`)

### **Spawn Template:**
```javascript
sessions_spawn({
  task: "[Clear description]. Requirements: [specific]. Save to: [path]. Use skill: [skill-name].",
  label: "[role]-[task-name]",
  model: "[model-name]",
  cleanup: "delete"  // Unless told otherwise
})
```

### **Always Specify:**
- **task**: What to do + where to save output
- **label**: Descriptive identifier (easier to track)
- **model**: Appropriate model for the task

---

## 📁 **FILE STRUCTURE (DO NOT MODIFY)**

```
/data/workspace/
├── .env                    # API KEYS - READ ONLY
├── secrets/                # CREDENTIALS - READ ONLY
├── team/                   # Team roles - OK to read, ask before editing
├── skills/                 # Workflows - OK to add, ask before editing existing
├── clients/                # Client work - OK to modify (with git discipline)
│   └── [client-name]/
│       ├── BRIEF.md        # Requirements
│       ├── roadmap.md
│       ├── research/
│       └── deliverables/
├── projects/               # Internal work - OK to modify
├── templates/              # Starters - OK to add
├── research/               # General research - OK to write
└── memory/                 # Logs - OK to write
```

---

## 🗂️ **CLIENT FOLDER STRUCTURE**

Every client folder MUST follow this structure:

```
clients/[client-name]/
├── BRIEF.md                # Project requirements & goals
├── roadmap.md              # Timeline & milestones
├── research/               # Market/competitor research
│   ├── competitors.md
│   └── market-analysis.md
└── deliverables/           # Final outputs (designs, code, docs)
    ├── design.md
    ├── index.html
    └── README.md
```

---

## 🚨 **PROHIBITED ACTIONS**

- ❌ Creating new "systems" without approval
- ❌ Editing `.env` or credential files
- ❌ Merging git branches (use rebase or ask)
- ❌ Installing packages without approval
- ❌ Deleting files outside `/tmp/`
- ❌ Modifying team/ or skills/ without discussion

---

## 🔍 **DEBUGGING & TROUBLESHOOTING**

### **When a Subagent Fails:**
1. Check the transcript: `/subagents log [id]`
2. Identify the error
3. If it's fixable → re-spawn with clarified requirements
4. If it's a blocker → notify user immediately

### **When Git is Dirty:**
```bash
# Check status
git status

# If you see uncommitted changes:
# 1. STOP what you were doing
# 2. Ask user: "There are uncommitted changes. Should I commit them first?"
# 3. Wait for approval
# 4. Then proceed
```

---

## 📊 **MONITORING & TRACKING**

### **Active Subagents**
Check regularly:
```bash
/subagents list
```

### **Session Status**
```bash
/status
```

### **Git State**
Before any file operation:
```bash
git status
```

---

## 🎓 **SKILLS USAGE**

### **When a Workflow Exists**
Before executing:
1. Check `skills/` for relevant skill
2. Read the `SKILL.md` file
3. Follow the instructions

### **Creating New Skills**
If you find yourself repeating a workflow:
1. Create `skills/[skill-name]/SKILL.md`
2. Document the process
3. Commit and push
4. Next time, read the skill instead of improvising

---

## 🔐 **SECRETS & CREDENTIALS**

### **Never Touch These:**
- `.env`
- `secrets/`
- `~/.openclaw/credentials/`
- Any file containing "API_KEY", "TOKEN", "SECRET"

### **If Keys Need Updating:**
1. Tell the user
2. Provide the exact line to add/change
3. Wait for them to do it
4. **Do NOT edit the file yourself**

---

## 🚀 **DEPLOYMENT & PRODUCTION**

### **Before Deploying:**
1. All deliverables reviewed by 2+ agents
2. Git history clean (clear commit messages)
3. Client approval received
4. Deployment plan documented

### **Never:**
- Deploy without review
- Deploy with uncommitted changes
- Deploy without backup plan

---

**This is your cheat sheet. When in doubt, check here first.**
