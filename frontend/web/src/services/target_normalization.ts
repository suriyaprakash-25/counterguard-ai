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

    // 2c2. Meesho product /slug/p/id segment
    if (domain.includes('meesho')) {
      const meeshoMatch = path.match(/\/([^/]+)\/p\//);
      if (meeshoMatch) {
        let slug = meeshoMatch[1].replace(/@[0-9]+$/, '').replace(/-/g, ' ').trim();
        return {
          displayTitle: toTitleCase(slug),
          cleanUrl,
          originalTarget: target,
        };
      }
    }

    // 2c3. AJIO product /slug/p/id segment
    if (domain.includes('ajio')) {
      const ajioMatch = path.match(/\/([^/]+)\/p\//);
      if (ajioMatch) {
        let slug = ajioMatch[1].replace(/[-_][0-9_]+$/, '').replace(/-/g, ' ').trim();
        return {
          displayTitle: toTitleCase(slug),
          cleanUrl,
          originalTarget: target,
        };
      }
    }

    // 2c4. Myntra product URL /category/brand/slug/id/buy
    if (domain.includes('myntra')) {
      const nonNumParts = path.split('/').filter(p => p && p.toLowerCase() !== 'buy' && !/^\d+$/.test(p));
      if (nonNumParts.length > 0) {
        const slug = nonNumParts[nonNumParts.length - 1].replace(/-/g, ' ').trim();
        return {
          displayTitle: toTitleCase(slug),
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

    // 2f. Generic product URL path slug extraction
    // e.g. /products/cmf-nothing-buds-c10776306.html, /product/slug, /item/slug
    let slugMatch = path.match(/\/(?:products?|items?|goods|p|pd|detail|listing|buy)\/([^/?#]+)/i);
    if (!slugMatch && path) {
      slugMatch = path.match(/\/([^/]+-[^/]+(?:\.html?|\.aspx?)?)$/i);
    }
    if (slugMatch) {
      let slug = slugMatch[1].replace(/\.(?:html?|aspx?|php)$/i, '');
      slug = slug.replace(/-[a-z]?\d{5,}$/i, '');
      const slugClean = decodeToken(slug).replace(/[-_]/g, ' ').trim();
      if (slugClean.length > 3 && !/^\d+$/.test(slugClean)) {
        return {
          displayTitle: toTitleCase(slugClean),
          cleanUrl,
          originalTarget: target,
        };
      }
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
  // 1. Backend display_title
  if (dto.display_title && !isRawUrl(dto.display_title)) {
    return dto.display_title;
  }

  // 2. Direct clean name provided in DTO
  if (dto.name && !isRawUrl(dto.name) && !dto.name.startsWith('search://')) {
    return dto.name;
  }

  // 3. Report has a product name
  const product = dto.product || dto.report?.product;
  if (product && product.length > 2 && !isRawUrl(product)) {
    return `${product} Assessment`;
  }

  // 4. Frontend-side normalization of the listing URL
  const rawTarget = dto.listing_url || dto.target_value || '';
  if (rawTarget) {
    const result = normalizeTarget(rawTarget);
    if (!isRawUrl(result.displayTitle)) {
      return result.displayTitle;
    }
  }

  // 5. Last resort: short ID
  return `Investigation ${(dto.id || '').substring(0, 8)}`;
}

export function canonicalizeProductTitle(title: string): string {
  if (!title) return '';
  const lower = title.toLowerCase().trim();
  const canonicalMap: Record<string, string> = {
    'wh1000xm5': 'Sony WH-1000XM5',
    'wh-1000xm5': 'Sony WH-1000XM5',
    'cmf buds 2a': 'Nothing CMF Buds 2a',
    'cmf buds': 'Nothing CMF Buds',
    'nothing phone 2a': 'Nothing Phone (2a)',
    'iphone 15 pro max': 'Apple iPhone 15 Pro Max',
    'iphone 15 pro': 'Apple iPhone 15 Pro',
    'airpods pro 2': 'Apple AirPods Pro (2nd Gen)',
    'galaxy s25 ultra': 'Samsung Galaxy S25 Ultra',
    'bose qc45': 'Bose QuietComfort 45'
  };

  for (const [key, val] of Object.entries(canonicalMap)) {
    if (lower.includes(key)) return val;
  }

  return title;
}

function isRawUrl(text: string): boolean {
  if (!text) return false;
  // Looks like a URL path with query parameters
  return text.includes('?') || text.startsWith('http') || text.startsWith('s?k=');
}
