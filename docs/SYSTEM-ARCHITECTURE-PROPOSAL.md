# System Architecture Proposal — Roviq OpenClaw Setup

**Date:** 2026-02-15  
**Prepared for:** Randy Torres, Roviq  
**Scope:** Strategic architecture recommendations for multi-agent system, shared state, dependency reduction, and modularity

---

## Executive Summary

Roviq's current architecture is a **single-agent (COO) system** managing multiple clients and services through a single OpenClaw instance on Railway. This works for now but creates bottlenecks, single points of failure, and limits scalability. This proposal recommends a transition to a **multi-agent architecture** inspired by ZeroClaw's trait-based design, with clear separation between orchestration, client-specific agents, and shared services.

**Key Recommendations:**
1. Keep the COO as the single orchestration agent (doesn't spawn subagents for itself)
2. Add client-specific specialist agents (one per active client)
3. Decouple scrapers and GLASS API from Railway to edge devices
4. Use ZeroClaw's trait-based approach for swappable components
5. Implement message-passing via a shared event bus (Redis Pub/Sub or SQLite-backed)

---

## 1. Current State Summary

### Infrastructure

| Component | Current State | Location |
|-----------|---------------|----------|
| **OpenClaw (COO)** | Always-on agent | Railway |
| **Dutchie Scraper** | Cron: 08:00 UTC | Railway |
| **Jane Scraper** | Cron: 07:00 UTC | Railway |
| **Leafly Scraper** | Cron: 07:05 UTC | Railway |
| **Weedmaps Scraper** | Cron: 03:30 UTC | Railway |
| **GLASS API** | Node.js service | Railway |
| **Database** | PostgreSQL on Railway | Railway |
| **Memory** | Markdown files in workspace | Local + Git |

### Client Portfolio

| Client | Type | Active Work |
|--------|------|-------------|
| **AC (Advanced Cultivators)** | Brand | Short films, merch, YouTube, weekly content |
| **CH (Cannabis Healing)** | Dispensary | SEO, blog, Alpine automations, Dutchie/Weedmaps |
| **HOP (House of Pride)** | Brand | GTM, website, labels, social launch |
| **Delivered Inc** | (Research/inbound) | TBD |

### Pain Points Identified

1. **Single point of failure**: All clients managed by one agent
2. **Railway dependency**: Scraper services, API, and database all on Railway
3. **Manual client switching**: COO must context-switch between clients during heartbeat
4. **No dedicated scraper agents**: Scrapers run on cron, not as intelligent agents
5. **Memory fragmentation**: Client context lives in markdown files, not queryable
6. **Limited automation**: Weekly content is manual (theme → generate → select → post)

---

## 2. Multi-Agent Architecture

### Recommended: Hub-and-Spoke Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         ROVIQ SYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │     COO      │  ← Orchestrator (always-on, single instance) │
│   │  (Hub Agent) │     • Spawns subagents for client work        │
│   └──────┬───────┘     • Owns cross-client memory               │
│          │               • Revenue tracking & strategic scan     │
│          │               • Human handoff (Randy)                 │
│          │                                                      │
│   ┌──────┴───────┐                                              │
│   │ Message Bus  │  ← Redis Pub/Sub or SQLite-backed queue      │
│   │  (Shared)    │     • Event-driven communication              │
│   └──────┬───────┘     • Client events, scraper triggers         │
│          │                                                      │
│   ┌──────┴──────┐                                               │
│   │             │                                               │
│   ▼             ▼            ┌─────────────┐                   │
│ ┌──────┐   ┌──────┐        │             │                   │
│ │ AC   │   │ CH   │        │  SCRAPER    │                   │
│ │Agent │   │Agent │   ...  │   AGENT     │                   │
│ └──────┘   └──────┘        │  (GLASS)    │                   │
│                             └─────────────┘                   │
│   Client Agents               Dedicated Service Agents          │
│   - AC Agent                  - Scraper Agent                  │
│   - CH Agent                  - API Agent                      │
│   - HOP Agent                 - Consumer Web Agent              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Option A: One Agent Per Client (Recommended)

| Agent | Responsibility | Trigger |
|-------|----------------|---------|
| **COO** | Orchestration, revenue, strategy | 15-min heartbeat |
| **AC Agent** | Content generation, brand tasks | Daily + on-demand |
| **CH Agent** | Dispensary ops, SEO, automations | Daily + on-demand |
| **HOP Agent** | Launch tasks, GTM, website | Project-based |
| **Scraper Agent** | Dutchie/Leafly/Weedmaps/Jane | Scheduled + on-demand |
| **API Agent** | GLASS API maintenance | Monitoring |

**Pros:**
- Clear ownership boundaries
- Client data isolation (each agent has own memory)
- Parallel execution (no blocking on context switch)
- Easier debugging (agent failures isolated)

**Cons:**
- More infrastructure (multiple OpenClaw instances or subagents)
- Coordination overhead (message passing required)
- Potential duplication of shared knowledge

### Option B: Single Agent with Client Context (Current + Evolution)

Keep COO as single agent but add **client sessions** or **context headers** to every task.

```python
# Example: Task with client context
{
  "task": "Generate this week's social content",
  "client": "ac",  # Routes to AC-specific memory/skills
  "context": {
    "brand_voice": "Premium craft cannabis, Mexican/Aztec heritage",
    "active_projects": ["short-films", "merch"]
  }
}
```

**Pros:**
- Simpler infrastructure
- Shared memory by default
- Easier to implement today

**Cons:**
- Doesn't scale beyond 4-5 clients
- Risk of context bleeding
- Single point of failure

### Recommendation

**Start with Option B (context-based) and evolve to Option A (per-client) as volume increases.** Given only 3 active clients, a single COO with client tagging is sufficient today. The architecture should support per-client agents when:
- Client count exceeds 5
- Client work becomes 24/7 (not just daily/weekly)
- Revenue justifies infrastructure cost

---

## 3. Shared State Architecture

### The Problem

Currently:
- Client info lives in `clients/[client-name]/BRIEF.md`
- COO memory in `memory/YYYY-MM-DD.md`
- API keys in `.env` (not accessible to agents)
- Scraper state in Railway PostgreSQL

### Recommended: Three-Layer State

```
┌─────────────────────────────────────────────────┐
│                 LAYER 1: Agent Memory           │
│  (Per-agent, queryable, vector + keyword)      │
│  • AC Agent → AC client memory                 │
│  • CH Agent → CH client memory                 │
│  • COO → Cross-client memory                  │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              LAYER 2: Shared Services           │
│  (PostgreSQL on Railway or edge)               │
│  • GLASS prices                                │
│  • Scraper run history                         │
│  • Client credentials (encrypted)              │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              LAYER 3: Event Bus                │
│  (Redis Pub/Sub or SQLite-backed queue)        │
│  • Agent → Agent messages                      │
│  • Scraper triggers                            │
│  • Notification events                         │
└─────────────────────────────────────────────────┘
```

### State Components

| State Type | Storage | Access |
|------------|---------|--------|
| **Agent memory** | SQLite with FTS5 + vectors | Per-agent (ZeroClaw default) |
| **Client configs** | Git repo (`clients/`) | All agents read |
| **API keys** | Encrypted secrets | Via COO only (security) |
| **GLASS data** | PostgreSQL | Scraper + API agents |
| **Events** | Redis or SQLite | All agents |

### ZeroClaw Memory Integration

ZeroClaw's memory system uses:
- SQLite with FTS5 (keyword search)
- Vector embeddings (cosine similarity)
- Hybrid merge (configurable weights)
- Auto-save and recall via tools

This matches Roviq's needs. Each agent gets:
```toml
[memory]
backend = "sqlite"
auto_save = true
embedding_provider = "openai"
vector_weight = 0.7
keyword_weight = 0.3
```

---

## 4. Dependency Reduction: Decoupling from Railway

### Current Railway Dependencies

| Service | Criticality | Decoupling Option |
|---------|-------------|-------------------|
| **PostgreSQL** | Critical | Keep for now (GLASS needs it) |
| **Scrapers** | High | Move to edge (ZeroClaw on Pi) |
| **GLASS API** | High | Move to edge or keep Railway |
| **COO Agent** | Critical | Keep Railway or move to home server |

### Decoupling Roadmap

**Phase 1: Move Scrapers to Edge (ZeroClaw)**

Scrapers are the highest-risk component on Railway:
- Rate limiting from dispensary APIs
- IP bans from anti-bot protection
- Cost for compute hours

**Recommendation:** Deploy ZeroClaw instances on Raspberry Pi ($10) at the office:
- One ZeroClaw per scraper (Dutchie, Leafly, Weedmaps, Jane)
- Runs 24/7 with <5MB RAM
- Direct access to GLASS database
- Scheduled runs via ZeroClaw heartbeat

**Phase 2: Move COO to Home Server or Edge**

If Railway goes down, Roviq loses:
- COO heartbeat
- All client coordination
- Discord communication

**Recommendation:** Run COO on:
1. **Home server** (Linux box or Mac Mini at office)
2. **Raspberry Pi** (if ZeroClaw is adopted)
3. **Backup Railway instance** (failover)

**Phase 3: Keep GLASS API on Railway**

The GLASS API is a web service requiring:
- HTTPS/TLS
- Public webhook endpoints
- Consistent uptime

**Recommendation:** Keep GLASS API on Railway for now. It's a web service, not an agent, and Railway is appropriate for HTTP services.

### Cost Comparison

| Setup | Monthly Cost | Capability |
|-------|--------------|------------|
| **Current: All Railway** | ~$100+/month | Full OpenClaw |
| **Proposed: Edge COO** | $10 (Pi) + $0 (GLASS API) | ZeroClaw |
| **Proposed: Edge Everything** | $40 (4 Pi) | ZeroClaw x4 |

---

## 5. Modularity: What Should Be Separate Services

### Current Architecture (Monolithic-ish)

```
┌─────────────────────────────────────┐
│           Railway                   │
│  ┌─────────────────────────────┐   │
│  │      OpenClaw (COO)         │   │
│  │  ┌─────────────────────┐   │   │
│  │  │ Scraper Services   │   │   │
│  │  │ (dutchie, jane...) │   │   │
│  │  └─────────────────────┘   │   │
│  │  ┌─────────────────────┐   │   │
│  │  │   GLASS API        │   │   │
│  │  └─────────────────────┘   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Recommended Architecture (Modular)

```
┌─────────────────────────────────────────────────────────────────┐
│                     COO (Orchestrator)                          │
│                   OpenClaw / ZeroClaw                          │
│          - Heartbeat        - Spawns subagents                  │
│          - Strategy         - Revenue tracking                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Client Agents  │ │  Scraper Agent  │ │   API Service   │
│  (Subagents)    │ │   (ZeroClaw)    │ │   (Node.js)     │
│  - AC           │ │  - Dutchie      │ │   - GLASS       │
│  - CH           │ │  - Leafly       │ │   - Routes      │
│  - HOP          │ │  - Weedmaps     │ │   - Auth        │
│                 │ │  - Jane         │ └─────────────────┘
└─────────────────┘ └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Railway)     │
                    └─────────────────┘
```

### Separation Criteria

| Component | Should Be | Rationale |
|-----------|-----------|------------|
| **Client work (content, automations)** | Subagent of COO | Lightweight, spawn-on-demand |
| **Scrapers (scheduled, heavy)** | Separate service | Long-running, rate-limited |
| **GLASS API (HTTP)** | Separate service | Web service, not agent |
| **Memory/memory** | Integrated | Agent needs context |
| **Credentials/keys** | Centralized (COO) | Security boundary |

---

## 6. Communication: How Agents Talk

### ZeroClaw's Approach

ZeroClaw uses **channels** for communication:
- CLI (local)
- Telegram, Discord, Slack (messaging)
- Webhooks (HTTP)

For Roviq's multi-agent system, we recommend:

### Option A: Message Bus (Recommended)

```
Agent A                    Agent B
   │                          │
   ├───publish(event)────────►│
   │    (Redis/queue)         ├──► process()
   │                          │
```

**Implementation:**
- Redis Pub/Sub (if Redis available)
- SQLite-backed queue (ZeroClaw fallback)
- Message schema:
```json
{
  "type": "scraper_complete",
  "source": "scraper-agent",
  "payload": {
    "platform": "dutchie",
    "prices_updated": 1420,
    "run_id": "abc-123"
  },
  "timestamp": "2026-02-15T08:00:00Z"
}
```

### Option B: Shared Memory (Simpler)

Each agent reads from a shared memory store:
- `memory/shared/events.md` — event log
- `memory/shared/scraper-status.md` — latest run status
- Agents poll periodically (less efficient)

### Option C: Webhooks (ZeroClaw Native)

Use ZeroClaw's built-in webhook channel:
- Each agent exposes `/webhook` endpoint
- Messages POSTed as JSON
- Requires network connectivity

### Recommendation

**Start with Option B (shared memory) for simplicity, evolve to Option A (message bus) when agents need real-time communication.**

For now:
- COO spawns subagents synchronously (no async messaging needed)
- Scraper results written to PostgreSQL → COO reads on next heartbeat
- Client work happens in subagent sessions (memory isolated)

---

## 7. Architecture Options Summary

### Option 1: Minimal Change (Quick Win)

| Change | Effort | Benefit |
|--------|--------|---------|
| Add client tagging to tasks | Low | Better context isolation |
| Implement SQLite memory per subagent | Low | Better recall |
| Add scraper status to shared memory | Low | Visibility |

**Timeline:** 1-2 weeks

### Option 2: ZeroClaw Migration (Medium Term)

| Change | Effort | Benefit |
|--------|--------|---------|
| Deploy ZeroClaw for scrapers | Medium | Edge deployment, cost savings |
| Migrate COO to ZeroClaw | Medium | Lower resource usage |
| Add Redis for message bus | Medium | Real-time agent comms |

**Timeline:** 1-2 months

### Option 3: Full Multi-Agent (Long Term)

| Change | Effort | Benefit |
|--------|--------|---------|
| One agent per client | High | Complete isolation |
| Edge deployment (all Pi) | High | Zero Railway dependency |
| Custom message bus | High | Full control |

**Timeline:** 3-6 months

---

## 8. Next Steps

### Immediate (This Week)

1. **Audit current scraper health** — Confirm which scrapers are actually running on Railway
2. **Document client contexts** — Create structured client profiles in `clients/[name]/`
3. **Test subagent spawning** — Verify COO can spawn isolated subagents per client

### Short-Term (This Month)

1. **Deploy ZeroClaw for one scraper** — Start with Dutchie on a Raspberry Pi
2. **Set up shared memory** — Create `memory/shared/` for cross-agent context
3. **Add client memory isolation** — Each subagent gets own SQLite memory

### Medium-Term (This Quarter)

1. **Migrate COO to ZeroClaw** — If edge deployment proves stable
2. **Implement message bus** — Add Redis for event-driven communication
3. **Evaluate per-client agents** — If client volume increases

### Long-Term (This Year)

1. **Full edge deployment** — Zero Railway dependency
2. **Multi-agent revenue model** — Per-client agents as a service
3. **Proprietary data network** — Edge devices across dispensaries (see zeroclaw-monetization.md)

---

## Appendix: ZeroClaw Traits Reference

For future implementation, ZeroClaw's trait-based architecture maps to Roviq's needs:

| Subsystem | ZeroClaw Trait | Roviq Use Case |
|-----------|----------------|----------------|
| AI Models | `Provider` | OpenRouter (anthropic, openai) |
| Channels | `Channel` | Discord (current), add Slack/Telegram |
| Memory | `Memory` | SQLite + vectors for client context |
| Tools | `Tool` | Custom scraper tools |
| Runtime | `RuntimeAdapter` | Native (Pi/edge) |
| Security | `SecurityPolicy` | Workspace scoping, API key encryption |
| Heartbeat | `Engine` | 15-min COO heartbeat |
| Skills | `Loader` | Client-specific skill packs |

---

## Summary

Roviq's current single-agent architecture works for 3-4 clients but will struggle to scale. The recommended path forward:

1. **Keep COO as orchestrator** — It's working, don't fix what's not broken
2. **Add client isolation** — Tag tasks with client context, use separate memory
3. **Decouple scrapers** — Move to ZeroClaw on edge (Pi) for cost and reliability
4. **Stay on Railway for now** — GLASS API needs it; scrapers don't
5. **Plan for multi-agent** — When client count hits 5+, spawn dedicated agents

The ZeroClaw approach (trait-based, edge-first, memory-augmented) aligns perfectly with Roviq's cannabis industry edge-computing strategy outlined in `zeroclaw-monetization.md`.

---

*Prepared by: Subagent (System Architecture Research)*  
*Review status: Ready for COO review → Randy approval*
