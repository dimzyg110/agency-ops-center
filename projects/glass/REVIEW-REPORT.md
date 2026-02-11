# GLASS Architecture & Deployment Review

**Date:** 2026-02-11
**Reviewer:** QA Agent (Subagent)
**Status:** 🔴 **NO-GO** for Pilot

## Executive Summary
The GLASS project has made significant progress with a comprehensive backend schema and a polished frontend UI. However, the **Pilot Launch is blocked** by a critical architectural mismatch in authentication. The frontend is built for Clerk Auth, while the backend implements a custom JWT system. These two are currently incompatible, meaning no frontend user can successfully make API calls to the backend.

Additionally, the frontend is currently operating in "Mock Mode" by default, and the "Real Mode" implementation for user data is missing (`return null`).

## 🔴 Critical Issues (Must Fix)

### 1. Authentication Architecture Mismatch
- **Frontend (`apps/web`):** Uses `@clerk/clerk-react` and `ClerkProvider`. Expects to authenticate via Clerk and receive Clerk session tokens.
- **Backend (`services/api`):** Uses `fastify-jwt` with a custom `users` table and `bcrypt` password hashing. Expects a symmetric-signed JWT from its own `/auth/login` endpoint.
- **Impact:** Any request from the frontend (sending a Clerk token or no token) will be rejected by the backend with `401 Unauthorized`.
- **Fix Required:**
    - **Option A (Recommended):** Update Backend `plugins/auth.ts` to verify Clerk tokens (using JWKS) and sync Clerk users to the local `users` table on the fly.
    - **Option B:** Remove Clerk from Frontend and implement a custom login form that hits `POST /auth/login`.

### 2. Frontend "Mock Mode" Dependency
- **Issue:** `apps/web/src/api/hooks.ts` defaults to `USE_MOCK = true`.
- **Gap:** In `useUser()` hook:
  ```typescript
  if (USE_MOCK) return mock.mockUser;
  // In real implementation, this would validate token and get user
  return null; // <--- MISSING IMPLEMENTATION
  ```
- **Impact:** Even if Auth was fixed, the app would treat every user as "logged out" or "null" when connected to the real API.
- **Fix Required:** Implement the real `useUser` logic to fetch profile data from `GET /auth/me` or `/profile`.

### 3. API Client Token Synchronization
- **Issue:** The `ApiClient` class expects `api.setToken(token)` to be called.
- **Gap:** The Clerk `useAuth()` hook in React provides a token, but there is no code in `App.tsx` or `AuthGuard.tsx` to pass this token to the `ApiClient`.
- **Impact:** API calls will be sent without an `Authorization` header.
- **Fix Required:** Add a `useEffect` in the root component to sync the Clerk token to `api.setToken()`.

## 🟠 Major Warnings (Should Fix)

### 1. Docker Build Context
- **File:** `services/api/Dockerfile`
- **Issue:** The Dockerfile copies `package.json` and runs `npm install` inside the `services/api` directory.
- **Risk:** If the root `package-lock.json` relies on hoisted dependencies (standard in workspaces), the subdirectory install might resolve different versions or fail.
- **Recommendation:** Use a proper monorepo build strategy (e.g., Turbo, or installing from root with workspace filtering).

### 2. Geo-Query Stability
- **File:** `services/api/src/routes/threats.ts`
- **Issue:** Uses manual Haversine formula with `acos()`.
- **Risk:** Floating point precision errors can cause `acos(x)` where `x > 1.0` or `x < -1.0`, causing query crashes.
- **Recommendation:** Clamp the input to `acos` to `[-1, 1]`, or better yet, enable PostGIS and use `ST_DWithin`.

## 🟡 Suggestions (Nice to Have)

1.  **Shared Types:** The `contracts/` folder is referenced in Dockerfile but not clearly used. Ensure `apps/web` and `services/api` share TypeScript types (e.g., via a shared workspace package) to prevent schema drift.
2.  **Environment Variables:** Ensure `JWT_SECRET` and `CORS_ORIGIN` are strictly enforced in production (Backend already does this, which is good).

## Deployment Configuration Review
- **Railway:** Root `railway.toml` correctly points to `services/api/Dockerfile`.
- **Health Checks:** `/health` endpoint is implemented and configured.
- **Restart Policy:** Configured correctly.

## Scraper Integration
- **Status:** ✅ **Healthy**
- **Data Flow:** Scraper -> Postgres -> API. This decoupling is good.
- **Dependencies:** Redis and Postgres connections are configured correctly.

## Final Recommendation
**NO-GO for Pilot.**
The system cannot function in its current state. The Auth mismatch is a hard blocker.

**Next Steps:**
1.  Assign a Backend Engineer to implement Clerk Token Verification in `services/api`.
2.  Assign a Frontend Engineer to wire up the Clerk token to `ApiClient` and implement real data fetching in `useUser`.
3.  Retest the full login flow.
