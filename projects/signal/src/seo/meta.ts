export interface MetaTagResult {
  title: string;
  description: string;
  ogTitle: string;
  ogDescription: string;
  ogType: string;
  canonical: string;
}

interface MetaInput {
  keyword: string;
  location?: string;
  clientName?: string;
  contentType?: string;
  domain?: string;
  slug?: string;
  differentiator?: string;
}

/**
 * Generate SEO-optimized meta tags.
 *
 * Title: primary keyword + location + brand, under 60 chars.
 * Description: CTA + keyword + differentiator, under 160 chars.
 * Includes Open Graph tags for social sharing.
 */
export function generateMeta(keywordOrInput: string | MetaInput, location?: string): MetaTagResult {
  // Handle both old signature and new object signature
  let input: MetaInput;
  if (typeof keywordOrInput === "string") {
    input = { keyword: keywordOrInput, location };
  } else {
    input = keywordOrInput;
  }

  const { keyword, clientName, contentType, domain, slug, differentiator } = input;
  const loc = input.location;

  // Build title: keyword | location | brand — under 60 chars
  let title: string;
  if (loc && clientName) {
    title = `${keyword} | ${loc} | ${clientName}`;
    if (title.length > 60) {
      title = `${keyword} in ${loc} | ${clientName}`;
    }
    if (title.length > 60) {
      title = `${keyword} | ${clientName}`;
    }
  } else if (loc) {
    title = `${keyword} | ${loc}`;
  } else if (clientName) {
    title = `${keyword} | ${clientName}`;
  } else {
    title = keyword;
  }
  if (title.length > 60) {
    title = `${title.slice(0, 57)}...`;
  }

  // Build description with CTA and differentiator — under 160 chars
  const ctaPrefix = contentType === "product-page"
    ? "Shop"
    : contentType === "blog-post"
      ? "Read about"
      : "Find";

  const diffText = differentiator ?? "real-time pricing and local insights";
  const locText = loc ? ` in ${loc}` : "";
  let description = `${ctaPrefix} ${keyword}${locText}. ${differentiator ? diffText : `Get ${diffText} from ${clientName ?? "local experts"}`}.`;

  if (description.length > 160) {
    description = `${description.slice(0, 157)}...`;
  }

  // OG type based on content type
  const ogTypeMap: Record<string, string> = {
    "blog-post": "article",
    "market-report": "article",
    "product-page": "product",
    "location-page": "business.business",
  };

  // Canonical URL
  const typePathMap: Record<string, string> = {
    "location-page": "locations",
    "product-page": "products",
    "market-report": "market-reports",
    "blog-post": "blog",
  };

  const typePath = typePathMap[contentType ?? ""] ?? "content";
  const canonical = domain && slug
    ? `https://${domain}/${typePath}/${slug}`
    : "";

  return {
    title,
    description,
    ogTitle: title,
    ogDescription: description,
    ogType: ogTypeMap[contentType ?? ""] ?? "website",
    canonical,
  };
}
