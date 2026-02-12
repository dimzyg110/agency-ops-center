import type { InjectedMarketContext, CategoryPriceData, FeaturedProduct, CompetitorComparison } from "../glass/data-injector.js";
import type { InternalLink } from "../seo/internal-links.js";
import type { MetaTagResult } from "../seo/meta.js";
import type { FAQItem } from "../seo/schema-markup.js";

export interface LocationPageInput {
  city: string;
  state: string;
  clientName: string;
  /** LLM-generated body sections (HTML string) */
  generatedBody: string;
  schemaMarkup: Record<string, unknown>;
  faqSchema: Record<string, unknown>;
  breadcrumbSchema: Record<string, unknown>;
  market: InjectedMarketContext;
  faqs: FAQItem[];
  internalLinks: InternalLink[];
  breadcrumbs: InternalLink[];
  meta: MetaTagResult;
}

function escapeJsx(str: string): string {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function renderCategoryTable(categories: CategoryPriceData[]): string {
  if (categories.length === 0) return "";

  const rows = categories
    .map(
      (cat) =>
        `            <tr className="border-b border-gray-100">
              <td className="py-3 pr-4 font-medium capitalize">${cat.category}</td>
              <td className="py-3 pr-4">$${cat.avgPrice.toFixed(2)}</td>
              <td className="py-3 pr-4">$${cat.minPrice.toFixed(2)} – $${cat.maxPrice.toFixed(2)}</td>
              <td className="py-3">${cat.productCount}</td>
            </tr>`
    )
    .join("\n");

  return `
        <div className="overflow-x-auto my-8">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="py-3 pr-4">Category</th>
                <th className="py-3 pr-4">Avg Price</th>
                <th className="py-3 pr-4">Price Range</th>
                <th className="py-3">Products</th>
              </tr>
            </thead>
            <tbody>
${rows}
            </tbody>
          </table>
        </div>`;
}

function renderFeaturedProducts(products: FeaturedProduct[]): string {
  if (products.length === 0) return "";

  const items = products
    .map(
      (p) =>
        `            <li className="flex justify-between py-2 border-b border-gray-50">
              <span>${p.name} <span className="text-gray-500 text-sm capitalize">(${p.category})</span></span>
              <span className="font-semibold">${p.inStock ? `$${p.price.toFixed(2)}` : "Out of stock"}</span>
            </li>`
    )
    .join("\n");

  return `
        <ul className="divide-y divide-gray-50">
${items}
        </ul>`;
}

function renderCompetitorComparisons(comparisons: CompetitorComparison[]): string {
  if (comparisons.length === 0) return "";

  const rows = comparisons
    .map(
      (c) =>
        `            <tr className="border-b border-gray-100">
              <td className="py-3 pr-4">${c.operatorName}</td>
              <td className="py-3 pr-4">$${c.avgPrice.toFixed(2)}</td>
              <td className="py-3 pr-4">${c.productCount}</td>
              <td className="py-3 capitalize">${c.categoryStrength}</td>
            </tr>`
    )
    .join("\n");

  return `
        <div className="overflow-x-auto my-8">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="py-3 pr-4">Dispensary</th>
                <th className="py-3 pr-4">Avg Price</th>
                <th className="py-3 pr-4">Products</th>
                <th className="py-3">Top Category</th>
              </tr>
            </thead>
            <tbody>
${rows}
            </tbody>
          </table>
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
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
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
          <h2 className="text-2xl font-bold mb-4">Explore More</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
${items}
          </ul>
        </section>`;
}

export function renderLocationPageTemplate(input: LocationPageInput): string {
  const componentName = `${input.city.replace(/[^a-zA-Z0-9]/g, "")}LocationPage`;
  const localBusinessSchema = JSON.stringify(input.schemaMarkup, null, 2);
  const faqSchemaJson = JSON.stringify(input.faqSchema, null, 2);
  const breadcrumbSchemaJson = JSON.stringify(input.breadcrumbSchema, null, 2);

  const categoryTable = renderCategoryTable(input.market.categoryPriceBreakdown);
  const featuredProducts = renderFeaturedProducts(input.market.featuredProducts);
  const competitors = renderCompetitorComparisons(input.market.competitorComparisons);
  const faqSection = renderFAQSection(input.faqs);
  const breadcrumbNav = renderBreadcrumbs(input.breadcrumbs);
  const relatedLinks = renderRelatedLinks(input.internalLinks);

  return `const localBusinessSchema = ${localBusinessSchema};

const faqSchema = ${faqSchemaJson};

const breadcrumbSchema = ${breadcrumbSchemaJson};

const metaTitle = "${escapeJsx(input.meta.title)}";
const metaDescription = "${escapeJsx(input.meta.description)}";

export const ${componentName} = () => (
  <article className="max-w-4xl mx-auto px-4 py-12">
${breadcrumbNav}

    <header className="mb-10">
      <h1 className="text-4xl font-bold mb-4">${input.clientName} in ${input.city}, ${input.state}</h1>
      <p className="text-xl text-gray-600">${input.market.narratives.valueProposition}</p>
    </header>

    <section className="prose prose-lg max-w-none mb-10">
${input.generatedBody}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Current Pricing by Category in ${input.city}</h2>
      <p className="text-gray-600 mb-4">${input.market.narratives.pricingNarrative}</p>
${categoryTable}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Featured Products</h2>
${featuredProducts}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">${input.city} Dispensary Comparison</h2>
      <p className="text-gray-600 mb-4">${input.market.narratives.competitiveNarrative}</p>
${competitors}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Inventory and Availability</h2>
      <p className="leading-relaxed">${input.market.narratives.inventoryNarrative}</p>
    </section>

${faqSection}

${relatedLinks}

    <section className="mt-12 bg-green-50 rounded-lg p-8 text-center">
      <h2 className="text-2xl font-bold mb-3">Visit ${input.clientName} in ${input.city}</h2>
      <p className="text-gray-700 mb-6">Stop by today and explore our full menu of cannabis products.</p>
      <a href="/menu" className="inline-block bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition-colors">View Our Menu</a>
    </section>

    <script type="application/ld+json">{JSON.stringify(localBusinessSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(faqSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(breadcrumbSchema)}</script>
  </article>
);
`;
}
