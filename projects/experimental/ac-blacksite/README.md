# AC Blacksite

**Code Repo:** `/Users/randytorres/Projects/ac-labs`

## Overview
Native iOS app modeled after MSCHF - a platform for drops, challenges, and exclusive experiences. **Frontend 95% complete**, backend stubbed.

**Inspiration:** MSCHF app (viral drops, limited releases, gamified experiences)

**Status:** Production-quality UI prototype, needs Firebase backend integration

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Platform | iOS 16+ (Native) |
| Framework | Swift + SwiftUI |
| Backend | Firebase (scaffolded, not implemented) |
| Auth | Apple/Google/Email (UI complete, mocked) |
| Database | Firestore (stubbed, using UserDefaults) |
| Config | Remote Config (stubbed) |

**Codebase:** 43 Swift source files

---

## Current Capabilities

### Working Features ✅

**Onboarding Flow**
- Cinematic intro with typewriter effects
- Intent selection (OBSERVE / WAIT / PARTICIPATE)
- Auth screen (Apple/Google/Email UI)
- Terminal verification animation
- Access granted video playback
- Full navigation to main app

**Ledger (Main Feed)**
- Operation list with status badges (active/locked/archived/redacted)
- Live indicator pulsing
- Last sync timestamp
- Ghost rows (8-24) for upcoming operations
- Navigation to operation details

**Access Control System**
- Locked operation view (sealed appearance)
- Token/code entry (terminal-style input)
- Verification flow with haptic + sound feedback
- Access state persistence (UserDefaults)
- Participation declaration submission
- Success/error states with delays

**Archived Operations**
- Content vault display (photos/videos grid)
- Media viewer with fullscreen
- Attendance counter

**Progressive Time-Locked Reveals**
- >48h: Locked (minimal info)
- 48h: City confirmed
- 24h: Venue address
- 2h: Entry instructions
- Event time: Full details

**Visual Design**
- Terminal aesthetic (Menlo fonts, grain overlay, scanlines, vignette)
- Gold accent color (#C9A227)
- Smooth animations and transitions
- Haptic feedback on interactions
- Sound effects (metallic click, industrial thud, access granted/denied)

**Data Models Implemented**
- User (id, intent, clearance level)
- Operation (full spec with access control, time-locked reveals, capacity)
- ParticipationDeclaration (status tracking)
- Briefing (intel drops)
- Announcement (system messages)

### Stubbed/Incomplete ❌

**Backend (All Mocked)**
- Firebase Auth not connected (credentials captured but not exchanged)
- Firestore operations return hardcoded mock data
- Remote Config not implemented
- No real database writes

**Features Awaiting Backend**
- Real authentication persistence
- Participation declaration submission to server
- Push notifications for briefings
- Actual media loading (URLs are placeholders)
- Analytics/tracking
- Approval/denial workflow for declarations

---

## App Flow

```
Cinematic Intro → Intent Selection → Auth → Terminal Verification → Access Video → Ledger (Main)
                                                                                      ↓
                                                                              Operation Detail
                                                                              (Locked/Code Entry/Unlocked)
                                                                                      ↓
                                                                              Archived Operations
                                                                              (Content Vault)
```

---

## Key Screens

| Screen | Status |
|--------|--------|
| CinematicIntroView | ✅ Complete |
| IntentSelectionView | ✅ Complete (with video) |
| AuthenticationView | ✅ UI complete (backend mocked) |
| TerminalVerificationView | ✅ Complete |
| AccessGrantedVideoView | ✅ Complete |
| LedgerView | ✅ Complete |
| OperationDetailView | ✅ Complete (3 sub-views) |
| ArchivedOperationView | ✅ Complete |
| SettingsView | ✅ Complete |
| DossierView | ⚠️ Minimal |
| SecureCommsView | ⚠️ Minimal |

---

## To Go Live

### Backend Integration Required
- [ ] Implement Firebase Auth (Apple/Google/Email token exchange)
- [ ] Implement Firestore CRUD for operations/users/declarations
- [ ] Set up Remote Config for active operation control
- [ ] Add push notifications for briefings
- [ ] Implement real media delivery (Firebase Storage or CDN)
- [ ] Build approval workflow for participation declarations

### Deployment
- [ ] TestFlight configuration
- [ ] App Store Connect setup
- [ ] Environment configs (dev/staging/prod)

---

## Design System

**Colors:**
- Background: Pure black
- Accent: Gold (#C9A227)
- Text: White, Gold variants
- Status: Green (active), Red (denied), Amber (pending)

**Typography:**
- Menlo (monospace, terminal feel)
- Courier (secondary)

**Effects:**
- Grain overlay
- Scanline vignette
- Ember particle effects

---

## Assets

- `ac-logo.mp4` - Animated logo for onboarding
- Exit/Participate images (1.9-2MB PNGs)
- System sounds (click, thud, beep, access granted/denied)
- iOS app icons in asset catalog

---

## Estimated Completion

- **Frontend:** 95% complete
- **Backend:** 5% complete (scaffolding only)
- **Overall:** 40-50% to production
