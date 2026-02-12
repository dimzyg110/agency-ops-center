import { GlassClient, type GlassOperator, type GlassPrice, type GlassProduct } from "../glass/client.js";
import type { ClientConfig } from "../config/schema.js";
import { callLLM } from "../llm/openai-client.js";

export interface KeywordBrief {
  primaryKeyword: string;
  secondaryKeywords: string[];
  longTailKeywords: string[];
  searchIntent: "transactional" | "informational" | "navigational" | "local";
  suggestedSections: string[];
  faqQuestions: string[];
  targetWordCount: number;
}

export interface ResearchContext {
  keyword: string;
  operators: GlassOperator[];
  prices: GlassPrice[];
  products: GlassProduct[];
  competitorSummary: string;
  keywordBrief: KeywordBrief;
  autocompleteSuggestions: string[];
}

/**
 * Fetch Google autocomplete suggestions for a query.
 * Falls back to empty array on failure (non-blocking).
 */
async function fetchAutocompleteSuggestions(query: string): Promise<string[]> {
  try {
    const url = `https://suggestqueries.google.com/complete/search?client=firefox&q=${encodeURIComponent(query)}`;
    const response = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; SIGNAL/1.0)" },
    });
    if (!response.ok) return [];

    const data = (await response.json()) as [string, string[]];
    return Array.isArray(data[1]) ? data[1].slice(0, 10) : [];
  } catch {
    return [];
  }
}

/**
 * Use LLM to classify keyword intent and generate a content brief.
 */
async function generateKeywordBrief(
  keyword: string,
  contentType: string,
  autocompleteSuggestions: string[],
  config: ClientConfig,
  cityOrTarget: string
): Promise<KeywordBrief> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    // Fallback brief when no API key
    return buildFallbackBrief(keyword, contentType, cityOrTarget);
  }

  try {
    const systemPrompt = `You are an SEO keyword analyst specializing in cannabis dispensary content. Analyze the given keyword and generate a content brief. Respond in valid JSON only, no markdown.`;

    const userPrompt = `Analyze this keyword for a ${contentType} about ${cityOrTarget}:
Primary keyword: "${keyword}"
Business: ${config.client.name} (cannabis dispensary)
Location: ${cityOrTarget}, Massachusetts
Audience: ${config.audience.primary}
Autocomplete suggestions: ${autocompleteSuggestions.join(", ") || "none available"}
Other tracked keywords: ${config.keywords.primary.join(", ")}

Return JSON with these exact fields:
{
  "primaryKeyword": "the main keyword to target",
  "secondaryKeywords": ["3-5 related keywords"],
  "longTailKeywords": ["3-5 long-tail variations"],
  "searchIntent": "transactional|informational|navigational|local",
  "suggestedSections": ["6-8 H2 section headings for the content"],
  "faqQuestions": ["5-7 FAQ questions users would ask"],
  "targetWordCount": 1500
}`;

    const response = await callLLM({
      role: "research",
      systemPrompt,
      userPrompt,
      temperature: 0.3,
    });

    // Extract JSON from response (handle markdown code blocks)
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (!jsonMatch?.[0]) {
      return buildFallbackBrief(keyword, contentType, cityOrTarget);
    }

    const parsed = JSON.parse(jsonMatch[0]) as Record<string, unknown>;
    return {
      primaryKeyword: typeof parsed.primaryKeyword === "string" ? parsed.primaryKeyword : keyword,
      secondaryKeywords: Array.isArray(parsed.secondaryKeywords) ? (parsed.secondaryKeywords as string[]) : [],
      longTailKeywords: Array.isArray(parsed.longTailKeywords) ? (parsed.longTailKeywords as string[]) : [],
      searchIntent: validateIntent(parsed.searchIntent),
      suggestedSections: Array.isArray(parsed.suggestedSections) ? (parsed.suggestedSections as string[]) : [],
      faqQuestions: Array.isArray(parsed.faqQuestions) ? (parsed.faqQuestions as string[]) : [],
      targetWordCount: typeof parsed.targetWordCount === "number" ? parsed.targetWordCount : 1500,
    };
  } catch {
    return buildFallbackBrief(keyword, contentType, cityOrTarget);
  }
}

function validateIntent(value: unknown): KeywordBrief["searchIntent"] {
  const valid = ["transactional", "informational", "navigational", "local"] as const;
  if (typeof value === "string" && valid.includes(value as KeywordBrief["searchIntent"])) {
    return value as KeywordBrief["searchIntent"];
  }
  return "local";
}

function buildFallbackBrief(keyword: string, contentType: string, city: string): KeywordBrief {
  const wordCountMap: Record<string, number> = {
    "location-page": 1800,
    "product-page": 1000,
    "market-report": 1800,
    "blog-post": 1500,
  };

  return {
    primaryKeyword: keyword,
    secondaryKeywords: [`${city} cannabis`, `${city} dispensary`, `marijuana ${city} MA`],
    longTailKeywords: [
      `best ${keyword}`,
      `${keyword} open now`,
      `${keyword} first time`,
    ],
    searchIntent: contentType === "blog-post" ? "informational" : "local",
    suggestedSections: [
      `About ${city} Cannabis`,
      "What to Expect",
      "Products and Pricing",
      "How to Get Here",
      "Frequently Asked Questions",
      "Local Tips",
    ],
    faqQuestions: [
      `What dispensaries are near ${city}?`,
      `What do I need to buy cannabis in Massachusetts?`,
      `How much do cannabis products cost in ${city}?`,
      `Is recreational cannabis legal in Massachusetts?`,
      `What are the best cannabis products for beginners?`,
    ],
    targetWordCount: wordCountMap[contentType] ?? 1500,
  };
}

export async function runResearch(
  config: ClientConfig,
  cityOrTarget: string,
  contentType: string = "location-page"
): Promise<ResearchContext> {
  const glassApiBaseUrl = process.env.GLASS_API_BASE_URL;
  if (!glassApiBaseUrl) {
    throw new Error("GLASS_API_BASE_URL is required.");
  }

  const client = new GlassClient(glassApiBaseUrl);
  const keyword = config.keywords.primary[0] ?? "cannabis dispensary";

  // Fetch GLASS data — all operators, not just the first one
  const operators = await client.fetchOperators(cityOrTarget);

  let allPrices: GlassPrice[] = [];
  let allProducts: GlassProduct[] = [];

  // Fetch data from ALL operators for comprehensive market view
  const fetchPromises = operators.map(async (op) => {
    try {
      const [prices, products] = await Promise.all([
        client.fetchPrices(op.id),
        client.fetchProducts(op.id),
      ]);
      return { prices, products };
    } catch {
      // Partial failure is okay — continue with other operators
      return { prices: [] as GlassPrice[], products: [] as GlassProduct[] };
    }
  });

  const results = await Promise.all(fetchPromises);
  for (const result of results) {
    allPrices = allPrices.concat(result.prices);
    allProducts = allProducts.concat(result.products);
  }

  // Fetch autocomplete suggestions (non-blocking, fallback to empty)
  const autocompleteSuggestions = await fetchAutocompleteSuggestions(keyword);

  // Generate keyword brief
  const keywordBrief = await generateKeywordBrief(
    keyword,
    contentType,
    autocompleteSuggestions,
    config,
    cityOrTarget
  );

  const competitorSummary =
    operators.length > 0
      ? `${operators.length} dispensaries tracked in ${cityOrTarget}. ${allPrices.length} price data points and ${allProducts.length} products loaded across all operators.`
      : `No operators returned by GLASS for ${cityOrTarget}.`;

  return {
    keyword,
    operators,
    prices: allPrices,
    products: allProducts,
    competitorSummary,
    keywordBrief,
    autocompleteSuggestions,
  };
}
