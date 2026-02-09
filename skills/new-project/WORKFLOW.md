# New Project Pipeline

**Trigger:** Randy has an idea, or a strategic opportunity surfaces.
**Goal:** Go from raw idea → validated concept → designed + planned → iterative execution.
**Standard:** Only quality projects survive. We have standards now.

---

## Phase 1: Idea Capture

**Who:** Randy or COO
**Time:** 5 min

1. Create: `projects/experimental/<project-name>/IDEA.md`
2. Fill in:
   ```markdown
   # [Project Name]

   - One-line pitch:
   - Problem it solves:
   - Who it's for:
   - How it makes money:
   - Why now:
   - Randy's conviction (1-10):
   ```
3. Status: `IDEA`

---

## Phase 2: Research & Validation

**Who:** COO spawns research agents
**Time:** ~30-60 min agent time

### Spawn 3 Research Agents:

#### Agent 1: Market & Competitor Research

```
Research the market for [project idea]. Find existing competitors,
similar products, market size, trends. Is anyone doing this already?
What's the gap? What's the TAM?
Save to: projects/experimental/<name>/research/market-research.md
```

#### Agent 2: Technical Feasibility

```
Evaluate the technical feasibility of [project idea]. What tech stack
would this require? How long to build an MVP? What are the hard parts?
Any existing tools/APIs that make this easier? Estimate dev time.
Save to: projects/experimental/<name>/research/tech-feasibility.md
```

#### Agent 3: Business Model Validation

```
Evaluate [project idea] as a business. Pricing models, revenue potential,
customer acquisition strategy, unit economics. Does this make money?
How does it fit into Roviq's existing ecosystem? Can it leverage our
existing assets (lead data, newsletter, client base)?
Save to: projects/experimental/<name>/research/business-validation.md
```

### Quality Gate: Kill or Continue

COO compiles research into `VALIDATION-SUMMARY.md`. Randy decides:

- **KILL** → Move to `projects/experimental/_archive/` with kill reason
- **CONTINUE** → Proceed to Phase 3

> **Standard:** If it doesn't have a clear path to revenue, strong market signal, AND Randy conviction ≥ 7, it dies here. We only build quality shit.

---

## Phase 3: Design & Brand

**Who:** COO spawns design + strategy agents
**Time:** ~1-2 hours agent time

### 3a. Brand Identity

```
Create brand identity for [project]. Name validation (if needed),
color palette, typography, visual direction, tone of voice.
Reference Roviq's aesthetic (premium, cinematic, cannabis-forward if relevant).
Save to: projects/experimental/<name>/design/brand-identity.md
```

### 3b. Landing Page Design

```
Design a landing page for [project]. Create HTML/CSS mockup.
Must be: Premium aesthetic, clear value prop, single CTA, mobile-first.
Follow Roviq design standards (dark mode, gradients, micro-animations).
Save to: projects/experimental/<name>/design/landing-page/
```

### 3c. GTM Strategy

```
Create go-to-market strategy for [project]. Launch plan, first 100 users,
growth channels, content strategy, partnership opportunities.
Remember: we don't cold sell. Value-first approach.
Save to: projects/experimental/<name>/strategy/gtm-strategy.md
```

### Review Cycle

- Spawn 2 reviewers (different models) for each deliverable
- COO synthesizes feedback
- Randy reviews final versions

---

## Phase 4: Planning & Architecture

**Who:** COO spawns planning agents
**Time:** ~1-2 hours agent time

### 4a. Product Requirements (PRD)

```
Write PRD for [project] MVP. Based on approved design and GTM.
Include: user stories, feature list (P0/P1/P2), success metrics,
tech stack recommendation, data model if applicable.
Save to: projects/experimental/<name>/PRD.md
```

### 4b. Development Plan

```
Create development plan for [project]. Break into 1-week sprints.
Sprint 1 must produce a working demo. Each sprint should have
clear deliverables and success criteria.
Save to: projects/experimental/<name>/DEV-PLAN.md
```

### 4c. Growth Plan

```
Create 90-day growth plan for [project] post-launch.
Week 1-2: Launch tactics. Week 3-4: First optimizations.
Month 2-3: Scale what works. Include metrics to track.
Save to: projects/experimental/<name>/strategy/growth-plan.md
```

### Quality Gate: Ready for Build?

Randy reviews PRD + DEV-PLAN + GROWTH-PLAN. Decides:

- **APPROVED** → Move to `projects/internal/<name>/`, begin Sprint 1
- **ITERATE** → Specific changes needed, back to relevant phase
- **KILL** → Archive with reason

---

## Phase 5: Iterative Execution

**Who:** COO coordinates dev, design, and review agents
**Time:** Ongoing, 1-week sprint cycles

### Each Sprint:

1. COO defines sprint tasks from DEV-PLAN
2. Spawn developer agents for each task
3. Spawn 2 reviewers per deliverable
4. COO synthesizes reviews
5. Randy reviews sprint output
6. Update DEV-PLAN with progress
7. Plan next sprint

### Sprint Deliverables:

- Working code/demo
- Updated docs
- Sprint retrospective (what worked, what didn't)

---

## File Structure

```
projects/experimental/<project-name>/
├── IDEA.md                    # Initial capture
├── VALIDATION-SUMMARY.md      # Research summary + Randy's decision
├── research/
│   ├── market-research.md
│   ├── tech-feasibility.md
│   └── business-validation.md
├── design/
│   ├── brand-identity.md
│   └── landing-page/
├── strategy/
│   ├── gtm-strategy.md
│   └── growth-plan.md
├── PRD.md                     # Product requirements
└── DEV-PLAN.md                # Sprint breakdown

# When approved → moves to:
projects/internal/<project-name>/
├── (all above files)
├── src/                       # Code
├── sprints/
│   ├── sprint-1-retro.md
│   └── sprint-2-retro.md
└── CHANGELOG.md
```

---

## Quality Standards

> **We only build quality shit.**

| Gate              | Criteria                                       | Enforcer    |
| ----------------- | ---------------------------------------------- | ----------- |
| Idea → Research   | Conviction ≥ 7, clear revenue path             | Randy       |
| Research → Design | Market validated, technically feasible         | Randy       |
| Design → Build    | 2+ reviews passed, Randy approved              | COO + Randy |
| Each Sprint       | 2+ code reviews, working demo                  | COO         |
| Ship → Launch     | GTM ready, landing page live, metrics tracking | Randy       |
