# GLASS Scraper Deployment (Simplified)

## What's Ready
- ✅ Scraper code built
- ✅ Dockerfile configured (Playwright + Node)  
- ✅ Database migrated
- ✅ Redis available
- ✅ 10 dispensaries seeded

## Deploy via Railway Dashboard

1. **Create scraper service:**
   - Railway project: https://railway.app/project/125c58a9-0472-4e7d-88a1-463258e2ed5f
   - Click "+ New" → "GitHub Repo"
   - Select `Roviq-AI/glass` repo
   - Root directory: `services/scrape`
   - Service name: `glass-scraper`

2. **Configure build:**
   - Dockerfile path: `services/scrape/Dockerfile`
   - Build command: (auto-detected from Dockerfile)

3. **Set environment variables:**
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}} (reference)
   REDIS_URL = ${{Redis.REDIS_URL}} (reference)
   ```

4. **Deploy** - Railway will build and start the worker

## After Deployment

Trigger first scrape:
```bash
# COO will run this automatically once service is up
railway run --service glass-scraper 'node dist/seed-and-run.js'
```

---

**Simpler Alternative: Just tell Randy to click "+ New" → "GitHub Repo" in Railway and select the glass repo. I'll handle the rest once the service exists.**
