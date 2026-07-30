import logging
import time
from typing import List

from backend.extractors.certification_extractor import CertificationExtractor
from backend.extractors.image_extractor import ImageExtractor
from backend.extractors.price_extractor import PriceExtractor
from backend.extractors.specification_extractor import SpecificationExtractor
from backend.extractors.title_extractor import TitleExtractor
from backend.extractors.variant_extractor import VariantExtractor
from backend.extractors.warranty_extractor import WarrantyExtractor
from backend.providers.extraction.base_provider import ExtractionProvider
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence
from backend.schemas.raw_extraction import RawExtractionResult

logger = logging.getLogger(__name__)


class HTMLExtractionProvider(ExtractionProvider):
    """
    HTMLExtractionProvider (Strategy Provider)

    Delegates DOM HTML parsing to modular field extractors (TitleExtractor, PriceExtractor, ImageExtractor, etc.)
    and aggregates traceable ExtractionEvidence objects.
    """

    def __init__(self):
        self.title_extractor = TitleExtractor()
        self.price_extractor = PriceExtractor()
        self.image_extractor = ImageExtractor()
        self.spec_extractor = SpecificationExtractor()
        self.variant_extractor = VariantExtractor()
        self.warranty_extractor = WarrantyExtractor()
        self.cert_extractor = CertificationExtractor()

    @property
    def provider_name(self) -> str:
        return "HTMLExtractionProvider"

    def supports(self, candidate: SourceCandidate) -> bool:
        return True

    def extract(
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> RawExtractionResult:
        start_time = time.time()
        logger.debug(
            f"[{self.provider_name}] Extracting via modular field extractors from URL '{candidate.url}'."
        )

        evidence_trail: List[ExtractionEvidence] = []

        raw_title, title_ev = self.title_extractor.extract_field(candidate, raw_content)
        if title_ev:
            evidence_trail.append(title_ev)

        raw_price_str, price_ev = self.price_extractor.extract_field(
            candidate, raw_content
        )
        if price_ev:
            evidence_trail.append(price_ev)

        raw_images, image_ev = self.image_extractor.extract_field(
            candidate, raw_content
        )
        if image_ev:
            evidence_trail.append(image_ev)

        raw_specs, spec_ev = self.spec_extractor.extract_field(candidate, raw_content)
        if spec_ev:
            evidence_trail.append(spec_ev)

        variants, var_ev = self.variant_extractor.extract_field(candidate, raw_content)
        if var_ev:
            evidence_trail.append(var_ev)

        raw_warranty, war_ev = self.warranty_extractor.extract_field(
            candidate, raw_content
        )
        if war_ev:
            evidence_trail.append(war_ev)

        certs, cert_ev = self.cert_extractor.extract_field(candidate, raw_content)
        if cert_ev:
            evidence_trail.append(cert_ev)

        brand_name = candidate.metadata.get(
            "brand_key",
            candidate.domain.split(".")[0].capitalize()
            if candidate.domain
            else "Generic Brand",
        )
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

        return RawExtractionResult(
            url=candidate.url,
            provider=self.provider_name,
            raw_title=raw_title,
            raw_brand=brand_name,
            raw_price_str=raw_price_str,
            raw_currency="INR",
            raw_images=raw_images,
            raw_specs=raw_specs,
            raw_warranty=raw_warranty,
            evidence_trail=evidence_trail,
            extraction_method="html",
            extraction_time_ms=elapsed_ms,
            confidence=candidate.confidence,
            metadata={
                "domain": candidate.domain,
                "variants": variants,
                "certifications": certs,
            },
        )
