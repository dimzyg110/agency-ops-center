# TEAM WORKFLOW

**Standard operating procedures for multi-agent collaboration.**

---

## 🔄 **REVIEW WORKFLOW (MANDATORY)**

Every deliverable MUST pass through this workflow:

### **Step 1: Specialist Completes Work**
- Output saved to designated path
- Specialist announces completion
- Orchestrator receives notification

### **Step 2: Spawn 2 Reviewers (Parallel)**
```javascript
// Reviewer 1
sessions_spawn({
  task: "Review [output] in [path]. Use reviewer-role skill. Check for: [criteria].",
  label: "reviewer-1",
  model: "anthropic/claude-sonnet-4-5"
})

// Reviewer 2 (different model for diversity)
sessions_spawn({
  task: "Review [output] in [path]. Use reviewer-role skill. Check for: [criteria].",
  label: "reviewer-2",
  model: "google/gemini-3-pro"
})
```

### **Step 3: Wait for Both Reviews**
- Do NOT proceed until both reviewers complete
- Collect both feedbacks

### **Step 4: Synthesize Feedback**
Orchestrator analyzes:
- **Common issues** (both reviewers flagged) → **Critical**, must fix
- **Single-reviewer issues** → **Minor**, optional or nice-to-have
- **Contradictions** → Spawn 3rd reviewer as tiebreaker

### **Step 5: Decision**
Three possible outcomes:

**A) Approve as-is**
- No critical issues
- Minor issues are acceptable
- → Move to next task

**B) Request changes**
- Critical issues found
- Specialist updates their work
- → Repeat review cycle

**C) Reject & restart**
- Fundamental misunderstanding
- → Spawn new specialist with clarified requirements

### **Step 6: Final Integration**
- All tasks approved
- Orchestrator compiles deliverables
- Updates client folder
- Commits and pushes

---

## 🎯 **QUALITY GATES**

No deliverable proceeds without:
- ✅ 2+ independent reviews
- ✅ All critical issues resolved
- ✅ Clear commit message
- ✅ Documentation updated

---

## 📊 **MODEL SELECTION STRATEGY**

Use different models for different roles to get diverse perspectives:

| Role | Primary Model | Why |
|------|--------------|-----|
| Orchestrator | Claude Sonnet 4.5 | Best at planning & coordination |
| Developer | Claude Sonnet 4.5 | Best code quality |
| Designer | Gemini 3 Pro | Strong visual/creative reasoning |
| Researcher | GPT-5.2 Codex | Good at synthesis |
| Reviewer 1 | Claude Sonnet 4.5 | Strict code review |
| Reviewer 2 | Gemini 3 Pro | Different perspective |

---

## 🚀 **ITERATION SPEED**

Target cycle times:
- Design → Review → Approve: **15-20 minutes**
- Code → Review → Approve: **20-30 minutes**
- Research → Review → Approve: **10-15 minutes**

If a cycle takes >2x target time:
- Check subagent logs for issues
- Clarify requirements
- Simplify the task

---

## 🔧 **TROUBLESHOOTING**

### **Reviewer Disagreement**
If reviewers contradict:
1. Spawn 3rd reviewer
2. Use majority decision
3. If still unclear, orchestrator makes final call

### **Specialist Stuck**
If specialist hasn't completed in 2x expected time:
1. Check logs: `/subagents log [id]`
2. If blocked on requirement → send clarification
3. If technical blocker → kill & restart with simplified task

### **Quality Decline**
If multiple reviews request changes:
1. Review the task assignment (was it clear?)
2. Check the skill (is it up to date?)
3. Update workflow if pattern emerges

---

**This workflow is non-negotiable. Every task. Every time.**
