# GLASS Frontend API Integration Log

**Date:** 2026-02-11  
**Task:** Replace hardcoded mock data with real API calls to backend endpoints

---

## Summary

Frontend has been wired to use real API endpoints. Mock data still available behind `VITE_USE_MOCK` flag for local development. All pages now have proper loading states and error handling with retry functionality.

---

## Files Changed

### 1. `/apps/web/src/types/index.ts`
- **Added:** `Profile` interface combining `User` and `Operator` for `/api/v1/profile` endpoint

### 2. `/apps/web/src/api/client.ts`
- **Added:** `getProfile()` method calling `GET /api/v1/profile`
- **Added:** `Profile` type import

### 3. `/apps/web/src/api/hooks.ts`
- **Added:** `useProfile()` hook with React Query integration
- **Returns:** `{ user, operator }` for current authenticated user
- **Cache time:** 5 minutes

### 4. `/apps/web/src/layouts/DashboardLayout.tsx`
- **Before:** Hardcoded `operatorName="GreenLeaf Dispensary"`
- **After:** Uses `useProfile()` hook to fetch operator name dynamically
- **Added:** Loading state with spinner when profile is loading
- **Added:** Uses `useAlerts({ read: false })` for real-time unread count

### 5. `/apps/web/src/pages/ThreatRadar.tsx`
- **Before:** Inline `mockThreats` array with hardcoded data
- **After:** Uses `useThreats()` and `useThreatFeed()` hooks
- **Added:** Loading skeletons
- **Added:** Error state with retry button
- **Added:** Severity and type filters using query params
- **Added:** Dynamic threat count badges

### 6. `/apps/web/src/pages/Recommendations.tsx`
- **Before:** Inline `mockRecommendations` array with hardcoded data
- **After:** Uses `useRecommendations()` hook with mutations
- **Added:** `useApplyRecommendation()` and `useDismissRecommendation()` mutations
- **Added:** Loading skeletons
- **Added:** Error state with retry button
- **Added:** Status filter (all/pending/applied/dismissed)
- **Added:** Real-time stats calculation from API data

### 7. `/apps/web/src/pages/Alerts.tsx`
- **Before:** Inline `mockAlerts` array with hardcoded data
- **After:** Uses `useAlerts()`, `useMarkAlertRead()`, `useDismissAlert()` hooks
- **Added:** Loading skeletons
- **Added:** Error state with retry button
- **Added:** Filter tabs (all/unread/critical/high/medium)
- **Added:** Proper timestamp formatting (2m ago, 1h ago, etc.)
- **Added:** Dynamic icon and color mapping based on alert type/severity

### 8. `/apps/web/src/pages/MorningBrief.tsx`
- **Before:** Some hardcoded stats values
- **After:** Better null-safety with optional chaining (`?.`)
- **Improved:** Stats calculation to handle missing API data gracefully

---

## API Endpoints Status

### ✅ Implemented in Frontend

| Endpoint | Method | Hook | Status |
|----------|--------|------|--------|
| `/api/v1/profile` | GET | `useProfile()` | **NEW - Needs backend** |
| `/api/v1/prices` | GET | `usePrices()` | Existing |
| `/api/v1/prices/movers` | GET | `usePriceMovers()` | Existing |
| `/api/v1/threats` | GET | `useThreats()` | Existing |
| `/api/v1/threats/feed` | GET | `useThreatFeed()` | Existing |
| `/api/v1/recommendations` | GET | `useRecommendations()` | Existing |
| `/api/v1/recommendations/:id/apply` | POST | `useApplyRecommendation()` | Existing |
| `/api/v1/recommendations/:id/dismiss` | POST | `useDismissRecommendation()` | Existing |
| `/api/v1/alerts` | GET | `useAlerts()` | Existing |
| `/api/v1/alerts/:id` | PATCH | `useMarkAlertRead()` | Existing |
| `/api/v1/alerts/:id/dismiss` | POST | `useDismissAlert()` | Existing |
| `/api/v1/dashboard/morning-brief` | GET | `useMorningBrief()` | Existing |

### ⚠️ Backend Endpoint Needed

The following endpoint **does not exist in the backend yet** and needs to be implemented:

```
GET /api/v1/profile
```

**Expected Response:**
```json
{
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "operator_id": "string",
    "role": "owner" | "admin" | "viewer"
  },
  "operator": {
    "id": "string",
    "name": "string",
    "license_number": "string",
    "city": "string",
    "state": "string",
    "status": "active" | "inactive" | "pending" | "suspended",
    "created_at": "ISO date string",
    "updated_at": "ISO date string"
  }
}
```

**Purpose:** Get current authenticated user and their associated operator in a single request for the dashboard header.

---

## How to Test Locally

### Option 1: With Mock Data (Default)
```bash
cd apps/web
npm run dev
```
- Mock data served from `/apps/web/src/api/mock.ts`
- `Alex Johnson` + `GreenLeaf Dispensary` will still show (from mock)

### Option 2: With Real Backend
```bash
# Set environment variable
echo "VITE_USE_MOCK=false" >> apps/web/.env.local
echo "VITE_API_URL=https://glass-api-production.up.railway.app/api/v1" >> apps/web/.env.local

cd apps/web
npm run dev
```

**Note:** Backend must be running and have all endpoints implemented. See "Backend Endpoint Needed" section above.

---

## Mock Data Still Available

For development, mock data is still accessible via the `USE_MOCK` flag in `hooks.ts`:

```typescript
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
```

All hooks check this flag and return mock data when enabled.

---

## Known Issues / Notes

1. **Stats in MorningBrief** - Some stats (like "Total Products Tracked") are calculated estimates based on available data, not direct API values. Backend may want to provide these directly.

2. **Error Handling** - All pages now have error states with retry buttons. Errors are logged to console but not shown to user (friendly messages only).

3. **Loading States** - All pages have consistent skeleton loading states matching the layout structure.

---

## Next Steps for Backend

1. Implement `GET /api/v1/profile` endpoint
2. Ensure all other endpoints match the expected response types in `/apps/web/src/types/index.ts`
3. Add CORS policy to allow `glass-web-production.up.railway.app`
4. Test frontend/backend integration end-to-end

---

## Verification Checklist

- [x] No TypeScript errors (`npm run typecheck` passes)
- [x] Build succeeds (`npm run build` succeeds)
- [x] All pages use API hooks
- [x] Loading states added to all pages
- [x] Error handling added to all pages
- [x] Retry functionality added
- [x] Hardcoded "Alex Johnson" removed from DashboardLayout
- [x] Hardcoded "GreenLeaf Dispensary" removed from DashboardLayout
- [x] Inline mock arrays removed from ThreatRadar, Recommendations, Alerts pages
- [x] React Query cache keys properly defined
- [x] Mutations invalidate related queries on success
