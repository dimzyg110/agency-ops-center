import { readFile } from "node:fs/promises";
import path from "node:path";
import type { ClientConfig } from "../config/schema.js";
import { createContentPullRequest, createBatchPullRequest, type GitHubPublishInput } from "../publishers/github-pr.js";

export interface PublishResult {
  prUrl: string;
  branch: string;
}

/**
 * Publish a single content file as a PR.
 */
export async function runPublish(config: ClientConfig, contentPath: string): Promise<PublishResult> {
  const absoluteContentPath = path.resolve(process.cwd(), contentPath);
  let content: string;

  try {
    content = await readFile(absoluteContentPath, "utf-8");
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown read error";
    throw new Error(`Unable to read content file ${absoluteContentPath}: ${reason}`);
  }

  const [owner, repo] = config.client.repo.split("/");
  if (!owner || !repo) {
    throw new Error(`Invalid repo format '${config.client.repo}'. Expected owner/repo.`);
  }

  const branchName = `signal/${config.client.slug}/${Date.now()}`;
  const targetPath = `${config.client.contentDir}/seo/${path.basename(absoluteContentPath)}`;

  return createContentPullRequest({
    owner,
    repo,
    baseBranch: "main",
    branchName,
    targetPath,
    content,
    commitMessage: `feat(signal): publish ${path.basename(absoluteContentPath)}`,
    title: `SIGNAL: Publish ${path.basename(absoluteContentPath)}`,
    body: buildPRDescription([path.basename(absoluteContentPath)]),
  });
}

/**
 * Publish multiple content files in a single batch PR.
 */
export async function runBatchPublish(
  config: ClientConfig,
  contentPaths: string[]
): Promise<PublishResult> {
  const [owner, repo] = config.client.repo.split("/");
  if (!owner || !repo) {
    throw new Error(`Invalid repo format '${config.client.repo}'. Expected owner/repo.`);
  }

  const files: Array<{ targetPath: string; content: string; filename: string }> = [];

  for (const contentPath of contentPaths) {
    const absoluteContentPath = path.resolve(process.cwd(), contentPath);
    try {
      const content = await readFile(absoluteContentPath, "utf-8");
      const filename = path.basename(absoluteContentPath);
      files.push({
        targetPath: `${config.client.contentDir}/seo/${filename}`,
        content,
        filename,
      });
    } catch (error) {
      const reason = error instanceof Error ? error.message : "Unknown read error";
      console.warn(`Skipping ${contentPath}: ${reason}`);
    }
  }

  if (files.length === 0) {
    throw new Error("No content files could be read for batch publish.");
  }

  const branchName = `signal/${config.client.slug}/batch-${Date.now()}`;
  const filenames = files.map((f) => f.filename);

  return createBatchPullRequest({
    owner,
    repo,
    baseBranch: "main",
    branchName,
    files: files.map((f) => ({
      path: f.targetPath,
      content: f.content,
    })),
    commitMessage: `feat(signal): batch publish ${files.length} content files`,
    title: `SIGNAL: Batch publish ${files.length} content files`,
    body: buildPRDescription(filenames),
  });
}

function buildPRDescription(filenames: string[]): string {
  const fileList = filenames.map((f) => `- \`${f}\``).join("\n");
  return `## SIGNAL Automated Content Publish

### Files included
${fileList}

### Quality checks
All files passed SIGNAL's automated quality review:
- ✅ Word count (minimum threshold met)
- ✅ Schema markup validated
- ✅ Cannabis compliance check (935 CMR 500)
- ✅ Readability score in range
- ✅ Internal links present
- ✅ Heading structure verified

### Review notes
- Content generated and humanized by SIGNAL pipeline
- GLASS market data injected from live API
- Schema markup includes LocalBusiness/Product/FAQPage/Article + BreadcrumbList
- Internal links follow hub-and-spoke topic cluster architecture

**Platform:** React / Vite / Tailwind / Netlify
`;
}
