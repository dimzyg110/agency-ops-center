import type { InternalLink } from "../seo/internal-links.js";
import type { MetaTagResult } from "../seo/meta.js";
import type { FAQItem } from "../seo/schema-markup.js";

export interface BlogPostInput {
  title: string;
  topic: string;
  /** LLM-generated body (HTML string) */
  generatedBody: string;
  schemaMarkup: Record<string, unknown>;
  faqSchema: Record<string, unknown>;
  breadcrumbSchema: Record<string, unknown>;
  faqs: FAQItem[];
  internalLinks: InternalLink[];
  breadcrumbs: InternalLink[];
  meta: MetaTagResult;
  clientName: string;
  publishDate: string;
  author: string;
}

function escapeJsx(str: string): string {
  return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
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
          <h2 className="text-2xl font-bold mb-4">Related Reading</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
${items}
          </ul>
        </section>`;
}

export function renderBlogPostTemplate(input: BlogPostInput): string {
  const componentName = `${input.topic.replace(/[^a-zA-Z0-9]/g, "")}BlogPost`;
  const articleSchema = JSON.stringify(input.schemaMarkup, null, 2);
  const faqSchemaJson = JSON.stringify(input.faqSchema, null, 2);
  const breadcrumbSchemaJson = JSON.stringify(input.breadcrumbSchema, null, 2);

  const faqSection = renderFAQSection(input.faqs);
  const breadcrumbNav = renderBreadcrumbs(input.breadcrumbs);
  const relatedLinks = renderRelatedLinks(input.internalLinks);

  return `const articleSchema = ${articleSchema};

const faqSchema = ${faqSchemaJson};

const breadcrumbSchema = ${breadcrumbSchemaJson};

const metaTitle = "${escapeJsx(input.meta.title)}";
const metaDescription = "${escapeJsx(input.meta.description)}";

export const ${componentName} = () => (
  <article className="max-w-4xl mx-auto px-4 py-12">
${breadcrumbNav}

    <header className="mb-10">
      <h1 className="text-4xl font-bold mb-4">${input.title}</h1>
      <div className="flex items-center text-sm text-gray-500 gap-4">
        <time dateTime="${input.publishDate}">${input.publishDate}</time>
        <span>By ${input.author}</span>
      </div>
    </header>

    <section className="prose prose-lg max-w-none mb-10">
${input.generatedBody}
    </section>

${faqSection}

${relatedLinks}

    <section className="mt-12 bg-green-50 rounded-lg p-8 text-center">
      <h2 className="text-2xl font-bold mb-3">Visit ${input.clientName}</h2>
      <p className="text-gray-700 mb-6">Explore our full product selection and talk to our knowledgeable staff.</p>
      <a href="/menu" className="inline-block bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition-colors">View Our Menu</a>
    </section>

    <script type="application/ld+json">{JSON.stringify(articleSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(faqSchema)}</script>
    <script type="application/ld+json">{JSON.stringify(breadcrumbSchema)}</script>
  </article>
);
`;
}
