import re
import urllib.parse
from typing import Dict, Optional


class TargetNormalizationService:
    """
    Dedicated Target Normalization Service for CounterGuard.

    Normalizes raw URLs, marketplace search parameters, ASINs, seller URLs,
    and free-text targets into clean, human-readable investigation display titles.

    Returns three values:
      - display_title   : Clean, readable investigation name for ALL UI surfaces
      - clean_url       : Original URL with tracking/noise parameters stripped
      - original_target : Preserved verbatim original URL for auditing
    """

    # Marketplace-specific tracking & noise parameters to remove
    TRACKING_PARAMS = {
        # Amazon
        "ref",
        "ref_",
        "crid",
        "sprefix",
        "qid",
        "sr",
        "th",
        "psc",
        "pf_rd_r",
        "pf_rd_p",
        "pf_rd_s",
        "pf_rd_t",
        "pf_rd_i",
        "pd_rd_r",
        "pd_rd_w",
        "pd_rd_wg",
        "linkCode",
        "linkId",
        "camp",
        "creative",
        "creativeASIN",
        # eBay
        "hash",
        "_trkparms",
        "_trksid",
        "nma",
        "si",
        "o",
        "pi",
        "iid",
        # General UTM & ad tracking
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
        "msclkid",
        "_ga",
        "_gl",
        # Session / noise
        "sessionid",
        "session_id",
        "s",
        "cmpid",
        "tag",
    }

    @classmethod
    def sanitize_url(cls, raw_url: str) -> str:
        """Return URL with tracking parameters stripped, preserving meaningful params."""
        if not raw_url or not (
            raw_url.startswith("http://") or raw_url.startswith("https://")
        ):
            return raw_url
        try:
            parsed = urllib.parse.urlparse(raw_url)
            query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)
            clean_params = {
                k: v
                for k, v in query_params.items()
                if k.lower() not in cls.TRACKING_PARAMS
            }
            new_query = urllib.parse.urlencode(clean_params, doseq=True)
            clean_parsed = parsed._replace(query=new_query)
            return urllib.parse.urlunparse(clean_parsed)
        except Exception:
            return raw_url

    @classmethod
    def _decode(cls, text: str) -> str:
        """URL-decode and clean a text token: CMF+Buds+2A → CMF Buds 2a."""
        try:
            decoded = urllib.parse.unquote_plus(text)
        except Exception:
            decoded = text
        return decoded.replace("+", " ").strip()

    @classmethod
    def normalize(  # noqa: C901
        cls,
        raw_target: str,
        brand_hint: Optional[str] = None,
        product_hint: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Normalize any target into display_title, clean_url, and original_target.

        Supports:
          - Amazon search URLs  (/s?k=..., /s?keywords=...)
          - Amazon product URLs (/dp/ASIN, /gp/product/ASIN)
          - Flipkart, eBay, Walmart, Best Buy product/seller URLs
          - Brand website domains
          - Seller store URLs   (/usr/, /seller/, /str/)
          - Free-text product names
          - ASINs (B08N5WRWNW)
          - SKUs
          - Domains
          - search:// protocol
        """
        raw_target = (raw_target or "").strip()
        clean_url = cls.sanitize_url(raw_target)

        # ── 1. search:// internal protocol ─────────────────────────────────────
        if raw_target.startswith("search://"):
            parts = raw_target[len("search://") :].split("/", 1)
            b = cls._decode(parts[0]) if parts else (brand_hint or "Brand")
            p = cls._decode(parts[1]) if len(parts) > 1 else (product_hint or "Product")
            b = b or brand_hint or "Brand"
            p = p or product_hint or "Product"
            return {
                "display_title": f"{b.title()} {p.title()} Assessment",
                "clean_url": clean_url,
                "original_target": raw_target,
            }

        # ── 2. HTTP / HTTPS URLs ────────────────────────────────────────────────
        if raw_target.startswith("http://") or raw_target.startswith("https://"):
            parsed = urllib.parse.urlparse(raw_target)
            domain = parsed.netloc.lower().replace("www.", "")
            query_params = urllib.parse.parse_qs(parsed.query)

            # ── 2a. Marketplace search pages ──────────────────────────────────
            # Amazon: /s?k=... or ?keywords=... or /search?q=...
            # Flipkart: /search?q=... eBay: /sch/i.html?_nkw=...
            # Walmart: /search?q=... BestBuy: /site/searchpage.jsp?st=...
            search_key_map = {
                "k": None,  # Amazon
                "keywords": None,  # Amazon
                "q": None,  # Flipkart, Walmart, eBay, generic
                "_nkw": None,  # eBay
                "st": None,  # Best Buy
                "query": None,  # generic
            }
            search_q = ""
            for key in search_key_map:
                if key in query_params:
                    search_q = query_params[key][0]
                    break

            # Also catch inline patterns like "k=cmf+buds" even after clean
            if not search_q:
                for key in ("k", "keywords", "q", "_nkw", "st", "query"):
                    m = re.search(rf"[?&]{key}=([^&]+)", raw_target)
                    if m:
                        search_q = m.group(1)
                        break

            if search_q:
                q_clean = cls._decode(search_q).title()
                return {
                    "display_title": f"{q_clean} Assessment",
                    "clean_url": clean_url,
                    "original_target": raw_target,
                }

            # ── 2b. Amazon product page (/dp/ASIN or /gp/product/ASIN) ────────
            asin_match = re.search(
                r"/(?:dp|gp/product)/([A-Z0-9]{10})", raw_target, re.IGNORECASE
            )
            if asin_match:
                asin = asin_match.group(1).upper()
                # Try path slug before /dp/ e.g. "/Sony-WH-1000XM5-Headphones/dp/"
                slug_match = re.search(
                    r"/([^/]+)/(?:dp|gp)/", raw_target, re.IGNORECASE
                )
                if slug_match:
                    slug = slug_match.group(1).replace("-", " ").strip()
                    if len(slug) > 4 and not re.match(
                        r"^[A-Z0-9]{10}$", slug, re.IGNORECASE
                    ):
                        return {
                            "display_title": slug.title(),
                            "clean_url": clean_url,
                            "original_target": raw_target,
                        }
                if brand_hint and product_hint:
                    return {
                        "display_title": f"{brand_hint.title()} {product_hint.title()}",
                        "clean_url": clean_url,
                        "original_target": raw_target,
                    }
                return {
                    "display_title": f"Amazon Product Listing ({asin})",
                    "clean_url": clean_url,
                    "original_target": raw_target,
                }

            # ── 2c. Flipkart product URL (/p/ segment) ────────────────────────
            if "flipkart" in domain:
                flip_match = re.search(r"/([^/]+)/p/", raw_target)
                if flip_match:
                    name = flip_match.group(1).replace("-", " ").title()
                    return {
                        "display_title": name,
                        "clean_url": clean_url,
                        "original_target": raw_target,
                    }

            # ── 2d. eBay item page (/itm/) ────────────────────────────────────
            if "ebay" in domain:
                item_match = re.search(r"/itm/([^/]+)/", raw_target)
                if item_match:
                    name = item_match.group(1).replace("-", " ").title()
                    return {
                        "display_title": name,
                        "clean_url": clean_url,
                        "original_target": raw_target,
                    }

            # ── 2e. Seller store / profile URL ───────────────────────────────
            seller_match = re.search(
                r"/(?:usr|seller|str|shops?|storefront)/([^/?&]+)",
                raw_target,
                re.IGNORECASE,
            )
            if not seller_match and "seller=" in raw_target:
                seller_match = re.search(r"[?&]seller=([^&]+)", raw_target)
            if seller_match:
                seller_name = (
                    cls._decode(seller_match.group(1)).replace("-", " ").strip()
                )
                return {
                    "display_title": f"Seller Investigation – {seller_name}",
                    "clean_url": clean_url,
                    "original_target": raw_target,
                }

            # ── 2f. Generic product URL path slug extraction ─────────────────
            # E.g. /products/cmf-nothing-buds-c10776306.html, /product/slug, /item/slug
            slug_match = re.search(
                r"/(?:products?|items?|goods|p|pd|detail|listing|buy)/([^/?#]+)",
                raw_target,
                re.IGNORECASE,
            )
            if not slug_match and parsed.path:
                slug_match = re.search(
                    r"/([^/]+-[^/]+(?:\.html?|\.aspx?)?)$", parsed.path, re.IGNORECASE
                )

            if slug_match:
                slug_raw = slug_match.group(1)
                slug = re.sub(
                    r"\.(?:html?|aspx?|php)$", "", slug_raw, flags=re.IGNORECASE
                )
                slug = re.sub(r"-[a-z]?\d{5,}$", "", slug, flags=re.IGNORECASE)
                slug_clean = (
                    cls._decode(slug).replace("-", " ").replace("_", " ").strip()
                )
                if len(slug_clean) > 3 and not slug_clean.isdigit():
                    return {
                        "display_title": slug_clean.title(),
                        "clean_url": clean_url,
                        "original_target": raw_target,
                    }

            # ── 2f. Brand/product hints available ────────────────────────────
            if brand_hint and product_hint:
                return {
                    "display_title": f"{brand_hint.title()} {product_hint.title()}",
                    "clean_url": clean_url,
                    "original_target": raw_target,
                }

            # ── 2g. Generic domain fallback ───────────────────────────────────
            return {
                "display_title": f"Domain Investigation – {domain}",
                "clean_url": clean_url,
                "original_target": raw_target,
            }

        # ── 3. Non-URL targets ──────────────────────────────────────────────────
        clean_text = cls._decode(raw_target)

        # ASIN pattern B08N5WRWNW
        if re.match(r"^[AB][A-Z0-9]{9}$", clean_text, re.IGNORECASE):
            return {
                "display_title": f"ASIN Target – {clean_text.upper()}",
                "clean_url": clean_text,
                "original_target": raw_target,
            }

        # Plain domain (no protocol, has a dot)
        if re.match(r"^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", clean_text):
            return {
                "display_title": f"Domain Investigation – {clean_text.lower()}",
                "clean_url": clean_text,
                "original_target": raw_target,
            }

        # Free-text product name or brand + model
        if brand_hint and product_hint:
            return {
                "display_title": f"{brand_hint.title()} {product_hint.title()} Assessment",
                "clean_url": clean_text,
                "original_target": raw_target,
            }

        # Generic free-text
        title_formatted = clean_text.title()
        if not title_formatted.lower().endswith(("assessment", "investigation")):
            title_formatted = f"{title_formatted} Assessment"
        return {
            "display_title": title_formatted,
            "clean_url": clean_text,
            "original_target": raw_target,
        }
