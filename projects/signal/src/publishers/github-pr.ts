import { Octokit } from "@octokit/rest";

export interface GitHubPublishInput {
  owner: string;
  repo: string;
  baseBranch: string;
  branchName: string;
  targetPath: string;
  content: string;
  commitMessage: string;
  title: string;
  body: string;
}

export interface BatchPublishInput {
  owner: string;
  repo: string;
  baseBranch: string;
  branchName: string;
  files: Array<{ path: string; content: string }>;
  commitMessage: string;
  title: string;
  body: string;
}

const MAX_RETRIES = 3;
const BASE_DELAY_MS = 1000;

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getOctokit(): Octokit {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN is required for publishing.");
  }
  return new Octokit({ auth: token });
}

/**
 * Retry wrapper for GitHub API calls with exponential backoff.
 * Retries on rate limits (403/429) and server errors (5xx).
 */
async function withRetry<T>(fn: () => Promise<T>, context: string): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      const isRetryable =
        lastError.message.includes("403") ||
        lastError.message.includes("429") ||
        lastError.message.includes("500") ||
        lastError.message.includes("502") ||
        lastError.message.includes("503");

      if (!isRetryable || attempt === MAX_RETRIES - 1) {
        break;
      }

      const delayMs = BASE_DELAY_MS * Math.pow(2, attempt) + Math.random() * 500;
      console.warn(`GitHub API ${context} failed (attempt ${attempt + 1}/${MAX_RETRIES}), retrying in ${Math.round(delayMs)}ms`);
      await sleep(delayMs);
    }
  }

  throw new Error(`GitHub API ${context} failed after ${MAX_RETRIES} attempts: ${lastError?.message ?? "Unknown error"}`);
}

/**
 * Create a PR with a single content file.
 */
export async function createContentPullRequest(input: GitHubPublishInput): Promise<{ prUrl: string; branch: string }> {
  const octokit = getOctokit();

  try {
    const baseRef = await withRetry(
      () => octokit.git.getRef({ owner: input.owner, repo: input.repo, ref: `heads/${input.baseBranch}` }),
      "getRef"
    );

    // Create branch with collision avoidance
    let branchName = input.branchName;
    try {
      await octokit.git.createRef({
        owner: input.owner,
        repo: input.repo,
        ref: `refs/heads/${branchName}`,
        sha: baseRef.data.object.sha,
      });
    } catch {
      // Branch name collision — add random suffix
      branchName = `${input.branchName}-${Math.random().toString(36).slice(2, 8)}`;
      await withRetry(
        () =>
          octokit.git.createRef({
            owner: input.owner,
            repo: input.repo,
            ref: `refs/heads/${branchName}`,
            sha: baseRef.data.object.sha,
          }),
        "createRef"
      );
    }

    await withRetry(
      () =>
        octokit.repos.createOrUpdateFileContents({
          owner: input.owner,
          repo: input.repo,
          path: input.targetPath,
          message: input.commitMessage,
          content: Buffer.from(input.content).toString("base64"),
          branch: branchName,
        }),
      "createFile"
    );

    const pr = await withRetry(
      () =>
        octokit.pulls.create({
          owner: input.owner,
          repo: input.repo,
          title: input.title,
          head: branchName,
          base: input.baseBranch,
          body: input.body,
        }),
      "createPR"
    );

    return { prUrl: pr.data.html_url, branch: branchName };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown GitHub publishing error";
    throw new Error(`Failed to publish PR for ${input.owner}/${input.repo}: ${reason}`);
  }
}

/**
 * Create a PR with multiple content files in a single commit.
 * Used for batch publishing to avoid PR fatigue.
 */
export async function createBatchPullRequest(input: BatchPublishInput): Promise<{ prUrl: string; branch: string }> {
  const octokit = getOctokit();

  try {
    // Get base branch ref
    const baseRef = await withRetry(
      () => octokit.git.getRef({ owner: input.owner, repo: input.repo, ref: `heads/${input.baseBranch}` }),
      "getRef"
    );
    const baseSha = baseRef.data.object.sha;

    // Get the base tree
    const baseCommit = await withRetry(
      () => octokit.git.getCommit({ owner: input.owner, repo: input.repo, commit_sha: baseSha }),
      "getCommit"
    );
    const baseTreeSha = baseCommit.data.tree.sha;

    // Create blobs for each file
    const treeItems: Array<{
      path: string;
      mode: "100644";
      type: "blob";
      sha: string;
    }> = [];

    for (const file of input.files) {
      const blob = await withRetry(
        () =>
          octokit.git.createBlob({
            owner: input.owner,
            repo: input.repo,
            content: Buffer.from(file.content).toString("base64"),
            encoding: "base64",
          }),
        `createBlob(${file.path})`
      );
      treeItems.push({
        path: file.path,
        mode: "100644",
        type: "blob",
        sha: blob.data.sha,
      });
    }

    // Create tree
    const tree = await withRetry(
      () =>
        octokit.git.createTree({
          owner: input.owner,
          repo: input.repo,
          base_tree: baseTreeSha,
          tree: treeItems,
        }),
      "createTree"
    );

    // Create commit
    const commit = await withRetry(
      () =>
        octokit.git.createCommit({
          owner: input.owner,
          repo: input.repo,
          message: input.commitMessage,
          tree: tree.data.sha,
          parents: [baseSha],
        }),
      "createCommit"
    );

    // Create branch
    let branchName = input.branchName;
    try {
      await octokit.git.createRef({
        owner: input.owner,
        repo: input.repo,
        ref: `refs/heads/${branchName}`,
        sha: commit.data.sha,
      });
    } catch {
      branchName = `${input.branchName}-${Math.random().toString(36).slice(2, 8)}`;
      await withRetry(
        () =>
          octokit.git.createRef({
            owner: input.owner,
            repo: input.repo,
            ref: `refs/heads/${branchName}`,
            sha: commit.data.sha,
          }),
        "createRef"
      );
    }

    // Create PR
    const pr = await withRetry(
      () =>
        octokit.pulls.create({
          owner: input.owner,
          repo: input.repo,
          title: input.title,
          head: branchName,
          base: input.baseBranch,
          body: input.body,
        }),
      "createPR"
    );

    return { prUrl: pr.data.html_url, branch: branchName };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown GitHub batch publishing error";
    throw new Error(`Failed to create batch PR for ${input.owner}/${input.repo}: ${reason}`);
  }
}
