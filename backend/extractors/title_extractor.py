import logging
import re
from typing import Optional, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class TitleExtractor(FieldExtractor):
    """
    Production TitleExtractor.
    Extracts product titles using confidence-scored hierarchy:
      1. OpenGraph / Twitter meta tags (og:title, twitter:title) [0.95]
      2. HTML H1 element (h1.product-title, h1) [0.92]
      3. HTML <title> tag [0.85]
      4. Candidate metadata fallback [0.80]
    """

    @property
    def target_field(self) -> str:
        return "title"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        if not raw_content:
            title_val = candidate.title or "Unknown Product Title"
            ev = ExtractionEvidence(
                field=self.target_field,
                value=title_val,
                css_selector="metadata.title",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=candidate.confidence,
            )
            return title_val, ev

        soup = BeautifulSoup(raw_content, "html.parser")

        # 1. Check OpenGraph / Meta title
        og_title = (
            soup.find("meta", property="og:title")
            or soup.find("meta", attrs={"name": "og:title"})
            or soup.find("meta", attrs={"name": "twitter:title"})
        )
        if og_title and og_title.get("content"):
            val = og_title["content"].strip()
            if len(val) > 2:
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=val,
                    css_selector="meta[property='og:title']",
                    xpath="//meta[@property='og:title']/@content",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=0.95,
                )
                return val, ev

        # 2. Check H1 element
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            val = h1.get_text(strip=True)
            if len(val) > 2:
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=val,
                    css_selector="h1",
                    xpath="//h1",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=0.92,
                )
                return val, ev

        # 3. Check HTML <title> tag
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            raw_t = title_tag.get_text(strip=True)
            # Strip site branding suffix (e.g. "Product Name | Official Store")
            clean_t = re.split(r"[|\-–—]", raw_t)[0].strip()
            if len(clean_t) > 2:
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=clean_t,
                    css_selector="title",
                    xpath="//title",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=0.85,
                )
                return clean_t, ev

        # 4. Fallback candidate title
        fallback_val = candidate.title or "Unknown Product Title"
        ev = ExtractionEvidence(
            field=self.target_field,
            value=fallback_val,
            css_selector="metadata.title",
            source_url=candidate.url,
            provider=candidate.provider,
            confidence=0.80,
        )
        return fallback_val, ev
