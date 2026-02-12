import { readFile } from "node:fs/promises";
import path from "node:path";
import yaml from "js-yaml";
import { z } from "zod";

const platformSchema = z.literal("react-netlify");

const frequencySchema = z.enum(["daily", "weekly", "2x-weekly", "monthly"]);

export const clientConfigSchema = z.object({
  client: z.object({
    name: z.string().min(1),
    slug: z.string().min(2).regex(/^[a-z0-9-]+$/),
    domain: z.string().min(3),
    platform: platformSchema,
    repo: z.string().min(3),
    contentDir: z.string().min(1),
  }),
  audience: z.object({
    primary: z.string().min(2),
    secondary: z.string().min(2),
    language: z.array(z.string().min(2)).min(1),
  }),
  keywords: z.object({
    primary: z.array(z.string().min(2)).min(1),
    location: z.array(z.string().min(2)).default([]),
    product: z.array(z.string().min(2)).default([]),
  }),
  content: z.object({
    locationPages: z.object({
      enabled: z.boolean(),
      towns: z.array(z.string().min(1)).default([]),
    }),
    productPages: z.object({
      enabled: z.boolean(),
      categories: z.array(z.string().min(1)).default([]),
    }),
    marketReports: z.object({
      enabled: z.boolean(),
      frequency: frequencySchema,
    }),
    blogPosts: z.object({
      enabled: z.boolean(),
      frequency: frequencySchema,
    }),
  }),
  tone: z.object({
    voice: z.string().min(2),
    avoid: z.array(z.string().min(2)).default([]),
  }),
});

export type ClientConfig = z.infer<typeof clientConfigSchema>;

export async function loadClientConfig(clientSlug: string): Promise<ClientConfig> {
  const configPath = path.resolve(process.cwd(), "src", "config", "clients", `${clientSlug}.yaml`);

  try {
    const raw = await readFile(configPath, "utf-8");
    const parsedYaml = yaml.load(raw);
    return clientConfigSchema.parse(parsedYaml);
  } catch (error) {
    const reason = error instanceof Error ? error.message : "Unknown config error";
    throw new Error(`Failed to load client config for '${clientSlug}' at ${configPath}: ${reason}`);
  }
}
