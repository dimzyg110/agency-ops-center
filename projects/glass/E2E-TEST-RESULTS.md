# GLASS Frontend E2E Test Results (Playwright)

**Date (UTC):** 2026-02-11T20:33:32Z  
**URL tested:** https://glass-web-production.up.railway.app/  
**Test email used:** test-glass-user@roviq.ai

## Summary
- The app loads and shows a **Clerk-powered auth UI**.
- Initial route shows **Sign In** UI, not full app data/dashboard.
- The visible Sign Up link in DOM is inside a **hidden Clerk footer** (`cl-footer hidden`) on initial page.
- Direct navigation to `/signup` works and shows signup form fields.
- Signup submit was attempted with email + password, but there was **no clear success or error message** in this run.
- No critical JS crashes observed, but there is a **401 console/network resource error** and CSP warning.
- API/network calls are definitely being made (Clerk + Cloudflare Turnstile endpoints observed).

## What the page actually shows
### Initial page (`/`)
- Branded GLASS auth wrapper.
- Clerk Sign In UI with:
  - Continue with Google
  - Email address + Password
  - Continue button
- Footer area in Clerk includes Sign Up link in markup, but the footer is hidden by class.

### Signup page (`/signup`, direct navigation)
- Signup screen text like:
  - "Start with GLASS"
  - "Get Price Wire in 60 seconds. No credit card required."
- Fields present:
  - First name (optional)
  - Last name (optional)
  - Email address
  - Password
- Continue button present.

## Clerk auth status
- **Clerk loaded:** Yes (`cl-*` components detected).
- **Initial Sign In visible:** Yes.
- **Sign Up visible on initial page:** No (link exists in hidden footer).
- **Signup attempt:** Performed on `/signup` with email `test-glass-user@roviq.ai` and password `TestGlass123!`.
- **Result:** No explicit verification/success/error UI was detected after submit in this run.

## Data displayed after auth attempt
- Login/signup completion could not be confirmed.
- Test remained on auth surface (`/signup`), so no operator/dashboard/business data was displayed.

## JavaScript / Console errors observed
- `Note that 'script-src' was not explicitly set, so 'default-src' is used as a fallback.`
- `%c%d font-size:0;color:transparent NaN` (appeared twice)
- `Failed to load resource: the server responded with a status of 401 ()`

## API calls observed (verification that calls are being made)
Sample captured calls:
- `GET https://humane-dinosaur-0.clerk.accounts.dev/npm/@clerk/clerk-js@5/dist/clerk.browser.js`
- `POST https://humane-dinosaur-0.clerk.accounts.dev/v1/dev_browser?...`
- `POST https://humane-dinosaur-0.clerk.accounts.dev/v1/environment?...`
- `GET https://humane-dinosaur-0.clerk.accounts.dev/v1/client?...`
- `GET .../signin_clerk.browser_...js`
- `GET .../signup_clerk.browser_...js`
- `GET https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit`
- Cloudflare challenge flow requests (`/cdn-cgi/challenge-platform/...`)

## Screenshots
Saved to:
- `/tmp/glass-test-1-initial.png`
- `/tmp/glass-test-2-signup-page.png`
- `/tmp/glass-test-3-email-filled.png`
- `/tmp/glass-test-4-submitted.png`

## Notes
- Initial UI appears to prioritize Sign In and hides the Sign Up footer action.
- Because signup did not surface an explicit completion/verification state in this run, a follow-up test with deeper Clerk flow assertions (verification code/email delivery, captcha state, and response payload inspection) is recommended.
