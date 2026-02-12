import type { FeaturedProduct } from "../glass/data-injector.js";
import type { InternalLink } from "../seo/internal-links.js";
import type { MetaTagResult } from "../seo/meta.js";
import type { FAQItem } from "../seo/schema-markup.js";

export interface ProductPageInput {
  category: string;
  clientName: string;
  /** LLM-generated body sections (HTML string) */
  generatedBody: string;
  schemaMarkup: Record<string, unknown>;
  faqSchema: Record<string, unknown>;
  breadcrumbSchema: Record<string, unknown>;
  products: FeaturedProduct[];
  faqs: FAQItem[];
  internalLinks: InternalLink[];
  breadcrumbs: InternalLink[];
  meta: MetaTagResult;
  avgPrice: number;
  priceRange: string;
}

function escapeJsx(str: string): string {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function renderProductGrid(products: FeaturedProduct[]): string {
  if (products.length === 0) return "";

  const cards = products
    .map(
      (p) =>
        `          <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold mb-1">${p.name}</h3>
            <p className="text-sm text-gray-500 capitalize mb-2">${p.category}</p>
            <p className="text-lg font-bold text-green-700">${p.inStock ? `$${p.price.toFixed(2)}` : "Out of stock"}</p>
            ${p.inStock ? '<span className="text-xs text-green-600">In Stock</span>' : '<span className="text-xs text-red-500">Currently unavailable</span>'}
          </div>`
    )
    .join("\n");

  return `
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 my-6">
${cards}
        </div>`;
}

function renderFAQSection(faqs: FAQItem[]): string {
  if (faqs.length === 0) return "";

  const items = faqs
    .map(
      (faq) =>
        `          <div className="border-b border-gray-200 pb-6">
            <h3 className="text-lg font-semibold mb-2">${faq.question}</h3>
            <p className="text-gray-700 leading-relaxed">${faq.answer}</p>
          </div>`
    )
    .join("\n");

  return `
        <section className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions About ${faqs.length > 0 ? "This Category" : "Products"}</h2>
          <div className="space-y-6">
${items}
          </div>
        </section>`;
}

function renderBreadcrumbs(breadcrumbs: InternalLink[]): string {
  const items = breadcrumbs
    .map(
      (b, i) =>
        i < breadcrumbs.length - 1
          ? `<a href="${b.href}" className="text-green-700 hover:underline">${b.text}</a>`
          : `<span className="text-gray-500">${b.text}</span>`
    )
    .join(' <span className="mx-2 text-gray-400">/</span> ');

  return `        <nav className="text-sm mb-8" aria-label="Breadcrumb">${items}</nav>`;
}

function renderRelatedLinks(links: InternalLink[]): string {
  const relatedLinks = links.filter((l) => l.context === "related" || l.context === "inline");
  if (relatedLinks.length === 0) return "";

  const items = relatedLinks
    .map((l) => `            <li><a href="${l.href}" className="text-green-700 hover:underline">${l.text}</a></li>`)
    .join("\n");

  return `
        <section className="mt-12 bg-gray-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Related Products and Locations</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
${items}
          </ul>
        </section>`;
}

export function renderProductPageTemplate(input: ProductPageInput): string {
  const componentName = `${input.category.replace(/[^a-zA-Z0-9]/g, "")}ProductPage`;
  const productSchemaJson = JSON.stringify(input.schemaMarkup, null, 2);
  const faqSchemaJson = JSON.stringify(input.faqSchema, null, 2);
  const breadcrumbSchemaJson = JSON.stringify(input.breadcrumbSchema, null, 2);

  const productGrid = renderProductGrid(input.products);
  const faqSection = renderFAQSection(input.faqs);
  const breadcrumbNav = renderBreadcrumbs(input.breadcrumbs);
  const relatedLinks = renderRelatedLinks(input.internalLinks);

  const capitalizedCategory = input.category.charAt(0).toUpperCase() + input.category.slice(1);

  return `const productSchema = ${productSchemaJson};

const faqSchema = ${faqSchemaJson};

const breadcrumbSchema = ${breadcrumbSchemaJson};

const metaTitle = "${escapeJsx(input.meta.title)}";
const metaDescription = "${escapeJsx(input.meta.description)}";

export const ${componentName} = () => (
  <article className="max-w-4xl mx-auto px-4 py-12">
${breadcrumbNav}

    <header className="mb-10">
      <h1 className="text-4xl font-bold mb-4">${input.clientName} ${capitalizedCategory} Guide</h1>
      <p className="text-xl text-gray-600">Average price: $${input.avgPrice.toFixed(2)} | Range: ${input.priceRange}</p>
    </header>

    <section className="prose prose-lg max-w-none mb-10">
${input.generatedBody}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Available ${capitalizedCategory} Products</h2>
${productGrid}
    </section>

${faqSection}

${relatedLinks}

    <section className="mt-12 bg-green-50 rounded-lg p-8 text-center">
      <h2 className="text-2xl font-bold mb-3">Shop ${capitalizedCategory} at ${input.clientName}</h2>
      <p className="text-gray-700 mb-6">Browse our full ${input.category} selection with current pricing and availability.</p>
      <a href="/menu" className="inline-block bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition-colors">View Full Menu</a>
    </section>

    <script type="application/ld+json">{JSON.stringify(productSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(faqSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(breadcrumbSchema)}</script>
  </article>
);
`;
}
