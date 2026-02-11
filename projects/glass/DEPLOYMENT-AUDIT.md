# GLASS Deployment Audit - 2026-02-11

## Summary
**TWO SEPARATE RAILWAY PROJECTS EXIST**

### Project 1: GLASS (Working) ✅
- **Project ID:** 125c58a9-0472-4e7d-88a1-463258e2ed5f
- **Git Repo:** https://github.com/Roviq-AI/glass.git
- **Status:** DEPLOYED AND WORKING
- **Frontend:** https://glass-web-production.up.railway.app/ (200 OK)
- **Backend:** https://glass-api-production.up.railway.app/health (200 OK)

### Project 2: Unknown (Failing) ❌
- **Project ID:** 99a0c45f-952d-4b86-b3d0-d5e7e9df5c3a
- **Service ID:** 5de8dd7b-1563-46fa-8fab-a8fef8a30a06
- **Status:** HEALTHCHECK FAILING
- **Not linked to this workspace**

## Current State (GLASS Project)

### Git Status
- ✅ Latest commit: `9b3ccb6` - "feat: complete database setup and seeding"
- ✅ Pushed to GitHub (origin: https://github.com/Roviq-AI/glass.git)
- ✅ 8 commits ahead of initial deployment

### Frontend (glass-web)
- ✅ Deployed successfully
- ✅ Variables configured:
  - `VITE_API_URL`: https://glass-api-production.up.railway.app/
  - `VITE_CLERK_PUBLISHABLE_KEY`: pk_test_aHVtYW5lLWRpbm9zYXVyLTAuY2xlcmsuYWNj...
  - `VITE_USE_MOCK`: false
- ✅ Serving at https://glass-web-production.up.railway.app/

### Backend (glass-api)
- ✅ Deployed successfully (uptime: ~10 minutes)
- ✅ Variables configured:
  - `DATABASE_URL`: Postgres connected
  - `REDIS_URL`: Redis connected
  - `CLERK_SECRET_KEY`: Configured
  - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Configured
- ✅ Health endpoint working: /health → 200 OK
- ⚠️ All API endpoints returning 401 (expected - requires Clerk auth)

### Database
- ✅ 12 tables created in `glass` schema
- ✅ 10 dispensaries seeded to `glass.sources`
- ✅ Migrations applied

## The Issue

**Randy sent a link to project `99a0c45f...` which is NOT the GLASS project I've been deploying.**

Two possibilities:
1. There are TWO GLASS deployments and one is outdated
2. Randy is looking at a different project entirely
3. Railway auto-created a second project during some operation

## What Needs Clarification

**Randy: Which project do you actually want working?**

Option A: **GLASS project (125c58a9...)** - Already working
- Frontend: https://glass-web-production.up.railway.app/
- Backend: https://glass-api-production.up.railway.app/
- If this is the right one, we're DONE

Option B: **Other project (99a0c45f...)** - Unknown/Failing  
- Need to link to it first to investigate
- Don't know what repo/code it's using
- Don't have access from current workspace

## Next Actions

### If GLASS project is correct:
```bash
# Test the frontend
open https://glass-web-production.up.railway.app/

# It should load, show Clerk login, and connect to API
```

### If other project needs fixing:
```bash
# Link to the failing project
export RAILWAY_TOKEN="<token-for-that-project>"
railway link 99a0c45f-952d-4b86-b3d0-d5e7e9df5c3a

# Then investigate what's deployed there
railway status
railway logs
```

## Conclusion

**The GLASS project I've been working on is fully deployed and functional.** If there's a problem, it's likely:
1. You're looking at the wrong Railway project
2. Or there's a second GLASS deployment I don't know about

**Tell me which project URL you want working and I'll focus on that.**
