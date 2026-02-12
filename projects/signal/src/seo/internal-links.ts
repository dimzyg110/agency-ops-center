import type { ClientConfig } from "../config/schema.js";

export interface InternalLink {
  text: string;
  href: string;
  context: "breadcrumb" | "inline" | "related" | "hub";
}

export interface TopicCluster {
  hubUrl: string;
  hubTitle: string;
  spokePages: InternalLink[];
}

/**
 * Build the full URL path for a content piece.
 */
function buildContentUrl(domain: string, type: string, slug: string): string {
  const base = `https://${domain}`;
  const typePathMap: Record<string, string> = {
    "location-page": "locations",
    "product-page": "products",
    "market-report": "market-reports",
    "blog-post": "blog",
  };
  const typePath = typePathMap[type] ?? "content";
  return `${base}/${typePath}/${slug}`;
}

/**
 * Generate topical hub-and-spoke internal links for a content piece.
 * Implements topical authority clusters:
 *   Location Hub → Individual Location Pages → Product Pages → Blog Posts
 */
export function buildTopicCluster(
  config: ClientConfig,
  contentType: string,
  currentSlug: string
): TopicCluster {
  const domain = config.client.domain;
  const spokePages: InternalLink[] = [];

  // Hub page is always the main locations page for location content
  const hubUrl = contentType === "location-page" || contentType === "product-page"
    ? `https://${domain}/locations`
    : `https://${domain}/blog`;

  const hubTitle = contentType === "location-page" || contentType === "product-page"
    ? `${config.client.name} Locations`
    : `${config.client.name} Blog`;

  // Add nearby location pages (for location pages, link to sibling towns)
  if (contentType === "location-page") {
    for (const town of config.content.locationPages.towns) {
      const townSlug = town.toLowerCase().replace(/\s+/g, "-");
      if (townSlug !== currentSlug) {
        spokePages.push({
          text: `${config.client.name} in ${town}`,
          href: buildContentUrl(domain, "location-page", townSlug),
          context: "related",
        });
      }
    }
    // Cross-link to relevant product pages
    for (const category of config.content.productPages.categories.slice(0, 3)) {
      spokePages.push({
        text: `${category.charAt(0).toUpperCase() + category.slice(1)} guide`,
        href: buildContentUrl(domain, "product-page", category.toLowerCase()),
        context: "inline",
      });
    }
  }

  // Product pages link to location pages and other products
  if (contentType === "product-page") {
    for (const town of config.content.locationPages.towns.slice(0, 3)) {
      spokePages.push({
        text: `Visit our ${town} location`,
        href: buildContentUrl(domain, "location-page", town.toLowerCase().replace(/\s+/g, "-")),
        context: "related",
      });
    }
    for (const category of config.content.productPages.categories) {
      const catSlug = category.toLowerCase().replace(/\s+/g, "-");
      if (catSlug !== currentSlug) {
        spokePages.push({
          text: `Browse ${category}`,
          href: buildContentUrl(domain, "product-page", catSlug),
          context: "related",
        });
      }
    }
  }

  // Blog posts link to location and product pages
  if (contentType === "blog-post" || contentType === "market-report") {
    for (const town of config.content.locationPages.towns.slice(0, 2)) {
      spokePages.push({
        text: `${config.client.name} ${town}`,
        href: buildContentUrl(domain, "location-page", town.toLowerCase().replace(/\s+/g, "-")),
        context: "inline",
      });
    }
    for (const category of config.content.productPages.categories.slice(0, 2)) {
      spokePages.push({
        text: `${category.charAt(0).toUpperCase() + category.slice(1)} products`,
        href: buildContentUrl(domain, "product-page", category.toLowerCase()),
        context: "inline",
      });
    }
  }

  return { hubUrl, hubTitle, spokePages };
}

/**
 * Generate breadcrumb trail for a content piece.
 */
export function buildBreadcrumbs(
  config: ClientConfig,
  contentType: string,
  pageTitle: string
): InternalLink[] {
  const domain = config.client.domain;
  const breadcrumbs: InternalLink[] = [
    { text: "Home", href: `https://${domain}`, context: "breadcrumb" },
  ];

  const typeLabels: Record<string, string> = {
    "location-page": "Locations",
    "product-page": "Products",
    "market-report": "Market Reports",
    "blog-post": "Blog",
  };

  const typeLabel = typeLabels[contentType] ?? "Content";
  const typePath = contentType === "location-page" ? "locations"
    : contentType === "product-page" ? "products"
    : contentType === "market-report" ? "market-reports"
    : "blog";

  breadcrumbs.push({
    text: typeLabel,
    href: `https://${domain}/${typePath}`,
    context: "breadcrumb",
  });

  breadcrumbs.push({
    text: pageTitle,
    href: "#",
    context: "breadcrumb",
  });

  return breadcrumbs;
}

/**
 * Legacy compatibility — suggest links from existing URLs.
 */
export function suggestInternalLinks(keyword: string, existingUrls: string[]): InternalLink[] {
  return existingUrls.slice(0, 5).map((url) => ({
    text: `Related: ${keyword}`,
    href: url,
    context: "related" as const,
  }));
}
