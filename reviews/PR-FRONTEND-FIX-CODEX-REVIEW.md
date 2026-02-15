# Review Feedback

## Scores

| Dimension       | Score | Notes |
| --------------- | ----- | ----- |
| Correctness     | 3/5   | API path fix is correct for current env setup, but one fallback regression exists in `Admin.tsx` and one visual border choice is likely too faint. |
| Completeness    | 4/5   | All requested files were updated and target issues were addressed. |
| Quality         | 3/5   | Changes are mostly clean, but commit rationale about “invalid Tailwind classes” is not accurate and one class replacement weakens visual definition. |
| Brief Adherence | 4/5   | Fixes generally match the brief (light-mode contrast + duplicate API prefix removal). |

## Verdict

**APPROVE WITH CHANGES**

## Issues

1. 🟠 **Major — API fallback regression (`apps/web/src/pages/Admin.tsx`):**
   `API` fallback is `https://glass-api-production.up.railway.app` (no `/api/v1`), but requests were changed to `fetch(`${API}/admin/...`)`. If `VITE_API_URL` is missing/misconfigured, this now calls `/admin/...` instead of `/api/v1/admin/...` and breaks.
   **Suggested fix:** make fallback include `/api/v1` OR normalize base URL once (e.g., helper that guarantees one `/api/v1`).

2. 🟡 **Minor — Tailwind validity claim is incorrect (multiple files):**
   The replaced classes were described as invalid, but based on `apps/web/tailwind.config.ts`, classes like `text-glass-black`, `border-glass-black`, and `text-glass-light-muted` are valid custom Tailwind classes (`colors.glass.*`).
   **Suggested fix:** update PR description/notes to reflect this was a design/contrast adjustment, not a compile-validity correction.

3. 🟡 **Minor — Likely visual regression in nav border (`apps/web/src/components/LandingNav.tsx`):**
   Changed `border-glass-light-muted/20` to `border-gray-200/20` for scrolled light mode. This new value is much lighter and may be near-invisible on white, reducing header separation.
   **Suggested fix:** use `border-gray-200` (no `/20`) or restore a stronger equivalent to prior contrast.

4. ⚪ **Nit — `class="light"` on `<html>` (`apps/web/index.html`) appears unnecessary:**
   Tailwind is configured with `darkMode: 'class'`, and I found no app usage of `.light` selectors. This is likely harmless, but currently non-functional noise unless another system relies on it.

## Strengths

- API duplicate-prefix fix is correct for current configured environment (`apps/web/.env` and `.env.example` both include `/api/v1`).
- Light-mode text/button updates in `LandingNav.tsx`, `Footer.tsx`, and `CueSignup.tsx` improve readability and are valid Tailwind classes.
- Changes are scoped and low-risk overall.

## Summary

The routing fix is directionally correct and most UI updates are good, but there is one real fallback regression risk in `Admin.tsx` and one likely subtle visual regression in nav border contrast. With those adjusted, this is ready to ship.
