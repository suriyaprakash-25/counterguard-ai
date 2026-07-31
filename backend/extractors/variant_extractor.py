import logging
import re
from typing import List, Optional, Set, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class VariantExtractor(FieldExtractor):
    """
    Production VariantExtractor.
    Extracts available color, storage, RAM, size, and edition variants from DOM elements and metadata.
    """

    COLOR_KEYWORDS = {
        "black",
        "white",
        "gray",
        "grey",
        "silver",
        "gold",
        "blue",
        "red",
        "green",
        "purple",
        "pink",
        "yellow",
        "orange",
    }
    STORAGE_PATTERN = re.compile(r"\b\d+\s*(?:GB|TB|MB)\b", re.IGNORECASE)

    @property
    def target_field(self) -> str:
        return "variants"

    def extract_field(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[List[str], Optional[ExtractionEvidence]]:
        seen_variants: Set[str] = set()
        collected_variants: List[str] = []

        if raw_content:
            soup = BeautifulSoup(raw_content, "html.parser")

            # 1. Swatch options / Select dropdowns
            swatches = soup.find_all(
                class_=re.compile(r"swatch|variant|color|size|option", re.I)
            )
            for s in swatches:
                text = s.get_text(strip=True)
                if text and len(text) < 35 and text.lower() not in seen_variants:
                    seen_variants.add(text.lower())
                    collected_variants.append(text)

            # 2. Extract storage specs (e.g. 128GB, 256GB, 512GB)
            storage_matches = self.STORAGE_PATTERN.findall(raw_content)
            for sm in storage_matches:
                clean_sm = sm.upper().replace(" ", "")
                if clean_sm not in seen_variants:
                    seen_variants.add(clean_sm.lower())
                    collected_variants.append(clean_sm)

        # Candidate metadata fallback
        meta_variants = candidate.metadata.get("variants", [])
        for mv in meta_variants:
            if isinstance(mv, str) and mv.lower() not in seen_variants:
                seen_variants.add(mv.lower())
                collected_variants.append(mv)

        evidence = None
        if collected_variants:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=collected_variants,
                css_selector=".swatch-option, .variant-selector, select option",
                xpath="//div[contains(@class, 'variant')]",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=0.88 if len(collected_variants) > 1 else 0.80,
            )

        return collected_variants, evidence
