# Claude Opus 4.6 Research

**Status:** Publicly Available
**Research Date:** 2026-02-12

## Official Model Details

- **Model ID:** `claude-opus-4-6`
  - *Note: Unlike previous models, this ID does not currently use a date suffix.*
- **Release Date:** February 5, 2026
- **Provider Availability:** Anthropic API, AWS Bedrock, Google Vertex AI

## Technical Specifications

- **Context Window:** 1,000,000 tokens (1M)
  - *Requirement:* Must use the beta header `anthropic-beta: context-1m-2025-08-07` to access the full 1M window.
  - *Standard Context:* 200,000 tokens (without beta header).
- **Max Output Tokens:** 128,000 tokens

## Pricing (Per Million Tokens)

Pricing is tiered based on context usage.

| Tier | Condition | Input Price | Output Price |
|------|-----------|-------------|--------------|
| **Standard** | Prompts < 200k tokens | $5.00 | $25.00 |
| **Long Context** | Prompts > 200k tokens | $10.00 | $37.50 |

*Note: US-only inference regions may incur a 1.1x multiplier on these rates.*

## Capabilities & Notes

- **Agentic Coding:** Highly optimized for complex, multi-step coding tasks and planning.
- **Computer Use:** Identified as the most accurate model for computer use (controlling screens/GUIs).
- **Thinking:** The explicit `thinking` budget parameter used in Sonnet 3.7/Opus 4.5 is deprecated for Opus 4.6. The model uses "adaptive thinking" automatically.
- **Beta Access:** While the model itself is public, the 1M context window requires the beta header.

## Sources

1. [Anthropic News - Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6)
2. [Claude API Documentation - Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
3. [Digital Applied - Claude Opus 4.6 Features & Pricing](https://www.digitalapplied.com/blog/claude-opus-4-6-release-features-benchmarks-guide)
4. [MarkTechPost - Release Coverage](https://www.marktechpost.com/2026/02/05/anthropic-releases-claude-opus-4-6-with-1m-context-agentic-coding-adaptive-reasoning-controls-and-expanded-safety-tooling-capabilities/)
