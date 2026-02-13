/**
 * Centralized LLM client with retry logic, exponential backoff,
 * and support for multiple OpenAI-compatible providers.
 *
 * Supports:
 * - OpenAI (OPENAI_API_KEY)
 * - NVIDIA (NVIDIA_API_KEY) - https://integrate.api.nvidia.com/v1
 * - OpenRouter (OPENROUTER_API_KEY) - https://openrouter.ai/api/v1
 */
import OpenAI from "openai";

export type LLMRole = "content" | "humanizer" | "research";
export type LLMProvider = "openai" | "nvidia" | "openrouter";

const OPENAI_MODEL_MAP: Record<LLMRole, string> = {
  content: "gpt-4o",
  humanizer: "gpt-4o-mini",
  research: "gpt-4o-mini",
};

const NVIDIA_MODEL_MAP: Record<LLMRole, string> = {
  content: "meta/llama-3.3-70b-instruct",
  humanizer: "meta/llama-3.1-8b-instruct",
  research: "meta/llama-3.1-8b-instruct",
};

const OPENROUTER_MODEL_MAP: Record<LLMRole, string> = {
  content: "anthropic/claude-3.5-sonnet",
  humanizer: "anthropic/claude-3.5-haiku",
  research: "anthropic/claude-3.5-haiku",
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

interface ProviderConfig {
  client: OpenAI;
  provider: LLMProvider;
}

/**
 * Auto-detect available LLM provider.
 * Priority: NVIDIA → OpenRouter → OpenAI
 */
function detectProvider(): ProviderConfig {
  const nvidiaKey = process.env.NVIDIA_API_KEY;
  if (nvidiaKey) {
    console.log("[LLM] Using NVIDIA provider");
    return {
      client: new OpenAI({
        apiKey: nvidiaKey,
        baseURL: "https://integrate.api.nvidia.com/v1",
      }),
      provider: "nvidia",
    };
  }

  const openrouterKey = process.env.OPENROUTER_API_KEY;
  if (openrouterKey) {
    console.log("[LLM] Using OpenRouter provider");
    return {
      client: new OpenAI({
        apiKey: openrouterKey,
        baseURL: "https://openrouter.ai/api/v1",
      }),
      provider: "openrouter",
    };
  }

  const openaiKey = process.env.OPENAI_API_KEY;
  if (openaiKey) {
    console.log("[LLM] Using OpenAI provider");
    return {
      client: new OpenAI({ apiKey: openaiKey }),
      provider: "openai",
    };
  }

  throw new Error(
    "No LLM API key available. Set NVIDIA_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY."
  );
}

/**
 * Check if any LLM provider key is available.
 */
export function hasLlmProvider(): boolean {
  return !!(
    process.env.NVIDIA_API_KEY ||
    process.env.OPENROUTER_API_KEY ||
    process.env.OPENAI_API_KEY
  );
}

/**
 * Get available provider names.
 */
export function getAvailableProviders(): LLMProvider[] {
  const providers: LLMProvider[] = [];
  if (process.env.NVIDIA_API_KEY) providers.push("nvidia");
  if (process.env.OPENROUTER_API_KEY) providers.push("openrouter");
  if (process.env.OPENAI_API_KEY) providers.push("openai");
  return providers;
}

function getModelForRole(provider: LLMProvider, role: LLMRole): string {
  const envModel = process.env.OPENAI_MODEL;
  if (envModel && provider === "openai") return envModel;
  
  switch (provider) {
    case "nvidia":
      return NVIDIA_MODEL_MAP[role];
    case "openrouter":
      return OPENROUTER_MODEL_MAP[role];
    case "openai":
    default:
      return OPENAI_MODEL_MAP[role];
  }
}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Call LLM with exponential backoff retry.
 */
export async function callLLM(options: LLMCallOptions): Promise<string> {
  const { client, provider } = detectProvider();
  const model = getModelForRole(provider, options.role);
  console.log(`[LLM] Using ${provider} / ${model} for ${options.role}`);

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
        throw new Error("LLM returned empty response content.");
      }
      return content;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

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

  throw new Error(
    `LLM call failed after ${MAX_RETRIES} attempts: ${lastError?.message ?? "Unknown error"}`
  );
}

/**
 * Generate long-form SEO content.
 */
export async function generateContent(
  systemPrompt: string,
  userPrompt: string
): Promise<string> {
  return callLLM({
    role: "content",
    systemPrompt,
    userPrompt,
    temperature: 0.75,
    maxTokens: 4096,
  });
}

/**
 * Humanize content using cost-efficient model.
 */
export async function humanizeContent(
  systemPrompt: string,
  content: string
): Promise<string> {
  return callLLM({
    role: "humanizer",
    systemPrompt,
    userPrompt: content,
    temperature: 0.8,
    maxTokens: 4096,
  });
}

/**
 * Research/keyword analysis using efficient model.
 */
export async function researchQuery(
  systemPrompt: string,
  query: string
): Promise<string> {
  return callLLM({
    role: "research",
    systemPrompt,
    userPrompt: query,
    temperature: 0.3,
    maxTokens: 2048,
  });
}
