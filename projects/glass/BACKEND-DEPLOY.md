# GLASS Backend API Deployment to Railway

Date: 2026-02-11 (UTC)
Service: `glass-api` (Railway project: `glass`, env: `production`)

## Commands Run

1. Checked current link/status
   - `railway status`
   - Result: project `glass`, env `production`, service `glass-api`

2. Linked service explicitly
   - `railway link`
   - Selected: workspace `Randy Torres's Projects` → project `glass` → service `glass-api`

3. Checked environment variables
   - `railway variables`
   - Confirmed vars existed (including `CORS_ORIGIN`, `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `PORT`)

4. Set required variables
   - `railway variables --set JWT_SECRET=$(openssl rand -hex 32)`
   - `railway variables --set PORT=3000`

5. Deployed
   - `railway up --detach`
   - Deployment ID: `e9a8c710-ddbd-49c8-a26b-7c984109c922`

6. Checked logs
   - `railway logs e9a8c710-ddbd-49c8-a26b-7c984109c922 --build --lines 200`
   - Build succeeded.

7. Health check
   - `curl https://glass-api-production.up.railway.app/health`
   - Initial result: `502 Application failed to respond`

## Issue Found + Fix

### Problem
The service was healthy internally, but Railway health checks were targeting `/api/v1/health` from `railway.toml`, while the API exposes infra health endpoint at `/health`.

Observed in runtime logs:
- `Route GET:/api/v1/health not found` (404)

### Fix Applied
Updated `railway.toml`:
- `healthcheckPath = "/api/v1/health"` → `healthcheckPath = "/health"`

Redeployed:
- `railway up --detach`
- New deployment ID: `5ad4f783-74e7-4ce1-9d7f-2f4388322fd1`

Verified runtime log for healthcheck:
- incoming request to `/health`
- response `statusCode: 200`

Final health check:
- `curl https://glass-api-production.up.railway.app/health`
- Result: `200`
- Body: `{"status":"ok","timestamp":"2026-02-11T17:16:42.607Z","uptime":9.962606306}`

## Railway Config Change Summary

File changed:
- `projects/glass/src/railway.toml`

Current relevant config:
- Build Dockerfile: `services/api/Dockerfile`
- Healthcheck path: `/health`
- Healthcheck timeout: `100`
