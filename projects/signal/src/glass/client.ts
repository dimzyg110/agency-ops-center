export interface GlassOperator {
  id: string;
  name: string;
  city: string;
}

export interface GlassPrice {
  operator_id: string;
  category: string;
  avg_price: number;
  currency: string;
}

export interface GlassProduct {
  id: string;
  operator_id: string;
  name: string;
  category: string;
  price: number;
  in_stock: boolean;
}

function buildHeaders(): HeadersInit {
  const apiKey = process.env.GLASS_API_KEY;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (apiKey) {
    headers.Authorization = `Bearer ${apiKey}`;
  }
  return headers;
}

export class GlassClient {
  constructor(private readonly baseUrl: string) {}

  private async getJson<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl.replace(/\/$/, "")}${endpoint}`;
    try {
      const response = await fetch(url, { headers: buildHeaders() });
      if (!response.ok) {
        throw new Error(`GLASS request failed (${response.status}): ${await response.text()}`);
      }
      return (await response.json()) as T;
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown GLASS error";
      throw new Error(`Failed GLASS fetch ${url}: ${reason}`);
    }
  }

  async fetchOperators(city: string): Promise<GlassOperator[]> {
    return this.getJson<GlassOperator[]>(`/operators?city=${encodeURIComponent(city)}`);
  }

  async fetchPrices(operatorId: string): Promise<GlassPrice[]> {
    return this.getJson<GlassPrice[]>(`/prices?operator_id=${encodeURIComponent(operatorId)}`);
  }

  async fetchProducts(operatorId: string): Promise<GlassProduct[]> {
    return this.getJson<GlassProduct[]>(`/products?operator_id=${encodeURIComponent(operatorId)}`);
  }
}
