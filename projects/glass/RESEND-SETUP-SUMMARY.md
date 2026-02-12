# Resend Setup Summary

## Configuration Updated

- **Resend API key behavior**: `scripts/auto-invite/send-invites.ts`
  - Now reads `process.env.RESEND_API_KEY` first.
  - Falls back to `re_SX85Q1HR_71ngYcBTXSxyKCekzhJyGpH2` for testing only.
- **From address**: `scripts/auto-invite/generate-email.ts`
  - Default sender updated to `GLASS <glass@mail.roviqai.xyz>`.
- **Branding and links**: `scripts/auto-invite/generate-email.ts`
  - Header now uses **GLASS by Roviq** branding.
  - Primary CTA link updated to: `https://glass-web-production.up.railway.app/market`.
- **CAN-SPAM footer**: `scripts/auto-invite/generate-email.ts`
  - Physical address updated to: `Roviq · Boston, MA`.
  - Unsubscribe link now generated per operator:
    - `https://glass-web-production.up.railway.app/unsubscribe?id={operator_id}`

## Template Quality Check

- HTML uses email-client-safe table layout with inline styles.
- No flexbox/grid detected.
- Subject line remains: `"{Operator Name} — Your Market Position This Week"` (compelling, non-spammy).
- Branding aligns with GLASS by Roviq.
- Footer includes physical address and unsubscribe link.

## Test Snapshot Generation

Top operators query result (by product volume) returned:
1. `0c920d2d-8143-4774-b60a-85a305cff264` — Canna Provisions Holyoke (1609)
2. `b481bb4c-e87e-4007-89c1-45eed80decd5` — Elevated Roots (1501)
3. `1c1f1b07-9ab7-45bf-b08d-291ea1eb0ebb` — Cape Cod Cannabis Recreational Dispensary (1440)
4. `87a84271-824f-46e5-80bd-7da88eddb8e7` — Canna Provisions - Lee (1193)
5. `0cdae04c-4f2d-44de-b187-537ef5baf089` — The Haven Center - Brewster (1189)

Preview generated for top operator:
- Operator ID: `0c920d2d-8143-4774-b60a-85a305cff264`
- Subject: `Canna Provisions Holyoke — Your Market Position This Week`
- Preview saved to: `/tmp/test-invite.html`

## Test Send Results

### Dry run
Command:

```bash
RESEND_API_KEY="re_SX85Q1HR_71ngYcBTXSxyKCekzhJyGpH2" \
DATABASE_URL="postgresql://postgres:rcsulogGljjcDcBMxfMeGNlqbmbgHspa@turntable.proxy.rlwy.net:18582/railway" \
npx tsx scripts/auto-invite/index.ts send --limit 1 --dry-run
```

Result:

```json
{
  "processed": 1,
  "sent": 0,
  "skippedNoEmail": 1,
  "skippedAlreadyInvited": 0,
  "skippedSignedUp": 0,
  "errors": 0
}
```

### Actual test email via Resend API
Sent to: `rtorres1331@panther.chaffey.edu`

Resend response:

```json
{
  "status": 200,
  "ok": true,
  "body": "{\"id\":\"2084334d-6bf1-4fcc-89b1-d25d33a063c7\"}"
}
```

## Next Steps for Batch Sending

1. Add a small pre-filter for `send` mode to avoid selecting operators with null email in first pass.
2. Move fallback API key out of code before production rollout (env-only in deployed environments).
3. Add optional `--to` override flag for controlled QA sends without modifying operator data.
4. Add open/click webhook handler wiring to update `auto_invite_log.opened_at` and `clicked_at`.
5. Start with low-volume sends (e.g., 10/hour already enforced), monitor bounce/spam metrics, then ramp.
