export interface ReviewResult {
  passed: boolean;
  score: number;
  issues: string[];
  checks: QualityCheck[];
}

export interface QualityCheck {
  name: string;
  passed: boolean;
  detail: string;
  severity: "error" | "warning";
}

interface ReviewOptions {
  contentType?: string;
  targetKeyword?: string;
}

// Cannabis compliance — 935 CMR 500 prohibited claims and patterns
const PROHIBITED_CLAIMS: RegExp[] = [
  /\bcure[sd]?\b/i,
  /\btreat(?:s|ment|ing)?\b/i,
  /\bheals?\b/i,
  /\bmedical\s+benefit/i,
  /\btherapeutic\b/i,
  /\bprescri(?:be|ption)\b/i,
  /\bFDA\s+approved\b/i,
  /\bsafe\s+for\s+(?:children|kids|minors|teens|youth)\b/i,
  /\bno\s+side\s+effects\b/i,
  /\bguaranteed\s+(?:results|relief|effects)\b/i,
  /\bweight\s+loss\b/i,
  /\bcancer\b/i,
  /\bepilepsy\b/i,
  /\bseizure\b/i,
  /\baddiction\s+free\b/i,
  /\bnon-addictive\b/i,
];

// Words/phrases that suggest youth targeting (compliance violation)
const YOUTH_TARGETING: RegExp[] = [
  /\bfor\s+(?:kids|children|teens|minors|youth|students)\b/i,
  /\bfamily\s+friendly\b/i,
  /\bcartoon/i,
  /\bcandy\s+(?:flavored|flavour)/i,
];

/**
 * Count words in content (strips HTML/JSX tags first).
 */
function countWords(content: string): number {
  const stripped = content
    .replace(/<[^>]*>/g, " ")
    .replace(/\{[^}]*\}/g, " ")
    .replace(/\/\/[^\n]*/g, " ")
    .replace(/const\s+\w+/g, " ")
    .replace(/export\s+/g, " ")
    .replace(/import\s+[^;]+;/g, " ")
    .replace(/className="[^"]*"/g, " ");
  return stripped.split(/\s+/).filter((word) => word.length > 1).length;
}

/**
 * Calculate Flesch-Kincaid readability score.
 * Score 60-70 is ideal for web content.
 */
function calculateReadability(content: string): number {
  const stripped = content
    .replace(/<[^>]*>/g, " ")
    .replace(/\{[^}]*\}/g, " ")
    .replace(/\/\/[^\n]*/g, " ");

  const sentences = stripped.split(/[.!?]+/).filter((s) => s.trim().length > 5);
  const words = stripped.split(/\s+/).filter((w) => w.length > 1);

  if (sentences.length === 0 || words.length === 0) return 0;

  // Simple syllable count
  const syllableCount = words.reduce((total, word) => {
    const cleaned = word.toLowerCase().replace(/[^a-z]/g, "");
    if (cleaned.length <= 2) return total + 1;
    const vowelGroups = cleaned.match(/[aeiouy]+/g);
    let count = vowelGroups ? vowelGroups.length : 1;
    if (cleaned.endsWith("e") && count > 1) count--;
    return total + Math.max(count, 1);
  }, 0);

  // Flesch Reading Ease formula
  const avgSentenceLength = words.length / sentences.length;
  const avgSyllablesPerWord = syllableCount / words.length;
  return 206.835 - 1.015 * avgSentenceLength - 84.6 * avgSyllablesPerWord;
}

/**
 * Calculate keyword density as a percentage.
 */
function calculateKeywordDensity(content: string, keyword: string): number {
  if (!keyword) return 0;
  const stripped = content.replace(/<[^>]*>/g, " ").toLowerCase();
  const words = stripped.split(/\s+/).filter((w) => w.length > 1);
  if (words.length === 0) return 0;

  const keywordLower = keyword.toLowerCase();
  const keywordWords = keywordLower.split(/\s+/);

  let occurrences = 0;
  for (let i = 0; i <= words.length - keywordWords.length; i++) {
    const phrase = words.slice(i, i + keywordWords.length).join(" ");
    if (phrase === keywordLower) {
      occurrences++;
    }
  }

  return (occurrences * keywordWords.length * 100) / words.length;
}

/**
 * Check for duplicate content signals (title/heading repetition).
 */
function checkDuplicateContent(content: string): string[] {
  const issues: string[] = [];
  const headings = content.match(/<h[1-6][^>]*>[^<]+<\/h[1-6]>/gi) ?? [];
  const headingTexts = headings.map((h) => h.replace(/<[^>]*>/g, "").trim().toLowerCase());

  const seen = new Set<string>();
  for (const text of headingTexts) {
    if (seen.has(text)) {
      issues.push(`Duplicate heading: "${text}"`);
    }
    seen.add(text);
  }

  return issues;
}

/**
 * Run comprehensive quality review on generated content.
 * 11+ automated checks covering SEO, compliance, and content quality.
 */
export function runReview(content: string, options: ReviewOptions = {}): ReviewResult {
  const checks: QualityCheck[] = [];
  const contentType = options.contentType ?? "location-page";

  // 1. H1 heading presence
  const hasH1 = content.includes("<h1");
  checks.push({
    name: "H1 heading",
    passed: hasH1,
    detail: hasH1 ? "H1 heading found" : "Missing H1 heading — required for SEO",
    severity: "error",
  });

  // 2. JSON-LD schema markup
  const hasSchema = content.includes("application/ld+json");
  checks.push({
    name: "Schema markup",
    passed: hasSchema,
    detail: hasSchema ? "JSON-LD schema block found" : "Missing JSON-LD schema markup",
    severity: "error",
  });

  // 3. Minimum word count by content type
  const wordCount = countWords(content);
  const minWordCounts: Record<string, number> = {
    "location-page": 1200,
    "product-page": 600,
    "market-report": 1200,
    "blog-post": 1000,
  };
  const minWords = minWordCounts[contentType] ?? 800;
  const meetsWordCount = wordCount >= minWords;
  checks.push({
    name: "Word count",
    passed: meetsWordCount,
    detail: `${wordCount} words (minimum: ${minWords})`,
    severity: "error",
  });

  // 4. Cannabis compliance (935 CMR 500)
  const complianceViolations: string[] = [];
  for (const pattern of PROHIBITED_CLAIMS) {
    const match = content.match(pattern);
    if (match?.[0]) {
      complianceViolations.push(`Prohibited health claim: "${match[0]}"`);
    }
  }
  for (const pattern of YOUTH_TARGETING) {
    const match = content.match(pattern);
    if (match?.[0]) {
      complianceViolations.push(`Youth targeting language: "${match[0]}"`);
    }
  }
  const passesCompliance = complianceViolations.length === 0;
  checks.push({
    name: "Cannabis compliance",
    passed: passesCompliance,
    detail: passesCompliance
      ? "No prohibited claims or youth-targeting language detected"
      : `${complianceViolations.length} violation(s): ${complianceViolations.join("; ")}`,
    severity: "error",
  });

  // 5. Duplicate content detection
  const duplicateIssues = checkDuplicateContent(content);
  checks.push({
    name: "Duplicate content",
    passed: duplicateIssues.length === 0,
    detail: duplicateIssues.length === 0
      ? "No duplicate headings detected"
      : duplicateIssues.join("; "),
    severity: "warning",
  });

  // 6. Readability score (Flesch-Kincaid)
  const readabilityScore = calculateReadability(content);
  const passesReadability = readabilityScore >= 30 && readabilityScore <= 90;
  checks.push({
    name: "Readability",
    passed: passesReadability,
    detail: `Flesch-Kincaid score: ${Math.round(readabilityScore)} (target: 30-90)`,
    severity: "warning",
  });

  // 7. Keyword density (if keyword provided)
  if (options.targetKeyword) {
    const density = calculateKeywordDensity(content, options.targetKeyword);
    const passesKeyword = density >= 0.5 && density <= 3.0;
    checks.push({
      name: "Keyword density",
      passed: passesKeyword,
      detail: `"${options.targetKeyword}" density: ${density.toFixed(1)}% (target: 0.5-3.0%)`,
      severity: "warning",
    });
  }

  // 8. Schema markup validation (check required properties, not just presence)
  const schemaValid = validateSchemaContent(content, contentType);
  checks.push({
    name: "Schema validation",
    passed: schemaValid.passed,
    detail: schemaValid.detail,
    severity: "error",
  });

  // 9. Internal link count
  const linkMatches = content.match(/href="/g) ?? [];
  const hasEnoughLinks = linkMatches.length >= 3;
  checks.push({
    name: "Internal links",
    passed: hasEnoughLinks,
    detail: `${linkMatches.length} link(s) found (minimum: 3)`,
    severity: "warning",
  });

  // 10. Meta description length
  const metaDescMatch = content.match(/metaDescription\s*=\s*"([^"]+)"/);
  const metaDesc = metaDescMatch?.[1] ?? "";
  const hasMetaDesc = metaDesc.length >= 50 && metaDesc.length <= 160;
  checks.push({
    name: "Meta description",
    passed: hasMetaDesc || metaDesc.length === 0,
    detail: metaDesc.length > 0
      ? `Meta description: ${metaDesc.length} chars (target: 50-160)`
      : "Meta description not found in component (may be handled by layout)",
    severity: "warning",
  });

  // 11. Heading structure (H2s present for content depth)
  const h2Count = (content.match(/<h2/g) ?? []).length;
  const hasGoodStructure = h2Count >= 3;
  checks.push({
    name: "Heading structure",
    passed: hasGoodStructure,
    detail: `${h2Count} H2 heading(s) found (minimum: 3)`,
    severity: "warning",
  });

  // 12. No "Generated by SIGNAL" watermark
  const hasWatermark = content.includes("Generated by SIGNAL");
  checks.push({
    name: "AI watermark removed",
    passed: !hasWatermark,
    detail: hasWatermark
      ? "Contains 'Generated by SIGNAL' watermark — must be removed"
      : "No AI watermarks detected",
    severity: "error",
  });

  // Calculate overall score and pass/fail
  const errorChecks = checks.filter((c) => c.severity === "error");
  const warningChecks = checks.filter((c) => c.severity === "warning");

  const errorsFailed = errorChecks.filter((c) => !c.passed).length;
  const warningsFailed = warningChecks.filter((c) => !c.passed).length;

  // Each error costs 15 points, each warning costs 5 points
  const score = Math.max(0, 100 - errorsFailed * 15 - warningsFailed * 5);
  const passed = errorsFailed === 0; // Must pass ALL error-severity checks

  const issues = checks
    .filter((c) => !c.passed)
    .map((c) => `[${c.severity.toUpperCase()}] ${c.name}: ${c.detail}`);

  return { passed, score, issues, checks };
}

function validateSchemaContent(
  content: string,
  contentType: string
): { passed: boolean; detail: string } {
  const issues: string[] = [];

  if (!content.includes("application/ld+json")) {
    return { passed: false, detail: "No JSON-LD schema found" };
  }

  // Check for required properties based on content type
  if (contentType === "location-page") {
    if (!content.includes('"@type":"Store"') && !content.includes('"@type": "Store"')) {
      // Also accept LocalBusiness
      if (!content.includes("LocalBusiness")) {
        issues.push("Schema should use Store or LocalBusiness type");
      }
    }
    if (!content.includes("PostalAddress") && !content.includes("addressLocality")) {
      issues.push("LocalBusiness schema missing address");
    }
  }

  if (contentType === "product-page") {
    if (!content.includes('"@type":"Product"') && !content.includes('"@type": "Product"')) {
      issues.push("Product schema type not found");
    }
    if (!content.includes("Offer") && !content.includes("offers")) {
      issues.push("Product schema missing offers/price information");
    }
  }

  if (content.includes("FAQPage")) {
    if (!content.includes("Question") || !content.includes("acceptedAnswer")) {
      issues.push("FAQPage schema missing Question/Answer pairs");
    }
  }

  return {
    passed: issues.length === 0,
    detail: issues.length === 0 ? "Schema contains required properties" : issues.join("; "),
  };
}
