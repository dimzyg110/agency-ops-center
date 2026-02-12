import type { CategoryPriceData, CompetitorComparison } from "../glass/data-injector.js";
import type { InternalLink } from "../seo/internal-links.js";
import type { MetaTagResult } from "../seo/meta.js";

export interface MarketReportInput {
  title: string;
  /** LLM-generated analysis body (HTML string) */
  generatedBody: string;
  schemaMarkup: Record<string, unknown>;
  breadcrumbSchema: Record<string, unknown>;
  categoryBreakdown: CategoryPriceData[];
  competitors: CompetitorComparison[];
  internalLinks: InternalLink[];
  breadcrumbs: InternalLink[];
  meta: MetaTagResult;
  clientName: string;
  city: string;
  reportDate: string;
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
                <th className="py-3 pr-4">Average Price</th>
                <th className="py-3 pr-4">Price Range</th>
                <th className="py-3">Products Tracked</th>
              </tr>
            </thead>
            <tbody>
${rows}
            </tbody>
          </table>
        </div>`;
}

function renderCompetitorTable(competitors: CompetitorComparison[]): string {
  if (competitors.length === 0) return "";

  const rows = competitors
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
                <th className="py-3 pr-4">Average Price</th>
                <th className="py-3 pr-4">Products</th>
                <th className="py-3">Strongest Category</th>
              </tr>
            </thead>
            <tbody>
${rows}
            </tbody>
          </table>
        </div>`;
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
          <h2 className="text-2xl font-bold mb-4">Related Content</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
${items}
          </ul>
        </section>`;
}

export function renderMarketReportTemplate(input: MarketReportInput): string {
  const articleSchema = JSON.stringify(input.schemaMarkup, null, 2);
  const breadcrumbSchemaJson = JSON.stringify(input.breadcrumbSchema, null, 2);

  const categoryTable = renderCategoryTable(input.categoryBreakdown);
  const competitorTable = renderCompetitorTable(input.competitors);
  const breadcrumbNav = renderBreadcrumbs(input.breadcrumbs);
  const relatedLinks = renderRelatedLinks(input.internalLinks);

  return `const articleSchema = ${articleSchema};

const breadcrumbSchema = ${breadcrumbSchemaJson};

const metaTitle = "${escapeJsx(input.meta.title)}";
const metaDescription = "${escapeJsx(input.meta.description)}";

export const MarketReport = () => (
  <article className="max-w-4xl mx-auto px-4 py-12">
${breadcrumbNav}

    <header className="mb-10">
      <h1 className="text-4xl font-bold mb-4">${input.title}</h1>
      <div className="flex items-center text-sm text-gray-500 gap-4">
        <time dateTime="${input.reportDate}">${input.reportDate}</time>
        <span>By ${input.clientName} Market Intelligence</span>
      </div>
    </header>

    <section className="prose prose-lg max-w-none mb-10">
${input.generatedBody}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Price Breakdown by Category</h2>
${categoryTable}
    </section>

    <section className="mb-10">
      <h2 className="text-2xl font-bold mb-4">Competitor Landscape in ${input.city}</h2>
${competitorTable}
    </section>

${relatedLinks}

    <section className="mt-12 bg-blue-50 rounded-lg p-8 text-center">
      <h2 className="text-2xl font-bold mb-3">Get the Full Market Picture</h2>
      <p className="text-gray-700 mb-6">Visit ${input.clientName} to see our current menu and pricing.</p>
      <a href="/menu" className="inline-block bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition-colors">View Current Menu</a>
    </section>

    <script type="application/ld+json">{JSON.stringify(articleSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(breadcrumbSchema)}</script>
  </article>
);
`;
}
