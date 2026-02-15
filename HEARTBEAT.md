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

## Current Status

### ✅ Completed
- PR #107: Railway scraper deploy + DB schema fix (merged)
- PR #108: UX loss aversion (merged)
- Scraper trigger mode: No auto-run on deploy (in PR #107)

### 🔄 In Progress
- PR #109: Production-ready location filter (review in progress)
  - Location filter now sets lat/lng for API filtering
  - 15 MA cities with coordinates
  - Savings counter uses real API data

### 📋 Pending
- Merge PR #109 after review
- Deploy Railway scrapers with new config
- Set up cron schedules for scrapers

### DB Schema (RESOLVED)
- Schema: `public` (NOT `glass`)
- All code updated to use `SET search_path TO public`
