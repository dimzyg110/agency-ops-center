#!/usr/bin/env node
import "dotenv/config";
import { Command } from "commander";
import path from "node:path";
import { writeFile } from "node:fs/promises";
import { loadClientConfig } from "./config/schema.js";
import { runGenerate, type ContentType } from "./pipeline/generate.js";
import { runHumanize } from "./pipeline/humanize.js";
import { runPublish, runBatchPublish } from "./pipeline/publish.js";
import { runResearch } from "./pipeline/research.js";
import { runReview } from "./pipeline/review.js";

interface SharedOptions {
  client: string;
  type: ContentType;
  target?: string;
  category?: string;
  topic?: string;
}

const VALID_TYPES: ContentType[] = ["location-page", "product-page", "market-report", "blog-post"];

function validateContentType(type: string): ContentType {
  if (!VALID_TYPES.includes(type as ContentType)) {
    throw new Error(`Invalid content type: '${type}'. Must be one of: ${VALID_TYPES.join(", ")}`);
  }
  return type as ContentType;
}

const program = new Command();
program.name("signal").description("SIGNAL SEO automation CLI").version("0.1.0");

async function runGenerationFlow(options: SharedOptions): Promise<{ outputPath: string; content: string }> {
  const config = await loadClientConfig(options.client);
  const researchTarget = options.target ?? "East Boston";
  const validatedType = validateContentType(options.type);
  const research = await runResearch(config, researchTarget, validatedType);

  return runGenerate({
    config,
    type: validatedType,
    target: options.target,
    category: options.category,
    topic: options.topic,
    research,
  });
}

program
  .command("generate")
  .requiredOption("--client <slug>", "Client slug, e.g. ch")
  .requiredOption("--type <type>", "location-page | product-page | market-report | blog-post")
  .option("--target <target>", "Location target")
  .option("--category <category>", "Product category")
  .option("--topic <topic>", "Blog topic")
  .action(async (options: SharedOptions) => {
    try {
      const result = await runGenerationFlow(options);
      console.log(`Generated: ${result.outputPath}`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown generate error";
      console.error(`Generate failed: ${reason}`);
      process.exitCode = 1;
    }
  });

program
  .command("pipeline")
  .requiredOption("--client <slug>", "Client slug")
  .requiredOption("--type <type>", "location-page | product-page | market-report | blog-post | all")
  .option("--target <target>", "Location target")
  .option("--category <category>", "Product category")
  .option("--topic <topic>", "Blog topic")
  .action(async (options: SharedOptions) => {
    try {
      const config = await loadClientConfig(options.client);

      // Handle "all" type — batch generation of all content types
      if (options.type === ("all" as ContentType)) {
        console.log("Starting batch pipeline for all content types...");
        const contentPaths: string[] = [];
        const errors: string[] = [];

        // Generate location pages for all configured towns
        if (config.content.locationPages.enabled) {
          for (const town of config.content.locationPages.towns) {
            try {
              console.log(`Generating location page: ${town}`);
              const result = await runSinglePipeline(config, "location-page", town, undefined, undefined);
              contentPaths.push(result.outputPath);
            } catch (error) {
              const reason = error instanceof Error ? error.message : "Unknown error";
              errors.push(`Location page (${town}): ${reason}`);
              console.warn(`Failed location page for ${town}: ${reason}`);
            }
          }
        }

        // Generate product pages for all configured categories
        if (config.content.productPages.enabled) {
          for (const category of config.content.productPages.categories) {
            try {
              console.log(`Generating product page: ${category}`);
              const result = await runSinglePipeline(config, "product-page", undefined, category, undefined);
              contentPaths.push(result.outputPath);
            } catch (error) {
              const reason = error instanceof Error ? error.message : "Unknown error";
              errors.push(`Product page (${category}): ${reason}`);
              console.warn(`Failed product page for ${category}: ${reason}`);
            }
          }
        }

        // Generate a market report
        if (config.content.marketReports.enabled) {
          try {
            console.log("Generating market report...");
            const result = await runSinglePipeline(config, "market-report", options.target, undefined, undefined);
            contentPaths.push(result.outputPath);
          } catch (error) {
            const reason = error instanceof Error ? error.message : "Unknown error";
            errors.push(`Market report: ${reason}`);
          }
        }

        console.log(`\nBatch complete: ${contentPaths.length} generated, ${errors.length} failed.`);

        if (errors.length > 0) {
          console.warn("Failures:");
          for (const err of errors) {
            console.warn(`  - ${err}`);
          }
        }

        // Batch publish all successful content
        if (contentPaths.length > 0) {
          try {
            const publishResult = await runBatchPublish(config, contentPaths);
            console.log(`Batch PR: ${publishResult.prUrl}`);
          } catch (error) {
            const reason = error instanceof Error ? error.message : "Unknown publish error";
            console.error(`Batch publish failed: ${reason}`);
          }
        }

        return;
      }

      // Single content type pipeline
      const result = await runSinglePipeline(
        config,
        validateContentType(options.type),
        options.target,
        options.category,
        options.topic
      );

      const publishResult = await runPublish(config, result.outputPath);
      console.log(`Pipeline complete. PR: ${publishResult.prUrl}`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown pipeline error";
      console.error(`Pipeline failed: ${reason}`);
      process.exitCode = 1;
    }
  });

/**
 * Run generate → review → humanize → save for a single content piece.
 * Partial failure handling: returns result even if humanizer fails.
 */
async function runSinglePipeline(
  config: import("./config/schema.js").ClientConfig,
  type: ContentType,
  target?: string,
  category?: string,
  topic?: string
): Promise<{ outputPath: string; content: string }> {
  const researchTarget = target ?? "East Boston";
  const research = await runResearch(config, researchTarget, type);

  const generated = await runGenerate({
    config,
    type,
    target,
    category,
    topic,
    research,
  });

  const review = runReview(generated.content, {
    contentType: type,
    targetKeyword: research.keywordBrief.primaryKeyword,
  });

  if (!review.passed) {
    console.warn(`Review warnings (score ${review.score}):`);
    for (const issue of review.issues) {
      console.warn(`  ${issue}`);
    }
    // Only block on errors, not warnings
    const hasErrors = review.checks.some((c) => c.severity === "error" && !c.passed);
    if (hasErrors) {
      throw new Error(`Review failed (score ${review.score}): ${review.issues.join(" | ")}`);
    }
  }

  // Humanize the content
  const humanized = await runHumanize(generated.content, config.tone.voice);
  const outputPath = path.resolve(generated.outputPath);
  await writeFile(outputPath, humanized, "utf-8");

  return { outputPath, content: humanized };
}

program
  .command("publish")
  .requiredOption("--client <slug>", "Client slug")
  .requiredOption("--content <path>", "Path to generated content file")
  .action(async (options: { client: string; content: string }) => {
    try {
      const config = await loadClientConfig(options.client);
      const result = await runPublish(config, options.content);
      console.log(`Published PR: ${result.prUrl}`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown publish error";
      console.error(`Publish failed: ${reason}`);
      process.exitCode = 1;
    }
  });

program
  .command("status")
  .requiredOption("--client <slug>", "Client slug")
  .action(async (options: { client: string }) => {
    try {
      const config = await loadClientConfig(options.client);
      console.log(`Client: ${config.client.name}`);
      console.log(`Platform: ${config.client.platform}`);
      console.log(`Repo: ${config.client.repo}`);
      console.log(`Primary keywords tracked: ${config.keywords.primary.length}`);
      console.log(`Location pages: ${config.content.locationPages.enabled ? config.content.locationPages.towns.join(", ") : "disabled"}`);
      console.log(`Product pages: ${config.content.productPages.enabled ? config.content.productPages.categories.join(", ") : "disabled"}`);
      console.log(`Market reports: ${config.content.marketReports.enabled ? config.content.marketReports.frequency : "disabled"}`);
      console.log(`Blog posts: ${config.content.blogPosts.enabled ? config.content.blogPosts.frequency : "disabled"}`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown status error";
      console.error(`Status failed: ${reason}`);
      process.exitCode = 1;
    }
  });

void program.parseAsync(process.argv);
