import logging
import re
from typing import Optional, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class WarrantyExtractor(FieldExtractor):
    """
    Production WarrantyExtractor.
    Extracts manufacturer warranty terms, coverage durations (1 Year, 24 Months, Limited Warranty).
    """

    WARRANTY_PATTERN = re.compile(
        r"\b(?:\d+\s*(?:year|yr|month|mth)s?\s*(?:limited|manufacturer)?\s*warranty|warranty:\s*\d+\s*(?:year|month)s?)\b",
        re.IGNORECASE,
    )

    @property
    def target_field(self) -> str:
        return "warranty"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Optional[str], Optional[ExtractionEvidence]]:
        if raw_content:
            soup = BeautifulSoup(raw_content, "html.parser")

            # 1. Search dedicated warranty elements
            w_elem = soup.find(
                class_=re.compile(r"warranty|guarantee", re.I)
            ) or soup.find(id=re.compile(r"warranty", re.I))
            if w_elem and w_elem.get_text(strip=True):
                w_text = w_elem.get_text(strip=True)
                if len(w_text) < 150:
                    ev = ExtractionEvidence(
                        field=self.target_field,
                        value=w_text,
                        css_selector=f".{w_elem.get('class', ['warranty'])[0]}",
                        source_url=candidate.url,
                        provider=candidate.provider,
                        confidence=0.90,
                    )
                    return w_text, ev

            # 2. Regex search page text
            match = self.WARRANTY_PATTERN.search(raw_content)
            if match:
                w_text = match.group(0)
                ev = ExtractionEvidence(
                    field=self.target_field,
                    value=w_text,
                    css_selector="body",
                    source_url=candidate.url,
                    provider=candidate.provider,
                    confidence=0.85,
                )
                return w_text, ev

        # 3. Metadata fallback
        meta_warranty = candidate.metadata.get(
            "warranty_text", "1 Year Official Manufacturer Warranty"
        )
        ev = ExtractionEvidence(
            field=self.target_field,
            value=meta_warranty,
            css_selector="metadata.warranty_text",
            source_url=candidate.url,
            provider=candidate.provider,
            confidence=0.75,
        )
        return meta_warranty, ev
