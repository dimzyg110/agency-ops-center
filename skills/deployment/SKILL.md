---
name: deployment
description: "Deploy services to Railway, Vercel, or Netlify. Use when: deploying a new service, updating a deployed service, or debugging deployment issues. Don't use when: local development only. Outputs: deployed URL, health check confirmation, env var checklist."
---

# Deployment Skill

This skill governs the deployment of applications to production environments (Railway, Vercel, Netlify). It enforces verification steps to prevent "false positives" where infrastructure is up but the app is broken.

## 1. Railway Deployment Checklist

For backend services, APIs, and Dockerized apps.

### Preparation
- [ ] **Dockerfile**: Ensure it exposes the correct port (usually determined by `PORT` env var).
- [ ] **railway.toml**: Verify service configuration (build command, start command, watch patterns).
- [ ] **Env Vars**: 
    - Audit all required keys (API keys, DB URLs).
    - **NEVER** commit `.env` files.
    - Check if secrets are added to Railway project settings.
- [ ] **Health Check**: Ensure an endpoint (e.g., `/health` or `/`) returns 200 OK without auth.

### Execution
- Deploy via Railway CLI or Git push (if configured).
- Monitor build logs for errors.
- Verify service status is "Active".

## 2. Vercel Deployment Checklist

For frontend apps (Next.js, React, static sites).

### Preparation
- [ ] **vercel.json**: specific build settings or rewrites if needed.
- [ ] **Build Command**: Ensure `npm run build` (or equivalent) passes locally.
- [ ] **Env Vars**: Add all `NEXT_PUBLIC_` and server-side keys to Vercel project settings.

### Execution
- Deploy via Vercel CLI or Git push.
- Check build logs.
- Verify preview deployment before promoting to production.

## 3. Post-Deploy Verification (MANDATORY)

**"Deployed" means "User flows work", not just "Service is green".**

### Health Check
- `curl -I [url]` to verify 200 OK.

### E2E Verification (The "Real" Test)
Spawn a Playwright agent to test critical user flows immediately after deployment.
- **Signup/Login**: Create a test user.
- **Critical Path**: Perform the main action (e.g., view dashboard, search).
- **Screenshots**: Capture evidence of success.

**Spawn Template:**
```javascript
sessions_spawn({
  task: "Test [app-name] deployment at [url]. 1. Sign up a new user. 2. Verify dashboard loads. 3. Take screenshots of success/failure. Report critical bugs immediately.",
  label: "qa-deployment-verify",
  model: "google-antigravity/gemini-3-pro-high"
})
```

## 4. Environment Variable Audit Template

Use this to ensure no secrets are missing.

| Variable Name | Required? | Present in Prod? | Source |
| ------------- | --------- | ---------------- | ------ |
| DATABASE_URL  | Yes       | [ ]              | Railway/Supabase |
| API_KEY_X     | Yes       | [ ]              | Provider X |
| AUTH_SECRET   | Yes       | [ ]              | Generated |

## 5. Common Failure Patterns (from GLASS Learnings)

### ❌ Claiming "Deployed" Without Testing
**Symptom:** Agent says "Deployment complete" because build passed, but app crashes on load or auth loops.
**Fix:** Never mark task complete until E2E test passes.

### ❌ Auth Redirect Loops (Clerk + React Router)
**Symptom:** Infinite redirect between `/` and `/login`.
**Fix:** Use `routing="hash"` or `path` correctly configured. Ensure middleware matches router guards.

### ❌ Database Schema Conflicts
**Symptom:** Drizzle/Prisma complains about existing tables during migration.
**Fix:** If safe (dev/staging), drop tables and re-run migration. Don't over-engineer schema diffs if a clean slate works.

### ❌ Missing Secrets
**Symptom:** App crashes with "property of undefined" or 500 errors on API calls.
**Fix:** `env | grep [KEY]` locally to verify what you think you have. Check dashboard for prod.

### ❌ Network Isolation
**Symptom:** Sandbox code cannot reach external DB or API.
**Fix:** Use Railway-hosted runners or specific proxies if needed. Don't assume localhost access to remote resources works without config.
