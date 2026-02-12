import { readFile } from "node:fs/promises";
import path from "node:path";
import type { ClientConfig } from "../config/schema.js";
import { createContentPullRequest } from "../publishers/github-pr.js";

export async function runPublish(config: ClientConfig, contentPath: string): Promise<{ prUrl: string; branch: string }> {
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
    body: "Automated publish from SIGNAL pipeline (React/Vite/Netlify workflow).",
  });
}
