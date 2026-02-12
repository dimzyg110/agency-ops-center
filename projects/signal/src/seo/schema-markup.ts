export type SupportedSchemaType = "LocalBusiness" | "Product" | "FAQPage" | "Article" | "BreadcrumbList";

export interface LocalBusinessSchema {
  name: string;
  description?: string;
  url: string;
  telephone?: string;
  address?: {
    streetAddress: string;
    addressLocality: string;
    addressRegion: string;
    postalCode: string;
    addressCountry: string;
  };
  geo?: {
    latitude: number;
    longitude: number;
  };
  openingHours?: string[];
  priceRange?: string;
  image?: string;
  areaServed?: string;
}

export interface ProductSchema {
  name: string;
  description: string;
  brand?: string;
  sku?: string;
  image?: string;
  price?: number;
  priceCurrency?: string;
  availability?: "InStock" | "OutOfStock" | "PreOrder";
  category?: string;
  aggregateRating?: {
    ratingValue: number;
    reviewCount: number;
  };
}

export interface FAQItem {
  question: string;
  answer: string;
}

export interface ArticleSchema {
  headline: string;
  description?: string;
  author?: string;
  datePublished?: string;
  dateModified?: string;
  publisher?: string;
  publisherLogo?: string;
  image?: string;
  url?: string;
}

export interface BreadcrumbItem {
  name: string;
  url: string;
}

/**
 * Generate complete LocalBusiness JSON-LD schema.
 */
export function generateLocalBusinessSchema(input: LocalBusinessSchema): Record<string, unknown> {
  const schema: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Store",
    "name": input.name,
    "url": input.url,
  };

  if (input.description) {
    schema.description = input.description;
  }

  if (input.telephone) {
    schema.telephone = input.telephone;
  }

  if (input.address) {
    schema.address = {
      "@type": "PostalAddress",
      "streetAddress": input.address.streetAddress,
      "addressLocality": input.address.addressLocality,
      "addressRegion": input.address.addressRegion,
      "postalCode": input.address.postalCode,
      "addressCountry": input.address.addressCountry,
    };
  }

  if (input.geo) {
    schema.geo = {
      "@type": "GeoCoordinates",
      "latitude": input.geo.latitude,
      "longitude": input.geo.longitude,
    };
  }

  if (input.openingHours && input.openingHours.length > 0) {
    schema.openingHours = input.openingHours;
  }

  if (input.priceRange) {
    schema.priceRange = input.priceRange;
  }

  if (input.image) {
    schema.image = input.image;
  }

  if (input.areaServed) {
    schema.areaServed = input.areaServed;
  }

  return schema;
}

/**
 * Generate complete Product JSON-LD schema.
 */
export function generateProductSchema(input: ProductSchema): Record<string, unknown> {
  const schema: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": input.name,
    "description": input.description,
  };

  if (input.brand) {
    schema.brand = {
      "@type": "Brand",
      "name": input.brand,
    };
  }

  if (input.sku) {
    schema.sku = input.sku;
  }

  if (input.image) {
    schema.image = input.image;
  }

  if (input.category) {
    schema.category = input.category;
  }

  if (input.price !== undefined) {
    schema.offers = {
      "@type": "Offer",
      "price": input.price,
      "priceCurrency": input.priceCurrency ?? "USD",
      "availability": `https://schema.org/${input.availability ?? "InStock"}`,
    };
  }

  if (input.aggregateRating) {
    schema.aggregateRating = {
      "@type": "AggregateRating",
      "ratingValue": input.aggregateRating.ratingValue,
      "reviewCount": input.aggregateRating.reviewCount,
    };
  }

  return schema;
}

/**
 * Generate FAQPage JSON-LD schema from Q&A pairs.
 */
export function generateFAQSchema(faqs: FAQItem[]): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map((faq) => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer,
      },
    })),
  };
}

/**
 * Generate Article JSON-LD schema with full metadata.
 */
export function generateArticleSchema(input: ArticleSchema): Record<string, unknown> {
  const schema: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": input.headline,
  };

  if (input.description) {
    schema.description = input.description;
  }

  if (input.author) {
    schema.author = {
      "@type": "Person",
      "name": input.author,
    };
  }

  const now = new Date().toISOString();
  schema.datePublished = input.datePublished ?? now;
  schema.dateModified = input.dateModified ?? now;

  if (input.publisher) {
    const publisherObj: Record<string, unknown> = {
      "@type": "Organization",
      "name": input.publisher,
    };
    if (input.publisherLogo) {
      publisherObj.logo = {
        "@type": "ImageObject",
        "url": input.publisherLogo,
      };
    }
    schema.publisher = publisherObj;
  }

  if (input.image) {
    schema.image = input.image;
  }

  if (input.url) {
    schema.url = input.url;
  }

  return schema;
}

/**
 * Generate BreadcrumbList JSON-LD schema.
 */
export function generateBreadcrumbSchema(items: BreadcrumbItem[]): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": item.url,
    })),
  };
}

/**
 * Legacy compatibility wrapper — still used by some callers.
 */
export function generateSchemaMarkup(type: SupportedSchemaType, payload: Record<string, unknown>): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": type,
    ...payload,
  };
}
