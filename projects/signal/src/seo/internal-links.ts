export interface InternalLink {
  text: string;
  href: string;
}

export function suggestInternalLinks(keyword: string, existingUrls: string[]): InternalLink[] {
  return existingUrls.slice(0, 5).map((url) => ({
    text: `Related: ${keyword}`,
    href: url,
  }));
}
