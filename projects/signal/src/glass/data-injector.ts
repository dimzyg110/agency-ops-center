import type { GlassOperator, GlassPrice, GlassProduct } from "./client.js";

export interface InjectedMarketContext {
  competitorPriceSummary: string;
  productAvailabilitySummary: string;
  marketPositionSummary: string;
  /** Detailed price breakdown by category for templates */
  categoryPriceBreakdown: CategoryPriceData[];
  /** Top products with specific names and prices */
  featuredProducts: FeaturedProduct[];
  /** Competitor comparison data */
  competitorComparisons: CompetitorComparison[];
  /** Raw statistics for template use */
  stats: MarketStats;
  /** Narrative paragraphs for content injection */
  narratives: MarketNarratives;
}

export interface CategoryPriceData {
  category: string;
  avgPrice: number;
  minPrice: number;
  maxPrice: number;
  productCount: number;
}

export interface FeaturedProduct {
  name: string;
  category: string;
  price: number;
  inStock: boolean;
}

export interface CompetitorComparison {
  operatorName: string;
  avgPrice: number;
  productCount: number;
  categoryStrength: string;
}

export interface MarketStats {
  totalOperators: number;
  totalProducts: number;
  inStockCount: number;
  outOfStockCount: number;
  categoryCount: number;
  overallAvgPrice: number;
  lowestPrice: number;
  highestPrice: number;
}

export interface MarketNarratives {
  pricingNarrative: string;
  inventoryNarrative: string;
  competitiveNarrative: string;
  valueProposition: string;
}

function computeCategoryBreakdown(products: GlassProduct[]): CategoryPriceData[] {
  const categoryMap = new Map<string, { prices: number[]; count: number }>();

  for (const product of products) {
    const existing = categoryMap.get(product.category);
    if (existing) {
      existing.prices.push(product.price);
      existing.count++;
    } else {
      categoryMap.set(product.category, { prices: [product.price], count: 1 });
    }
  }

  const result: CategoryPriceData[] = [];
  for (const [category, data] of categoryMap) {
    const avg = data.prices.reduce((sum, p) => sum + p, 0) / data.prices.length;
    result.push({
      category,
      avgPrice: Math.round(avg * 100) / 100,
      minPrice: Math.min(...data.prices),
      maxPrice: Math.max(...data.prices),
      productCount: data.count,
    });
  }

  return result.sort((a, b) => b.productCount - a.productCount);
}

function selectFeaturedProducts(products: GlassProduct[], limit: number = 8): FeaturedProduct[] {
  const inStock = products
    .filter((p) => p.in_stock)
    .sort((a, b) => a.price - b.price);

  // Pick a mix: cheapest in each category, then fill with popular items
  const seen = new Set<string>();
  const featured: FeaturedProduct[] = [];

  // One from each category first
  for (const product of inStock) {
    if (!seen.has(product.category) && featured.length < limit) {
      featured.push({
        name: product.name,
        category: product.category,
        price: product.price,
        inStock: product.in_stock,
      });
      seen.add(product.category);
    }
  }

  // Fill remaining slots
  for (const product of inStock) {
    if (featured.length >= limit) break;
    if (!featured.some((f) => f.name === product.name)) {
      featured.push({
        name: product.name,
        category: product.category,
        price: product.price,
        inStock: product.in_stock,
      });
    }
  }

  return featured;
}

function buildCompetitorComparisons(
  operators: GlassOperator[],
  prices: GlassPrice[],
  products: GlassProduct[]
): CompetitorComparison[] {
  return operators.slice(0, 5).map((op) => {
    const opPrices = prices.filter((p) => p.operator_id === op.id);
    const opProducts = products.filter((p) => p.operator_id === op.id);
    const avgPrice = opPrices.length
      ? opPrices.reduce((sum, p) => sum + p.avg_price, 0) / opPrices.length
      : 0;

    // Find strongest category by product count
    const catCounts = new Map<string, number>();
    for (const product of opProducts) {
      catCounts.set(product.category, (catCounts.get(product.category) ?? 0) + 1);
    }
    let topCat = "general";
    let topCount = 0;
    for (const [cat, count] of catCounts) {
      if (count > topCount) {
        topCat = cat;
        topCount = count;
      }
    }

    return {
      operatorName: op.name,
      avgPrice: Math.round(avgPrice * 100) / 100,
      productCount: opProducts.length,
      categoryStrength: topCat,
    };
  });
}

function buildNarratives(
  operators: GlassOperator[],
  stats: MarketStats,
  categoryBreakdown: CategoryPriceData[],
  city: string
): MarketNarratives {
  const priceParts: string[] = [];
  if (categoryBreakdown.length > 0) {
    const topCat = categoryBreakdown[0];
    if (topCat) {
      priceParts.push(
        `${topCat.category.charAt(0).toUpperCase() + topCat.category.slice(1)} averages $${topCat.avgPrice.toFixed(2)} across ${city}-area dispensaries, with prices ranging from $${topCat.minPrice.toFixed(2)} to $${topCat.maxPrice.toFixed(2)}.`
      );
    }
    if (categoryBreakdown.length > 1) {
      const secondCat = categoryBreakdown[1];
      if (secondCat) {
        priceParts.push(
          `${secondCat.category.charAt(0).toUpperCase() + secondCat.category.slice(1)} products average $${secondCat.avgPrice.toFixed(2)}, with ${secondCat.productCount} options currently tracked.`
        );
      }
    }
  }
  const pricingNarrative = priceParts.length > 0
    ? priceParts.join(" ")
    : `Price data is still being collected for the ${city} market.`;

  const inventoryNarrative =
    stats.totalProducts > 0
      ? `Across ${stats.totalOperators} tracked dispensaries in ${city}, there are ${stats.inStockCount} products currently in stock out of ${stats.totalProducts} total items tracked across ${stats.categoryCount} categories. That means about ${Math.round((stats.inStockCount / stats.totalProducts) * 100)}% availability — ${stats.inStockCount / stats.totalProducts > 0.8 ? "strong inventory levels" : "some items may sell out quickly"}.`
      : `Inventory tracking for ${city} dispensaries is underway.`;

  const competitiveNarrative =
    operators.length > 1
      ? `The ${city} cannabis market includes ${operators.length} active dispensaries. Competition keeps pricing competitive — the area average of $${stats.overallAvgPrice.toFixed(2)} per item is ${stats.overallAvgPrice < 40 ? "below" : "near"} the statewide Massachusetts average.`
      : `${city} currently has limited dispensary options, which may affect local pricing.`;

  const valueProposition =
    stats.overallAvgPrice > 0
      ? stats.overallAvgPrice < 38
        ? `With an area average below $38, ${city} is one of the more affordable cannabis markets in the Greater Boston area.`
        : stats.overallAvgPrice < 45
          ? `${city} dispensary pricing sits in the mid-range for Greater Boston, with good variety across product categories.`
          : `Premium pricing in ${city} reflects high demand and quality inventory from local dispensaries.`
      : `Market pricing data for ${city} is being compiled.`;

  return { pricingNarrative, inventoryNarrative, competitiveNarrative, valueProposition };
}

export function injectGlassData(
  prices: GlassPrice[],
  products: GlassProduct[],
  operators: GlassOperator[] = [],
  city: string = "the area"
): InjectedMarketContext {
  const avgPrice = prices.length
    ? prices.reduce((sum, row) => sum + row.avg_price, 0) / prices.length
    : 0;

  const inStock = products.filter((product) => product.in_stock).length;
  const categories = new Set(products.map((product) => product.category));
  const allPrices = products.map((p) => p.price).filter((p) => p > 0);

  const stats: MarketStats = {
    totalOperators: operators.length,
    totalProducts: products.length,
    inStockCount: inStock,
    outOfStockCount: products.length - inStock,
    categoryCount: categories.size,
    overallAvgPrice: avgPrice > 0 ? Math.round(avgPrice * 100) / 100 : 0,
    lowestPrice: allPrices.length > 0 ? Math.min(...allPrices) : 0,
    highestPrice: allPrices.length > 0 ? Math.max(...allPrices) : 0,
  };

  const categoryBreakdown = computeCategoryBreakdown(products);
  const featuredProducts = selectFeaturedProducts(products);
  const competitorComparisons = buildCompetitorComparisons(operators, prices, products);
  const narratives = buildNarratives(operators, stats, categoryBreakdown, city);

  return {
    competitorPriceSummary:
      avgPrice > 0
        ? `The local average across ${operators.length > 0 ? operators.length : "tracked"} competitors in ${city} is $${avgPrice.toFixed(2)}.`
        : "Competitor price data is not yet available from GLASS.",
    productAvailabilitySummary: `${inStock} of ${products.length} tracked products are currently in stock across ${categories.size} categories.`,
    marketPositionSummary:
      avgPrice > 35
        ? `The ${city} market shows premium pricing pressure, with averages above $35 per item.`
        : `The ${city} market currently offers value pricing opportunities, with averages at or below $35.`,
    categoryPriceBreakdown: categoryBreakdown,
    featuredProducts,
    competitorComparisons,
    stats,
    narratives,
  };
}
