export interface MetaTagResult {
  title: string;
  description: string;
}

export function generateMeta(keyword: string, location?: string): MetaTagResult {
  const titleBase = location ? `${keyword} | ${location}` : keyword;
  const title = titleBase.length > 60 ? `${titleBase.slice(0, 57)}...` : titleBase;
  const descriptionRaw = `Explore ${keyword}${location ? ` in ${location}` : ""} with current market context, local insights, and up-to-date product highlights.`;
  const description = descriptionRaw.length > 160 ? `${descriptionRaw.slice(0, 157)}...` : descriptionRaw;

  return { title, description };
}
