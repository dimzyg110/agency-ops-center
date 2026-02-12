export interface ReviewResult {
  passed: boolean;
  score: number;
  issues: string[];
}

export function runReview(content: string): ReviewResult {
  const issues: string[] = [];

  if (!content.includes("<h1")) {
    issues.push("Missing H1 heading.");
  }
  if (!content.includes("application/ld+json")) {
    issues.push("Missing JSON-LD schema block.");
  }
  if (content.length < 700) {
    issues.push("Content appears too short for SEO target.");
  }

  const score = Math.max(0, 100 - issues.length * 20);
  return {
    passed: issues.length === 0,
    score,
    issues,
  };
}
