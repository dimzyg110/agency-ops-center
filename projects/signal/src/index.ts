#!/usr/bin/env node
import "dotenv/config";
import { Command } from "commander";
import path from "node:path";
import { writeFile } from "node:fs/promises";
import { loadClientConfig } from "./config/schema.js";
import { runGenerate, type ContentType } from "./pipeline/generate.js";
import { runHumanize } from "./pipeline/humanize.js";
import { runPublish } from "./pipeline/publish.js";
import { runResearch } from "./pipeline/research.js";
import { runReview } from "./pipeline/review.js";

interface SharedOptions {
  client: string;
  type: ContentType;
  target?: string;
  category?: string;
  topic?: string;
}

const program = new Command();
program.name("signal").description("SIGNAL SEO automation CLI").version("0.1.0");

async function runGenerationFlow(options: SharedOptions): Promise<{ outputPath: string; content: string }> {
  const config = await loadClientConfig(options.client);
  const researchTarget = options.target ?? "East Boston";
  const research = await runResearch(config, researchTarget);

  return runGenerate({
    config,
    type: options.type,
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
  .requiredOption("--type <type>", "location-page | product-page | market-report | blog-post")
  .option("--target <target>", "Location target")
  .option("--category <category>", "Product category")
  .option("--topic <topic>", "Blog topic")
  .action(async (options: SharedOptions) => {
    try {
      const config = await loadClientConfig(options.client);
      const generated = await runGenerationFlow(options);
      const review = runReview(generated.content);

      if (!review.passed) {
        throw new Error(`Review failed (score ${review.score}): ${review.issues.join(" | ")}`);
      }

      const humanized = runHumanize(generated.content);
      const outputPath = path.resolve(generated.outputPath);
      await writeFile(outputPath, humanized, "utf-8");

      const publishResult = await runPublish(config, outputPath);
      console.log(`Pipeline complete. PR: ${publishResult.prUrl}`);
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown pipeline error";
      console.error(`Pipeline failed: ${reason}`);
      process.exitCode = 1;
    }
  });

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
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown status error";
      console.error(`Status failed: ${reason}`);
      process.exitCode = 1;
    }
  });

void program.parseAsync(process.argv);
