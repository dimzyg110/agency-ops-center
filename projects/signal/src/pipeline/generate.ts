import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import OpenAI from "openai";
import type { ClientConfig } from "../config/schema.js";
import type { ResearchContext } from "./research.js";
import { injectGlassData } from "../glass/data-injector.js";
import { generateSchemaMarkup } from "../seo/schema-markup.js";
import { renderBlogPostTemplate } from "../templates/blog-post.js";
import { renderLocationPageTemplate } from "../templates/location-page.js";
import { renderMarketReportTemplate } from "../templates/market-report.js";
import { renderProductPageTemplate } from "../templates/product-page.js";

export type ContentType = "location-page" | "product-page" | "market-report" | "blog-post";

export interface GenerateInput {
  config: ClientConfig;
  type: ContentType;
  target?: string;
  category?: string;
  topic?: string;
  research: ResearchContext;
}

async function generateNarrative(prompt: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return "OpenAI key not configured; generated fallback copy for MVP scaffolding.";
  }

  try {
    const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";
    const openai = new OpenAI({ apiKey });
    const completion = await openai.responses.create({
      model,
      input: prompt,
    });

    return completion.output_text || "Generated empty response from model.";
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown OpenAI error";
    throw new Error(`Content generation failed: ${reason}`);
  }
}

export async function runGenerate(input: GenerateInput): Promise<{ outputPath: string; content: string }> {
  const slugPart = (input.target || input.category || input.topic || input.type).toLowerCase().replace(/\s+/g, "-");
  const outputDir = path.resolve(process.cwd(), "output", input.config.client.slug);
  await mkdir(outputDir, { recursive: true });

  const market = injectGlassData(input.research.prices, input.research.products);
  const prompt = `Create concise SEO copy for ${input.type} about ${slugPart}. Audience: ${input.config.audience.primary}. Tone: ${input.config.tone.voice}.`;
  const generatedBody = await generateNarrative(prompt);

  let content = "";

  if (input.type === "location-page") {
    const city = input.target ?? "East Boston";
    content = renderLocationPageTemplate({
      city,
      clientName: input.config.client.name,
      schemaMarkup: generateSchemaMarkup("LocalBusiness", {
        name: input.config.client.name,
        areaServed: city,
        url: `https://${input.config.client.domain}`,
      }),
      market,
    });
  } else if (input.type === "product-page") {
    const category = input.category ?? "flower";
    content = renderProductPageTemplate({
      category,
      clientName: input.config.client.name,
      body: generatedBody,
      schemaMarkup: generateSchemaMarkup("Product", {
        name: `${input.config.client.name} ${category}`,
        description: generatedBody,
      }),
    });
  } else if (input.type === "market-report") {
    content = renderMarketReportTemplate({
      title: `${input.config.client.name} Weekly Market Report`,
      summary: `${generatedBody}\n\n${input.research.competitorSummary}`,
      schemaMarkup: generateSchemaMarkup("Article", {
        headline: `${input.config.client.name} Market Report`,
      }),
    });
  } else {
    const topic = input.topic ?? "airport cannabis guide";
    content = renderBlogPostTemplate({
      title: `${input.config.client.name}: ${topic}`,
      topic,
      body: generatedBody,
      schemaMarkup: generateSchemaMarkup("Article", {
        headline: topic,
      }),
    });
  }

  const outputPath = path.join(outputDir, `${input.type}-${slugPart}.tsx`);
  await writeFile(outputPath, content, "utf-8");

  return { outputPath, content };
}
