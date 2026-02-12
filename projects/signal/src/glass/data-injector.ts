import type { GlassPrice, GlassProduct } from "./client.js";

export interface InjectedMarketContext {
  competitorPriceSummary: string;
  productAvailabilitySummary: string;
  marketPositionSummary: string;
}

export function injectGlassData(prices: GlassPrice[], products: GlassProduct[]): InjectedMarketContext {
  const avgPrice = prices.length
    ? prices.reduce((sum, row) => sum + row.avg_price, 0) / prices.length
    : 0;

  const inStock = products.filter((product) => product.in_stock).length;
  const categories = new Set(products.map((product) => product.category));

  return {
    competitorPriceSummary:
      avgPrice > 0
        ? `Local average across tracked competitors is about $${avgPrice.toFixed(2)}.`
        : "No competitor price data is currently available from GLASS.",
    productAvailabilitySummary: `Tracked inventory shows ${inStock}/${products.length} products currently in stock across ${categories.size} categories.`,
    marketPositionSummary:
      avgPrice > 35
        ? "Current market positioning suggests premium pricing pressure in this area."
        : "Current market positioning suggests value pricing opportunities in this area.",
  };
}
