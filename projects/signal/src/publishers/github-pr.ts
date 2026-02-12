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

export async function createContentPullRequest(input: GitHubPublishInput): Promise<{ prUrl: string; branch: string }> {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN is required for publishing.");
  }

  const octokit = new Octokit({ auth: token });

  try {
    const baseRef = await octokit.git.getRef({
      owner: input.owner,
      repo: input.repo,
      ref: `heads/${input.baseBranch}`,
    });

    await octokit.git.createRef({
      owner: input.owner,
      repo: input.repo,
      ref: `refs/heads/${input.branchName}`,
      sha: baseRef.data.object.sha,
    });

    await octokit.repos.createOrUpdateFileContents({
      owner: input.owner,
      repo: input.repo,
      path: input.targetPath,
      message: input.commitMessage,
      content: Buffer.from(input.content).toString("base64"),
      branch: input.branchName,
    });

    const pr = await octokit.pulls.create({
      owner: input.owner,
      repo: input.repo,
      title: input.title,
      head: input.branchName,
      base: input.baseBranch,
      body: input.body,
    });

    return { prUrl: pr.data.html_url, branch: input.branchName };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown GitHub publishing error";
    throw new Error(`Failed to publish PR for ${input.owner}/${input.repo}: ${reason}`);
  }
}
