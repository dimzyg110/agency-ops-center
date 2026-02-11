# GLASS PostgreSQL Setup

## Step 1: Create New Postgres Database

1. Open Railway dashboard: https://railway.app/project/125c58a9-0472-4e7d-88a1-463258e2ed5f
2. Click "+ New" → "Database" → "Add PostgreSQL"
3. Service name: `glass-postgres`
4. Wait for deployment (~30 seconds)

## Step 2: Link Services to New Database

### For glass-api service:
1. Go to glass-api service settings
2. Variables tab
3. Update `DATABASE_URL` to reference the new `glass-postgres` service
   - Remove old DATABASE_URL
   - Click "+ New Variable" → "Add Reference"
   - Select `glass-postgres` → `DATABASE_URL`
4. Save and redeploy

### For glass-scraper service (when created):
- Same process: reference glass-postgres DATABASE_URL

## Step 3: Run Migrations

From your local machine:
```bash
cd projects/glass/src/services/api
railway run --service glass-api 'npm run db:push'
```

Or COO can run after the new DB is linked.

## Step 4: Verify

```bash
curl https://glass-api-production.up.railway.app/health
# Should still return 200 OK
```

---

**Current State:**
- ✅ API deployed and running
- ✅ Redis ready
- ✅ Scraper Dockerfile ready
- ⏳ Need fresh Postgres (you create in dashboard)
- ⏳ Need scraper service created (you create in dashboard)

Once you create the new Postgres and link it to glass-api, ping me and I'll run the migrations + deploy scrapers.
