---
name: ui-ux-pro-max
description: |-
  Use when: user needs UX flows, information architecture, design critique, or design-system tokens. Don't use when: building a full static site (use frontend-design-ultimate) or redesigning an existing app (use human-optimized-frontend). Routing tree: "Building new site from scratch?" → frontend-design-ultimate; "Need UX critique or design tokens?" → ui-ux-pro-max; "Redesigning existing frontend with quantified eval?" → human-optimized-frontend; "Need design workflow (wireframe → theme → code)?" → frontend-design (superdesign); "Extracting design from existing codebase?" → frontend-design-extractor
---

Follow these steps to deliver high-quality UI/UX output with minimal back-and-forth.

## 1) Triage
Ask only what you must to avoid wrong work:
- Target platform: web / iOS / Android / desktop
- Stack (if code changes): React/Next/Vue/Svelte, CSS/Tailwind, component library
- Goal and constraints: conversion, speed, brand vibe, accessibility level (WCAG AA?)
- What you have: screenshot, Figma, repo, URL, user journey

If the user says "全部都要" (design + UX + code + design system), treat it as four deliverables and ship in that order.

## 2) Produce Deliverables (pick what fits)
Always be concrete: name components, states, spacing, typography, and interactions.

- **UI concept + layout**: Provide a clear visual direction, grid, typography, color system, key screens/sections.
- **UX flow**: Map the user journey, critical paths, error/empty/loading states, edge cases.
- **Design system**: Tokens (color/typography/spacing/radius/shadow), component rules, accessibility notes.
- **Implementation plan**: Exact file-level edits, component breakdown, and acceptance criteria.

## 3) Use Bundled Assets
This skill bundles data you can cite for inspiration/standards.

- **Design intelligence data**: Read from `skills/ui-ux-pro-max/assets/data/` when you need palettes, patterns, or UI/UX heuristics.
- **Upstream reference**: If you need more phrasing/examples, consult `skills/ui-ux-pro-max/references/upstream-skill-content.md`.

## 4) Optional Script (Design System Generator)
If you need to quickly generate tokens and page-specific overrides, use the bundled script:

```bash
python3 skills/ui-ux-pro-max/scripts/design_system.py --help
```

Prefer running it when the user wants a structured token output (ASCII-friendly).

## Output Standards
- Default to ASCII-only tokens/variables unless the project already uses Unicode.
- Include: spacing scale, type scale, 2-3 font pair options, color tokens, component states.
- Always cover: empty/loading/error, keyboard navigation, focus states, contrast.
