import logging
import re
from typing import Any, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class SpecificationExtractor(FieldExtractor):
    """
    Production SpecificationExtractor.
    Parses HTML specification tables (<table>), definition lists (<dl><dt><dd>), and structured spec rows.
    """

    @property
    def target_field(self) -> str:
        return "specifications"

    def clean_key(self, raw_k: str) -> str:
        clean = re.sub(r"[^\w\s]", "", raw_k).strip().lower()
        return clean.replace(" ", "_")

    def extract_field(  # noqa: C901
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[Dict[str, Any], Optional[ExtractionEvidence]]:
        extracted_specs: Dict[str, Any] = {}

        if raw_content:
            soup = BeautifulSoup(raw_content, "html.parser")

            # 1. Parse HTML <table> elements
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["th", "td"])
                    if len(cols) >= 2:
                        k_text = cols[0].get_text(strip=True)
                        v_text = cols[1].get_text(strip=True)
                        if k_text and v_text and len(k_text) < 50:
                            extracted_specs[self.clean_key(k_text)] = v_text

            # 2. Parse Definition Lists (<dl><dt><dd>)
            dl_tags = soup.find_all("dl")
            for dl in dl_tags:
                dts = dl.find_all("dt")
                dds = dl.find_all("dd")
                for dt, dd in zip(dts, dds):
                    k_text = dt.get_text(strip=True)
                    v_text = dd.get_text(strip=True)
                    if k_text and v_text and len(k_text) < 50:
                        extracted_specs[self.clean_key(k_text)] = v_text

            # 3. Parse key-value spec rows (<div class="spec-item"><span class="label">...</span><span class="val">...</span></div>)
            spec_rows = soup.find_all(class_=re.compile(r"spec|feature|tech", re.I))
            for row in spec_rows:
                labels = row.find_all(class_=re.compile(r"label|name|title|key", re.I))
                values = row.find_all(class_=re.compile(r"val|value|desc|detail", re.I))
                if labels and values:
                    k_text = labels[0].get_text(strip=True)
                    v_text = values[0].get_text(strip=True)
                    if (
                        k_text
                        and v_text
                        and len(k_text) < 50
                        and self.clean_key(k_text) not in extracted_specs
                    ):
                        extracted_specs[self.clean_key(k_text)] = v_text

        # Merge candidate metadata specs
        meta_specs = candidate.metadata.get("specifications", {})
        for mk, mv in meta_specs.items():
            ck = self.clean_key(mk)
            if ck not in extracted_specs:
                extracted_specs[ck] = str(mv)

        evidence = None
        if extracted_specs:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=extracted_specs,
                css_selector="table, dl, .spec-item",
                xpath="//table | //dl",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=0.90 if len(extracted_specs) > 2 else 0.80,
            )

        return extracted_specs, evidence
