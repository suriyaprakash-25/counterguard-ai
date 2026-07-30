/**
 * url.ts — Helper utilities for URL parsing & formatting
 */

export function extractDomain(url: string): string {
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export function formatUrlForDisplay(url: string, maxLength: number = 40): string {
  if (!url) return "";
  if (url.length <= maxLength) return url;
  return url.slice(0, maxLength - 3) + "...";
}
