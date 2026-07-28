/**
 * Frontend Target Normalization Utility
 *
 * Mirrors the backend TargetNormalizationService for client-side display.
 * Used as a fallback when `display_title` is not provided by the API
 * (backward compatibility for older investigation records).
 */

const TRACKING_PARAMS = new Set([
  'ref', 'ref_', 'crid', 'sprefix', 'qid', 'sr', 'th', 'psc',
  'pf_rd_r', 'pf_rd_p', 'pf_rd_s', 'pf_rd_t', 'pf_rd_i',
  'pd_rd_r', 'pd_rd_w', 'pd_rd_wg',
  'linkcode', 'linkid', 'camp', 'creative', 'creativeasin',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'gclid', 'fbclid', 'msclkid', '_ga', '_gl',
  'sessionid', 'session_id', 's', 'cmpid', 'tag',
  'hash', '_trkparms', '_trksid', 'nma', 'si', 'o', 'pi', 'iid',
]);

function decodeToken(text: string): string {
  try {
    return decodeURIComponent(text.replace(/\+/g, ' ')).trim();
  } catch {
    return text.replace(/\+/g, ' ').trim();
  }
}

function sanitizeUrl(rawUrl: string): string {
  if (!rawUrl || (!rawUrl.startsWith('http://') && !rawUrl.startsWith('https://'))) {
    return rawUrl;
  }
  try {
    const url = new URL(rawUrl);
    const keysToDelete: string[] = [];
    url.searchParams.forEach((_val, key) => {
      if (TRACKING_PARAMS.has(key.toLowerCase())) {
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach(k => url.searchParams.delete(k));
    return url.toString();
  } catch {
    return rawUrl;
  }
}

export interface NormalizationResult {
  displayTitle: string;
  cleanUrl: string;
  originalTarget: string;
}

export function normalizeTarget(
  rawTarget: string,
  brandHint?: string,
  productHint?: string,
): NormalizationResult {
  const target = (rawTarget || '').trim();
  const cleanUrl = sanitizeUrl(target);

  // 1. search:// protocol
  if (target.startsWith('search://')) {
    const rest = target.slice('search://'.length);
    const [b = '', p = ''] = rest.split('/', 2);
    const brand = decodeToken(b) || brandHint || 'Brand';
    const prod = decodeToken(p) || productHint || 'Product';
    return {
      displayTitle: `${toTitleCase(brand)} ${toTitleCase(prod)} Assessment`,
      cleanUrl,
      originalTarget: target,
    };
  }

  // 2. HTTP/HTTPS URLs
  if (target.startsWith('http://') || target.startsWith('https://')) {
    let url: URL;
    try {
      url = new URL(target);
    } catch {
      return { displayTitle: target, cleanUrl, originalTarget: target };
    }

    const domain = url.hostname.replace(/^www\./, '').toLowerCase();
    const path = url.pathname;

    // 2a. Search pages (Amazon /s?k=, Flipkart /search?q=, eBay ?_nkw=, Walmart ?q=)
    const searchKeys = ['k', 'keywords', 'q', '_nkw', 'st', 'query'];
    let searchQ = '';
    for (const key of searchKeys) {
      const val = url.searchParams.get(key);
      if (val) { searchQ = val; break; }
    }
    // Fallback regex scan (catches pre-decoded params in the raw string)
    if (!searchQ) {
      const m = rawTarget.match(/[?&](?:k|keywords|q|_nkw|st|query)=([^&]+)/i);
      if (m) searchQ = m[1];
    }
    if (searchQ) {
      return {
        displayTitle: `${toTitleCase(decodeToken(searchQ))} Assessment`,
        cleanUrl,
        originalTarget: target,
      };
    }

    // 2b. Amazon product page /dp/ASIN or /gp/product/ASIN
    const asinMatch = path.match(/\/(?:dp|gp\/product)\/([A-Z0-9]{10})/i);
    if (asinMatch) {
      const asin = asinMatch[1].toUpperCase();
      // Extract readable slug before /dp/
      const slugMatch = path.match(/\/([^/]+)\/(?:dp|gp)/i);
      if (slugMatch) {
        const slug = decodeToken(slugMatch[1]).replace(/-/g, ' ').trim();
        if (slug.length > 4 && !/^[A-Z0-9]{10}$/i.test(slug)) {
          return { displayTitle: toTitleCase(slug), cleanUrl, originalTarget: target };
        }
      }
      if (brandHint && productHint) {
        return {
          displayTitle: `${toTitleCase(brandHint)} ${toTitleCase(productHint)}`,
          cleanUrl,
          originalTarget: target,
        };
      }
      return {
        displayTitle: `Amazon Product Listing (${asin})`,
        cleanUrl,
        originalTarget: target,
      };
    }

    // 2c. Flipkart product /p/ segment
    if (domain.includes('flipkart')) {
      const flipMatch = path.match(/\/([^/]+)\/p\//);
      if (flipMatch) {
        return {
          displayTitle: toTitleCase(flipMatch[1].replace(/-/g, ' ')),
          cleanUrl,
          originalTarget: target,
        };
      }
    }

    // 2d. eBay item /itm/
    if (domain.includes('ebay')) {
      const itemMatch = path.match(/\/itm\/([^/?]+)/);
      if (itemMatch) {
        return {
          displayTitle: toTitleCase(itemMatch[1].replace(/-/g, ' ')),
          cleanUrl,
          originalTarget: target,
        };
      }
    }

    // 2e. Seller store URLs
    const sellerMatch = path.match(/\/(?:usr|seller|str|shops?|storefront)\/([^/?&]+)/i)
      || target.match(/[?&]seller=([^&]+)/i);
    if (sellerMatch) {
      const sellerName = decodeToken(sellerMatch[1]).replace(/-/g, ' ');
      return {
        displayTitle: `Seller Investigation – ${sellerName}`,
        cleanUrl,
        originalTarget: target,
      };
    }

    // 2f. Brand + product hints
    if (brandHint && productHint) {
      return {
        displayTitle: `${toTitleCase(brandHint)} ${toTitleCase(productHint)}`,
        cleanUrl,
        originalTarget: target,
      };
    }

    // 2g. Generic domain fallback
    return {
      displayTitle: `Domain Investigation – ${domain}`,
      cleanUrl,
      originalTarget: target,
    };
  }

  // 3. Non-URL targets
  const clean = decodeToken(target);

  // ASIN pattern
  if (/^[AB][A-Z0-9]{9}$/i.test(clean)) {
    return {
      displayTitle: `ASIN Target – ${clean.toUpperCase()}`,
      cleanUrl,
      originalTarget: target,
    };
  }

  // Plain domain
  if (/^[a-z0-9-]+\.[a-z]{2,}$/i.test(clean)) {
    return {
      displayTitle: `Domain Investigation – ${clean.toLowerCase()}`,
      cleanUrl,
      originalTarget: target,
    };
  }

  if (brandHint && productHint) {
    return {
      displayTitle: `${toTitleCase(brandHint)} ${toTitleCase(productHint)} Assessment`,
      cleanUrl,
      originalTarget: target,
    };
  }

  let title = toTitleCase(clean);
  if (!/assessment|investigation$/i.test(title)) {
    title = `${title} Assessment`;
  }
  return { displayTitle: title, cleanUrl, originalTarget: target };
}

function toTitleCase(str: string): string {
  return str.replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase());
}

/**
 * Resolve the best available display name for an investigation DTO.
 * Priority: backend display_title → report product name → frontend normalization fallback.
 */
export function resolveInvestigationTitle(dto: any): string {
  // 1. Backend already normalized it
  if (dto.display_title && !isRawUrl(dto.display_title)) {
    return dto.display_title;
  }

  // 2. Report has a product name
  const product = dto.product || dto.report?.product;
  if (product && product.length > 2 && !isRawUrl(product)) {
    return `${product} Assessment`;
  }

  // 3. Frontend-side normalization of the listing URL
  const rawTarget = dto.listing_url || dto.target_value || dto.name || '';
  if (rawTarget) {
    const result = normalizeTarget(rawTarget);
    if (!isRawUrl(result.displayTitle)) {
      return result.displayTitle;
    }
  }

  // 4. Last resort: short ID
  return `Investigation ${(dto.id || '').substring(0, 8)}`;
}

function isRawUrl(text: string): boolean {
  if (!text) return false;
  // Looks like a URL path with query parameters
  return text.includes('?') || text.startsWith('http') || text.startsWith('s?k=');
}
