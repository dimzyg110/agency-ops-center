export type SupportedSchemaType = "LocalBusiness" | "Product" | "FAQPage" | "Article";

export function generateSchemaMarkup(type: SupportedSchemaType, payload: Record<string, unknown>): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": type,
    ...payload,
  };
}
