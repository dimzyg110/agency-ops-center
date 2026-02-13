import { humanizeContent } from "../llm/openai-client.js";

/**
 * Content humanizer with AI pattern detection and removal.
 *
 * Pipeline:
 * 1. Score AI patterns (pre)
 * 2. Apply rule-based humanization (PRIMARY — all 24+ patterns)
 * 3. Optional LLM enhancement pass (if API key available)
 * 4. Score AI patterns (post)
 */

// ============================================================================
// AI PATTERN DEFINITIONS (24 patterns from humanizer skill)
// ============================================================================

export interface AiPattern {
  name: string;
  category: string;
  description: string;
  detect: RegExp;
  fix: string | ((match: string) => string);
  weight: number;
}

export interface AiScoreResult {
  score: number;
  patterns: string[];
  details: Array<{
    pattern: string;
    category: string;
    matches: number;
    weight: number;
  }>;
}

// All 24 AI patterns from the humanizer skill
const AI_PATTERNS: AiPattern[] = [
  // CONTENT PATTERNS (1-6)
  {
    name: "inflated_significance",
    category: "content",
    description: "Stands/serves as, testament/reminder, vital/crucial/pivotal, underscores",
    detect: /\b(?:stands?|serves?) as\b|\b(?:a )?testament\s+to\b|\b(?:a )?reminder of\b|\b(?:vital|significant|crucial|pivotal|key)\s+(?:role|moment)\b|\bunderscores?\b|\bhighlights?\s+(?:its )?(?:importance|significance)\b|\breflects?\s+(?:broader|the\s+(?:broader|evolving))\b|\bsymboliz(?:ing|es?)\s+(?:its|the)?\s*(?:ongoing|enduring|lasting)\b|\bcontributing\s+to\s+the\b|\bsetting\s+the\s+stage\s+for\b|\bmark(?:ing|s?)\s+(?:a\s+)?(?:shift|turning\s+point)|\bshaping\s+the\b|\brepresents?\s+(?:a\s+)?shift\b|\bkey\s+turning\s+point\b|\bevolving\s+landscape\b|\bfocal\s+point\b|\bindelible\s+mark\b|\bdeeply\s+rooted\b/gi,
    fix: "",
    weight: 8,
  },
  {
    name: "notability_emphasis",
    category: "content",
    description: "Claims of notability without specifics",
    detect: /\bindependent\s+coverage\b|\b(?:local|regional|national|major)\s+media\s+outlets?\b|\bwritten\s+by\s+(?:a\s+)?leading\s+expert\b|\bactive\s+social\s+media\s+presence\b|\bover\s+\d+[KM]?\s+(?:followers|subscribers)\b/gi,
    fix: "",
    weight: 6,
  },
  {
    name: "superficial_ing",
    category: "content",
    description: "Present participle phrases adding fake depth",
    detect: /,\s*(?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|contributing\s+to|cultivating|fostering|encompassing|showcasing)[^.]+(?=\.|,)/gi,
    fix: "",
    weight: 9,
  },
  {
    name: "promotional_language",
    category: "content",
    description: "Advertisement-like adjectives",
    detect: /\bboasts\s+(?:a|an)\b|\bvibrant\b|\brich\s+(?:cultural\s+)?(?:heritage|history)\b|\bprofound\b|\benhancing\s+its\b|\bshowcasing\b|\bexemplifies\b|\bcommitment\s+to\b|\bnatural\s+beauty\b|\bnestled\s+(?:within|in)\b|\bin\s+the\s+heart\s+of\b|\bgroundbreaking\b|\brenowned\b|\bbreathtaking\b|\bmust-visit\b|\bstunning\b/gi,
    fix: (match: string) => match.replace(/\bboasts\s+a\b/gi, "has").replace(/\bnestled\s+in\b/gi, "in").replace(/\bin\s+the\s+heart\s+of\b/gi, "in"),
    weight: 7,
  },
  {
    name: "vague_attributions",
    category: "content",
    description: "Weasel words attributing opinions to vague authorities",
    detect: /\bindustry\s+reports\s+(?:suggest|indicate|claim)\b|\bobservers?\s+have\s+(?:cited|noted)\b|\bexperts?\s+(?:argue|believe|suggest|claim)\b|\bsome\s+critics?\s+(?:argue|suggest)\b|\bseveral\s+(?:sources|publications)(?:\s+have)?\b/gi,
    fix: "",
    weight: 7,
  },
  {
    name: "challenges_future_prospects",
    category: "content",
    description: "Formulaic Challenges sections",
    detect: /\bDespite\s+(?:its|the|these)\s+[^.]+(?:faces?|presents?)\s+(?:several\s+)?challenges\b|\bDespite\s+these\s+challenges\b|\bChallenges?\s+and\s+(?:Legacy|Future)\b|\bFuture\s+Outlook\b/gi,
    fix: "",
    weight: 5,
  },
  // LANGUAGE/GRAMMAR PATTERNS (7-12)
  {
    name: "ai_vocabulary",
    category: "language",
    description: "High-frequency AI words",
    detect: /\bAdditionally\b|\balign\s+with\b|\bcrucial\b|\bdelve\b|\bemphasiz(?:ing|e)\b|\bendur(?:ing|es?)\b|\benhance\b|\bfoster(?:ing)?\b|\bgarner\b|\bhighlight(?:ing)?\s+(?:as|the)\b|\binterplay\b|\bintricate\b|\bintricacies\b|\bkey\s+(?:role|player|factor)\b|\blandscape\s+(?:of|in)\b|\bpivotal\b|\bshowcase\b|\btapestry\s+(?:of|in)\b|\btestament\b|\bunderscore(?:ing)?\b|\bvaluable\b|\bvibrant\b/gi,
    fix: (match: string) => {
      const replacements: Record<string, string> = {
        additionally: "",
        crucial: "key",
        delve: "explore",
        emphasizing: "",
        enduring: "lasting",
        foster: "build",
        fostering: "building",
        garner: "get",
        highlight: "show",
        interplay: "connection",
        intricate: "complex",
        intricacies: "details",
        pivotal: "key",
        showcase: "show",
        tapestry: "mix",
        underscore: "show",
        underscores: "shows",
        valuable: "useful",
        vibrant: "active",
      };
      const lower = match.toLowerCase().trim();
      return replacements[lower] !== undefined ? replacements[lower] : match;
    },
    weight: 10,
  },
  {
    name: "copula_avoidance",
    category: "language",
    description: "Serves/stands as instead of simple is",
    detect: /\b(?:serves?|stands?)\s+as\s+(?:a|an)?\b/gi,
    fix: "is",
    weight: 6,
  },
  {
    name: "negative_parallelisms",
    category: "language",
    description: "Not only...but..., It's not just about...",
    detect: /\bIt's\s+not\s+(?:just|merely)\s+about[^,]+,?\s*(?:it'?s|it is)\b|\bNot\s+only[^,]+,?\s*but\s+(?:also\s+)?/gi,
    fix: "",
    weight: 8,
  },
  {
    name: "rule_of_three",
    category: "language",
    description: "Forced groupings of three",
    detect: /\b\w+,\s+\w+,\s+and\s+\w+\b/g,
    fix: (match: string) => {
      // Keep first and last items, drop the middle: "A, B, and C" -> "A and C"
      const parts = match.split(/,\s+|\s+and\s+/).filter((p): p is string => !!p);
      if (parts.length >= 3) {
        const first = parts[0]!;
        const last = parts[parts.length - 1]!;
        return `${first.trim()} and ${last.trim()}`;
      }
      return match;
    },
    weight: 5,
  },
  {
    name: "elegant_variation",
    category: "language",
    description: "Excessive synonym cycling",
    detect: /\b(?:protagonist|main character|central figure|hero)\b.*\b(?:protagonist|main character|central figure|hero)\b/gi,
    fix: "",
    weight: 4,
  },
  {
    name: "false_ranges",
    category: "language",
    description: "From X to Y where X and Y are not on a meaningful scale",
    detect: /\bfrom\s+\w+\s+to\s+\w+\s+to\s+\w+\b|\bfrom\s+(?:the\s+)?(?:singularity|Big Bang)\s+to\s+(?:the\s+)?(?:grand\s+cosmic\s+web|present)\b/gi,
    fix: "",
    weight: 5,
  },
  // STYLE PATTERNS (13-18)
  {
    name: "em_dash_overuse",
    category: "style",
    description: "Excessive em dashes",
    detect: /—[^—]+—/g,
    fix: (match: string) => match.replace(/—/g, ", "),
    weight: 6,
  },
  {
    name: "boldface_overuse",
    category: "style",
    description: "Mechanical use of boldface",
    detect: /\*\*[^*]+\*\*/g,
    fix: (match: string) => match.replace(/\*\*/g, ""),
    weight: 4,
  },
  {
    name: "inline_header_lists",
    category: "style",
    description: "Bold headers with colons in lists",
    detect: /\*\*[^:]+:\*\*/g,
    fix: (match: string) => match.replace(/\*\*([^:]+):\*\*/g, "$1"),
    weight: 5,
  },
  {
    name: "title_case_headings",
    category: "style",
    description: "Capitalizing all main words in headings",
    detect: /^##?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$/gm,
    fix: (match: string) => match.replace(/\s+[A-Z]/g, (m) => m.toLowerCase()),
    weight: 3,
  },
  {
    name: "emoji_use",
    category: "style",
    description: "Emojis in headings or bullet points",
    detect: /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu,
    fix: "",
    weight: 4,
  },
  {
    name: "curly_quotes",
    category: "style",
    description: "Using curly quotes instead of straight quotes",
    detect: /[\u201C\u201D\u2018\u2019`]/gu,
    fix: (match: string) => {
      const map: Record<string, string> = { 
        "\u201C": '"',  // left double quote
        "\u201D": '"',  // right double quote
        "\u2018": "'",  // left single quote
        "\u2019": "'",  // right single quote
        "`": "'" 
      };
      return map[match] || match;
    },
    weight: 2,
  },
  // COMMUNICATION PATTERNS (19-21)
  {
    name: "collaborative_artifacts",
    category: "communication",
    description: "Chatbot correspondence pasted as content",
    detect: /\bI\s+hope\s+this\s+helps\b|\bOf\s+course!\b|\bCertainly!\b|\bYou're\s+absolutely\s+right!\b|\bWould\s+you\s+like\b|\blet\s+me\s+know\b|\bhere\s+is\s+(?:a|an)\b/gi,
    fix: "",
    weight: 9,
  },
  {
    name: "knowledge_cutoff",
    category: "communication",
    description: "AI disclaimers about incomplete information",
    detect: /\bas\s+of\s+\w+\s+\d{4}\b|\bup\s+to\s+(?:my|the)\s+last\s+(?:training|knowledge)\s+update\b|\bWhile\s+specific\s+details\s+are\s+(?:limited|scarce)\b|\bbased\s+on\s+available\s+information\b/gi,
    fix: "",
    weight: 8,
  },
  {
    name: "sycophantic_tone",
    category: "communication",
    description: "Overly positive, people-pleasing language",
    detect: /\bGreat\s+question!\b|\bYou're\s+absolutely\s+right\b|\bThat's\s+(?:an\s+)?excellent\s+point\b|\bI\s+love\s+(?:that|this|your)\b/gi,
    fix: "",
    weight: 8,
  },
  // FILLER/HEDGING PATTERNS (22-24)
  {
    name: "filler_phrases",
    category: "filler",
    description: "Wordy constructions that can be simplified",
    detect: /\bin\s+order\s+to\s+achieve\b|\bdue\s+to\s+the\s+fact\s+that\b|\bat\s+this\s+point\s+in\s+time\b|\bin\s+the\s+event\s+that\b|\bthe\s+\w+\s+has\s+the\s+ability\s+to\b|\bIt\s+is\s+important\s+to\s+note\s+that\b/gi,
    fix: (match: string) => {
      const fillers: Record<string, string> = {
        "in order to achieve": "To achieve",
        "due to the fact that": "Because",
        "at this point in time": "Now",
        "in the event that": "If",
        "it is important to note that": "",
      };
      const lower = match.toLowerCase();
      for (const [filler, replacement] of Object.entries(fillers)) {
        if (lower.includes(filler)) return replacement;
      }
      return match;
    },
    weight: 7,
  },
  {
    name: "excessive_hedging",
    category: "filler",
    description: "Over-qualifying statements",
    detect: /\bcould\s+potentially\s+possibly\b|\bmight\s+arguably\s+be\s+said\s+to\b|\bthere\s+is\s+a\s+possibility\s+that\b/gi,
    fix: "",
    weight: 6,
  },
  {
    name: "generic_conclusions",
    category: "filler",
    description: "Vague upbeat endings",
    detect: /\bThe\s+future\s+looks\s+bright\b|\bExciting\s+times\s+lie\s+ahead\b|\b(?:major|significant)\s+step\s+in\s+the\s+right\s+direction\b|\bcontinues?\s+to\s+thrive\b/gi,
    fix: "",
    weight: 6,
  },
];

// Placeholder tokens for protected content
interface ProtectedBlocks {
  jsonLdBlocks: string[];
  codeFences: string[];
}

/**
 * Extract JSON-LD blocks and code fences as placeholders before processing.
 * This prevents regex patterns from mangling structured data.
 */
function extractProtectedBlocks(content: string): { text: string; blocks: ProtectedBlocks } {
  const jsonLdBlocks: string[] = [];
  const codeFences: string[] = [];
  
  let text = content;
  
  // Extract JSON-LD blocks first (highest priority)
  const jsonLdRegex = /<script[^>]*type="application\/ld\+json"[^>]*>[\s\S]*?<\/script>/gi;
  text = text.replace(jsonLdRegex, (match) => {
    const token = `__JSONLD_${jsonLdBlocks.length}__`;
    jsonLdBlocks.push(match);
    return token;
  });
  
  // Extract code fences (```...```)
  const codeFenceRegex = /```[\s\S]*?```/g;
  text = text.replace(codeFenceRegex, (match) => {
    const token = `__CODEFENCE_${codeFences.length}__`;
    codeFences.push(match);
    return token;
  });
  
  // Extract inline code blocks (`...`)
  const inlineCodeRegex = /`[^`]+`/g;
  text = text.replace(inlineCodeRegex, (match) => {
    const token = `__CODEFENCE_${codeFences.length}__`;
    codeFences.push(match);
    return token;
  });
  
  return { text, blocks: { jsonLdBlocks, codeFences } };
}

/**
 * Restore protected blocks from placeholders after processing.
 */
function restoreProtectedBlocks(text: string, blocks: ProtectedBlocks): string {
  let result = text;
  
  // Restore JSON-LD blocks
  blocks.jsonLdBlocks.forEach((block, i) => {
    result = result.replace(`__JSONLD_${i}__`, block);
  });
  
  // Restore code fences
  blocks.codeFences.forEach((block, i) => {
    result = result.replace(`__CODEFENCE_${i}__`, block);
  });
  
  return result;
}

// Simple regex replacements for mechanical fixes
const SIMPLE_REPLACEMENTS: Array<[RegExp, string]> = [
  [/\bAdditionally,\s+/g, ""],
  [/\bMoreover,\s+/g, ""],
  [/\bFurthermore,\s+/g, ""],
  [/\bIt is(?:\s+also)?\s+worth\s+noting\s+that\s+/g, ""],
  [/\bIn this\s+regard,?\s*/g, ""],
  [/\bcould\s+potentially\b/g, "may"],
  [/\bmight\s+possibly\b/g, "may"],
  [/\bit\s+could\s+be\s+argued\s+that\b/g, ""],
  [/\bgroundbreaking\b/gi, "new"],
  [/\brevolutionary\b/gi, "new"],
  [/\bcutting-edge\b/gi, "current"],
  [/\bstate-of-the-art\b/gi, "current"],
  [/\/\/\s*Generated by SIGNAL[^\n]*/g, ""],
  [/Generated by SIGNAL[^"]*/g, ""],
];

// ============================================================================
// AI PATTERN SCORING
// ============================================================================

/**
 * Score content for AI patterns (0-100 scale).
 * 0 = no AI patterns detected, 100 = heavily AI-generated
 */
export function scoreAiPatterns(content: string): AiScoreResult {
  const detected: Array<{
    pattern: string;
    category: string;
    matches: number;
    weight: number;
  }> = [];

  let totalWeightedMatches = 0;
  let totalPossibleWeight = 0;

  for (const pattern of AI_PATTERNS) {
    const globalRegex = new RegExp(pattern.detect.source, "gi");
    const allMatches = content.match(globalRegex);
    const matches = allMatches?.length || 0;

    if (matches > 0) {
      detected.push({
        pattern: pattern.name,
        category: pattern.category,
        matches,
        weight: pattern.weight,
      });
      totalWeightedMatches += matches * pattern.weight;
    }

    totalPossibleWeight += pattern.weight * 3;
  }

  const rawScore = (totalWeightedMatches / totalPossibleWeight) * 100;
  const score = Math.min(100, Math.round(rawScore * 100) / 100);

  return {
    score,
    patterns: detected.map((d) => d.pattern),
    details: detected,
  };
}

// ============================================================================
// RULE-BASED HUMANIZER (PRIMARY PATH)
// ============================================================================

interface ContentSegment {
  type: "text" | "tag";
  content: string;
}

function segmentContent(content: string): ContentSegment[] {
  const segments: ContentSegment[] = [];
  let current = 0;
  // Include React fragments <> and </> in tag regex
  const tagRegex = /(<\w[^>]*>|<\/[^>]+>|<\s*>|<\/\s*>)/gi;

  let match: RegExpExecArray | null;
  while ((match = tagRegex.exec(content)) !== null) {
    if (match.index > current) {
      segments.push({
        type: "text",
        content: content.slice(current, match.index),
      });
    }
    segments.push({
      type: "tag",
      content: match[0],
    });
    current = match.index + match[0].length;
  }

  if (current < content.length) {
    segments.push({
      type: "text",
      content: content.slice(current),
    });
  }

  return segments;
}

function applyMechanicalFixes(text: string): string {
  let result = text;

  for (const [pattern, replacement] of SIMPLE_REPLACEMENTS) {
    result = result.replace(pattern, replacement);
  }

  for (const pattern of AI_PATTERNS) {
    if (typeof pattern.fix === "string" && pattern.fix === "") continue;
    
    const fixRegex = new RegExp(pattern.detect.source, "gi");
    if (typeof pattern.fix === "string") {
      result = result.replace(fixRegex, pattern.fix);
    } else {
      result = result.replace(fixRegex, pattern.fix);
    }
  }

  return result;
}

/**
 * Normalize whitespace globally after all processing.
 * Collapses multiple spaces to one, fixes punctuation spacing.
 */
function normalizeWhitespace(text: string): string {
  let result = text;
  
  // Collapse multiple spaces to single space
  result = result.replace(/\s{2,}/g, " ");
  // Fix double commas
  result = result.replace(/,\s*,/g, ",");
  // Fix multiple periods
  result = result.replace(/\.{2,}/g, ".");
  // Remove space before punctuation
  result = result.replace(/\s+([.,;:!?])/g, "$1");
  
  return result;
}

function ruleBasedHumanize(content: string): string {
  // Extract protected blocks (JSON-LD, code fences) before any processing
  const { text: protectedText, blocks } = extractProtectedBlocks(content);
  
  // Segment content into text and HTML/React tags
  const segments = segmentContent(protectedText);
  
  // Process each segment - don't trim individual segments
  const processed = segments.map((seg) => {
    if (seg.type === "tag") return seg.content;
    return applyMechanicalFixes(seg.content);
  });
  
  // Join and normalize whitespace globally
  let result = processed.join("");
  result = normalizeWhitespace(result);
  
  // Restore protected blocks
  result = restoreProtectedBlocks(result, blocks);

  return result;
}

// ============================================================================
// LLM ENHANCEMENT (SECONDARY)
// ============================================================================

const HUMANIZER_SYSTEM_PROMPT = `You are a professional editor specializing in making AI-generated content sound natural and human-written.

Your job: rewrite the provided content to remove ALL signs of AI generation while keeping the meaning, structure, and SEO elements intact.

CRITICAL RULES:
1. PRESERVE all HTML/JSX tags exactly as they are.
2. PRESERVE all JSON-LD schema blocks exactly.
3. PRESERVE all JavaScript/TypeScript code.
4. ONLY rewrite the human-readable text content BETWEEN the HTML tags.
5. Remove any "Generated by SIGNAL" or similar watermark comments.

AI PATTERNS TO FIX:
- Remove "Additionally", "Moreover", "Furthermore"
- Replace AI vocabulary: "crucial", "pivotal", "vibrant", "tapestry", "landscape", "delve", "foster", "garner", "underscore", "showcase", "testament"
- Break up Rule of Three patterns
- Remove em dash overuse
- Kill "It's not just X, it's Y" constructions
- Remove "-ing" superficial analysis phrases
- Replace "serves as" / "stands as" with "is"
- Remove sycophantic language ("Great question!", "Certainly!")
- Use simple "is/are/has" instead of elaborate constructions
- Remove hedging and generic positive conclusions
- Use straight quotes, not curly quotes

VOICE GUIDELINES:
- Sound like a knowledgeable local, not a corporate brochure
- Vary sentence length: short punchy ones mixed with longer ones
- Be direct and specific
- Use first-person plural ("we", "our") when referring to the business
- Reference specific details rather than vague claims

Return ONLY the rewritten content. No explanations, no commentary.`;

async function llmEnhancementPass(content: string, brandVoice?: string): Promise<string> {
  const voiceAddendum = brandVoice
    ? `\n\nBRAND VOICE: ${brandVoice}. Adapt the tone while keeping it natural.`
    : "";

  try {
    const result = await humanizeContent(HUMANIZER_SYSTEM_PROMPT + voiceAddendum, content);

    if (!result.includes("<article") && content.includes("<article")) {
      console.warn("[Humanizer] LLM stripped JSX structure — keeping rule-based output.");
      return content;
    }

    return result;
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown error";
    console.warn(`[Humanizer] LLM enhancement failed (${reason}) — keeping rule-based output.`);
    return content;
  }
}

// ============================================================================
// MAIN EXPORTS
// ============================================================================

/**
 * Run the humanizer pipeline.
 * Primary path: Rule-based humanization (always runs).
 * Enhancement: LLM pass if API key available (runs AFTER rule-based).
 */
export async function runHumanize(
  content: string,
  brandVoice?: string,
  options?: { skipLlm?: boolean }
): Promise<string> {
  console.log("[Humanizer] Applying rule-based fixes (24+ patterns)...");
  const ruleBasedResult = ruleBasedHumanize(content);

  const hasNvidiaKey = !!process.env.NVIDIA_API_KEY;
  const hasOpenaiKey = !!process.env.OPENAI_API_KEY;
  const hasOpenrouterKey = !!process.env.OPENROUTER_API_KEY;
  const hasLlmKey = hasNvidiaKey || hasOpenaiKey || hasOpenrouterKey;

  if (!hasLlmKey || options?.skipLlm) {
    if (!hasLlmKey) {
      console.log("[Humanizer] No LLM API key — rule-based output complete.");
    } else {
      console.log("[Humanizer] Skipping LLM pass (--skip-llm).");
    }
    return ruleBasedResult;
  }

  console.log(`[Humanizer] Running LLM enhancement (${hasOpenaiKey ? "OpenAI" : hasNvidiaKey ? "NVIDIA" : "OpenRouter"})...`);
  const enhancedResult = await llmEnhancementPass(ruleBasedResult, brandVoice);

  return enhancedResult;
}

/**
 * Run humanization with before/after scoring for pipeline logging.
 */
export async function runHumanizeWithScoring(
  content: string,
  brandVoice?: string
): Promise<{
  content: string;
  beforeScore: AiScoreResult;
  afterScore: AiScoreResult;
}> {
  const beforeScore = scoreAiPatterns(content);
  console.log(`[Humanizer] Pre-humanization AI score: ${beforeScore.score}/100 (${beforeScore.patterns.length} patterns detected)`);

  const humanized = await runHumanize(content, brandVoice);

  const afterScore = scoreAiPatterns(humanized);
  console.log(`[Humanizer] Post-humanization AI score: ${afterScore.score}/100 (${afterScore.patterns.length} patterns detected)`);

  const improvement = beforeScore.score - afterScore.score;
  if (improvement > 0) {
    console.log(`[Humanizer] Score improved by ${improvement.toFixed(1)} points`);
  }

  return {
    content: humanized,
    beforeScore,
    afterScore,
  };
}
