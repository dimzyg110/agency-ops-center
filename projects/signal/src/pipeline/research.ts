import { GlassClient, type GlassOperator, type GlassPrice, type GlassProduct } from "../glass/client.js";
import type { ClientConfig } from "../config/schema.js";

export interface ResearchContext {
  keyword: string;
  operators: GlassOperator[];
  prices: GlassPrice[];
  products: GlassProduct[];
  competitorSummary: string;
}

export async function runResearch(config: ClientConfig, cityOrTarget: string): Promise<ResearchContext> {
  const glassApiBaseUrl = process.env.GLASS_API_BASE_URL;
  if (!glassApiBaseUrl) {
    throw new Error("GLASS_API_BASE_URL is required.");
  }

  const client = new GlassClient(glassApiBaseUrl);
  const keyword = config.keywords.primary[0] ?? "cannabis dispensary";

  const operators = await client.fetchOperators(cityOrTarget);
  const primaryOperator = operators[0];

  if (!primaryOperator) {
    return {
      keyword,
      operators: [],
      prices: [],
      products: [],
      competitorSummary: `No operators returned by GLASS for ${cityOrTarget}.`,
    };
  }

  const [prices, products] = await Promise.all([
    client.fetchPrices(primaryOperator.id),
    client.fetchProducts(primaryOperator.id),
  ]);

  return {
    keyword,
    operators,
    prices,
    products,
    competitorSummary: `${operators.length} operators discovered. ${prices.length} price entries and ${products.length} products loaded from GLASS.`,
  };
}
