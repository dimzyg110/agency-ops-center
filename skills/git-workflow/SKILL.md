---
name: git-workflow
description: "Git workflow for parallel agent development. Use when: multiple agents working on same repo, creating PRs, managing worktrees. Don't use when: single-file edits in workspace."
---

# Git Workflow for Parallel Agent Development

This skill defines the Git workflow for coordinating multiple subagents working on the same repository simultaneously. It enforces isolation via **git worktrees** to prevent conflicts and accidental overwrites.

## 1. Worktree Setup for Parallel Agents

Agents MUST NOT share the same working directory. Use **git worktrees** so each lane gets its own isolated checkout.

### Directory Structure
```
/data/workspace/projects/[project]/src/   ← main (COO only)
/tmp/[project]-[lane]/                    ← agent-lane (e.g., backend-skeleton)
```

### Creating a Worktree
When spawning a subagent for a parallel task:
1. Create a branch for the task:
   ```bash
   git branch [task-branch] main
   ```
2. Create the worktree in `/tmp/`:
   ```bash
   git worktree add /tmp/[project]-[lane] [task-branch]
   ```
3. Pass the worktree path to the subagent:
   ```javascript
   sessions_spawn({
     task: "Work in /tmp/[project]-[lane]. Implement [feature].",
     ...
   })
   ```

### Cleaning Up
After the agent finishes and changes are pushed/merged:
```bash
git worktree remove /tmp/[project]-[lane]
git branch -d [task-branch] # if merged
```

## 2. Branch Naming Conventions

- **Features**: `feat/[feature-name]`
- **Fixes**: `fix/[bug-description]`
- **Chores**: `chore/[maintenance-task]`
- **Refactors**: `refactor/[module-name]`
- **Docs**: `docs/[topic]`

Examples:
- `feat/user-auth`
- `fix/login-redirect-loop`
- `chore/update-deps`

## 3. Commit Message Format

Follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

[optional body]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding missing tests
- `chore`: Build process, auxiliary tools

**Example**:
```
feat(auth): implement Google OAuth login

Added Passport strategy for Google. Updated user schema to store provider ID.
```

## 4. PR Creation Workflow

1. **Agent Implementation**: Agent works in its worktree, commits changes locally.
2. **Review**: Agent self-reviews or spawns a peer reviewer.
3. **Push Handoff**: Agent notifies COO that work is ready.
4. **COO Action**:
   - COO navigates to the worktree or pulls the branch to main (if fast-forward).
   - **COO handles all `git push`**.
   - **COO handles `gh pr create`**.

**Agents DO NOT push directly.** This ensures the COO maintains the "gatekeeper" role and validates all outgoing code.

## 5. COO Role

The COO is the **Release Manager**.

- **Orchestrates**: Decides which branches are created and when.
- **Validates**: Checks `git status` and diffs before pushing.
- **Merges**: Handles PR merges after approval.
- **Syncs**: Keeps the main worktree up to date.

**Rule**: If an agent needs to push, it must ask the COO. The COO executes the push.
