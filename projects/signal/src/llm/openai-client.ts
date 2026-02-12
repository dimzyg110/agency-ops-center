/**
 * Centralized OpenAI client with retry logic, exponential backoff,
 * and model selection for different pipeline stages.
 */
import OpenAI from "openai";

export type LLMRole = "content" | "humanizer" | "research";

const MODEL_MAP: Record<LLMRole, string> = {
  content: "gpt-4o",
  humanizer: "gpt-4o-mini",
  research: "gpt-4o-mini",
};

const MAX_RETRIES = 3;
const BASE_DELAY_MS = 1000;

interface LLMCallOptions {
  role: LLMRole;
  systemPrompt: string;
  userPrompt: string;
  temperature?: number;
  maxTokens?: number;
}

function getOpenAIClient(): OpenAI {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY environment variable is required for LLM calls.");
  }
  return new OpenAI({ apiKey });
}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Call OpenAI with exponential backoff retry.
 * Retries on rate limits (429), server errors (5xx), and timeouts.
 */
export async function callLLM(options: LLMCallOptions): Promise<string> {
  const model = process.env.OPENAI_MODEL ?? MODEL_MAP[options.role];
  const client = getOpenAIClient();

  let lastError: Error | undefined;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const completion = await client.chat.completions.create({
        model,
        messages: [
          { role: "system", content: options.systemPrompt },
          { role: "user", content: options.userPrompt },
        ],
        temperature: options.temperature ?? 0.7,
        max_tokens: options.maxTokens ?? 4096,
      });

      const content = completion.choices[0]?.message?.content;
      if (!content) {
        throw new Error("OpenAI returned empty response content.");
      }
      return content;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if retryable
      const isRetryable =
        lastError.message.includes("429") ||
        lastError.message.includes("500") ||
        lastError.message.includes("502") ||
        lastError.message.includes("503") ||
        lastError.message.includes("timeout") ||
        lastError.message.includes("ECONNRESET");

      if (!isRetryable || attempt === MAX_RETRIES - 1) {
        break;
      }

      const delayMs = BASE_DELAY_MS * Math.pow(2, attempt) + Math.random() * 500;
      console.warn(
        `LLM call failed (attempt ${attempt + 1}/${MAX_RETRIES}), retrying in ${Math.round(delayMs)}ms: ${lastError.message}`
      );
      await sleep(delayMs);
    }
  }

  throw new Error(`LLM call failed after ${MAX_RETRIES} attempts: ${lastError?.message ?? "Unknown error"}`);
}

/**
 * Generate long-form SEO content using GPT-4o.
 */
export async function generateContent(systemPrompt: string, userPrompt: string): Promise<string> {
  return callLLM({
    role: "content",
    systemPrompt,
    userPrompt,
    temperature: 0.75,
    maxTokens: 4096,
  });
}

/**
 * Humanize content using GPT-4o-mini for cost efficiency.
 */
export async function humanizeContent(systemPrompt: string, content: string): Promise<string> {
  return callLLM({
    role: "humanizer",
    systemPrompt,
    userPrompt: content,
    temperature: 0.8,
    maxTokens: 4096,
  });
}

/**
 * Research/keyword analysis using GPT-4o-mini.
 */
export async function researchQuery(systemPrompt: string, query: string): Promise<string> {
  return callLLM({
    role: "research",
    systemPrompt,
    userPrompt: query,
    temperature: 0.3,
    maxTokens: 2048,
  });
}
