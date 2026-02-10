# Research: Massachusetts Cannabis Delivery Mobile App Gap

**Status:** The claim that "no cannabis delivery operator in Massachusetts has built their own mobile app" is **substantively correct**, with important nuances regarding *web apps* vs. *native apps* and recent third-party partnerships.

## 1. Has anyone tried and failed? (The "Graveyard" & Current Status)
*   **Lantern (Marketplace):** **Yes, tried and failed.** Lantern launched the "first shoppable cannabis marketplace app" on iOS in November 2022. However, they **shut down operations in January 2023** (just 2 months later) citing regulatory hurdles and capital constraints.
    *   *Source:* [Lantern Expands with iOS App](https://www.prnewswire.com/news-releases/lantern-expands-on-demand-cannabis-delivery-service-with-ios-app-301676382.html) | [Lantern Closure](https://www.reddit.com/r/bostontrees/comments/105ois9/lantern_closure_shakes_marijuana_delivery_market/)
*   **Zyp Run (Operator):** **No native app.** Despite raising $2.6M, Zyp Run does **not** have a consumer-facing native app on the App Store or Google Play. The "Zyp" app currently on the App Store is for an electric scooter company. Zyp Run relies entirely on a mobile-optimized web platform (PWA) at `app.zyprun.com`.
*   **Rolling Releaf:** **No native app.** They use a mobile-optimized website and accept "Mobile Prepayment," but do not have a standalone store app. The "Releaf App" found in search is a separate strain-tracking journal, not a store.
*   **Happy Valley:** **No delivery app.**

## 2. Is it a regulatory barrier? (The "Google Wall")
*   **Google Play Store (Android):** **YES, CRITICAL BARRIER.** Google maintains a strict ban on apps that facilitate the sale or delivery of marijuana (specifically, apps with an in-app shopping cart). This makes it impossible to launch a fully functional native delivery app for Android users.
    *   *Source:* [Google Play Policy](https://support.google.com/googleplay/android-developer/answer/9878810?hl=en)
*   **Apple App Store (iOS):** **Partial Barrier.** Apple lifted its ban in June 2021 for licensed entities (geo-restricted to legal jurisdictions). While *allowed*, the development requires strict geo-fencing compliance.
    *   *Source:* [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
*   **MA State Regulations (935 CMR 500):** **No explicit ban.** State regulations allow for "Third-party Technology Platforms" and digital ordering. The barrier is corporate policy (Google/Apple), not state law.

## 3. Is it an economic/scale issue?
*   **Yes.** Most MA delivery operators are **Social Equity** businesses with limited capital.
*   **Cost:** Developing a native iOS app + maintaining a separate compliant workaround for Android (PWA) costs **$30k–$50k+ upfront** plus ongoing maintenance.
*   **ROI:** With Google banning 50% of the mobile market (Android), operators cannot justify the expense of a native app when a responsive mobile website serves 100% of customers.

## 4. Are there third-party apps?
*   **Jointly x Delivered Inc:** This is the most significant recent development. **Jointly**, a third-party "cannabis discovery" app, partnered with **Delivered Inc** (July 2024) to handle fulfillment in MA.
    *   *Key Insight:* Delivered Inc did *not* build their own app; they are acting as the logistics backend for Jointly's frontend. This reinforces the opportunity to build a *branded* app for an operator, rather than them being a generic fulfillment partner for a tech platform.
    *   *Source:* [Delivered Partners with Jointly](https://talkingjointsmemo.com/inbox-delivered-partners-with-jointly-for-ai-powered-shopping/)
*   **Weedmaps / Leafly:** Act as directories. On iOS, they can sometimes facilitate orders, but on Android, they are restricted to "menu viewing" only (no cart).

## 5. National Competitive Landscape
*   **Eaze:** Has a native iOS app. They are the "Uber of Weed" in CA/MI.
*   **Amuse:** Has a native iOS app.
*   **Pattern:** In mature markets (CA, CO), large venture-backed operators have native iOS apps. In emerging/fragmented markets like MA, operators rely on web.

## 6. What happened to Zyp Run?
*   **Funding:** Raised $2.6M Seed (Jan 2023) led by Satori Investment Partners.
*   **Use of Funds:** Money was used to build their "proprietary e-commerce platform" (the web app `app.zyprun.com`), secure their warehouse/delivery depot in Boston, and hire drivers. It was **not** used to build a native mobile app.
*   **Status:** Active and operating, but strictly web-based.

## Conclusion for Proposal
The claim is valid. **No MA delivery operator possesses a proprietary, branded native app.**
*   **Why?** The Google ban fractures the user base, making native apps a "luxury" iOS-only feature that cash-strapped social equity operators can't justify.
*   **The Opportunity:** A "Progressive Web App" (PWA) that *feels* native (installable on home screen, push notifications) but bypasses App Store bans is the winning strategy. Or, an iOS-exclusive "Premium" experience to capture the high-value iPhone demographic, while using web for Android.
