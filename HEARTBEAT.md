# Heartbeat

- Check subagent status (stuck or completed?)
- Check pending reviews to synthesize
- ⛔ **REVIEW GATE CHECK:** Did any deliverables reach Randy without 2+ reviews? If yes → flag immediately, run reviews retroactively, and apologize.
- ⛔ **HUMANIZER GATE CHECK:** Did any client-facing deliverables reach Randy without a humanizer pass? If yes → flag immediately, run humanizer retroactively.
- 🎯 **STRATEGIC SCAN:** Did any research reveal a tool, platform, or technique that applies to multiple clients? If yes → propose the cross-client play and spawn research if needed. Don't wait to be asked.
- Check client messages / approaching deadlines
- Check DASHBOARD.md for unresolved blockers
- Check revenue pipeline progress (newsletter, snapshots, sprints)
- Commit any uncommitted changes
- Update daily memory log if needed

## Current Issues

### Railway Scraper Deployment (IN PROGRESS)
- PR #50 created: `fix/railway-scraper-deploy`
- Config paths fixed: `/src/scrapers/...` (was missing /src)
- DB schema fixed: `search_path TO public` (was incorrectly using glass)
- **Awaiting:** Randy to merge PR and redeploy in Railway dashboard

### Frontend UX (IN PROGRESS)
- Opus implementing loss aversion changes
- Branch: `feat/ux-loss-aversion` (spawned just now)

### Reviews
- SCRAPER-FIXES-CODEX-REVIEW.md - pending
- SCRAPER-FIXES-MINIMAX-REVIEW.md - pending
