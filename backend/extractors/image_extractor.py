import logging
import urllib.parse
from typing import List, Optional, Set, Tuple

from bs4 import BeautifulSoup

from backend.extractors.base_extractor import FieldExtractor
from backend.schemas.discovery_engine import SourceCandidate
from backend.schemas.extraction_evidence import ExtractionEvidence

logger = logging.getLogger(__name__)


class ImageExtractor(FieldExtractor):
    """
    Production ImageExtractor.
    Collects hero image, gallery images, and high-resolution zoom images while filtering out icons/pixel trackers.
    """

    @property
    def target_field(self) -> str:
        return "images"

    def is_valid_product_image(self, url: str) -> bool:
        if not url or len(url) < 8:
            return False
        clean = url.lower()
        if any(
            bad in clean
            for bad in (
                ".svg",
                ".gif",
                "logo",
                "icon",
                "avatar",
                "badge",
                "pixel",
                "tracker",
                "spinner",
                "loader",
            )
        ):
            return False
        return True

    def make_absolute(self, src: str, base_url: str) -> str:
        if not src:
            return ""
        if src.startswith("//"):
            return "https:" + src
        if src.startswith("http://") or src.startswith("https://"):
            return src
        return urllib.parse.urljoin(base_url, src)

    def extract_field(  # noqa: C901
        self, candidate: SourceCandidate, raw_content: str = ""
    ) -> Tuple[List[str], Optional[ExtractionEvidence]]:
        seen_images: Set[str] = set()
        collected_images: List[str] = []

        if raw_content:
            soup = BeautifulSoup(raw_content, "html.parser")

            # 1. OpenGraph hero image
            og_img = soup.find("meta", property="og:image") or soup.find(
                "meta", attrs={"name": "twitter:image"}
            )
            if og_img and og_img.get("content"):
                abs_url = self.make_absolute(og_img["content"].strip(), candidate.url)
                if self.is_valid_product_image(abs_url) and abs_url not in seen_images:
                    seen_images.add(abs_url)
                    collected_images.append(abs_url)

            # 2. Hero & Gallery images from DOM
            img_tags = soup.find_all("img")
            for img in img_tags:
                src = img.get("data-zoom") or img.get("data-src") or img.get("src")
                if src:
                    abs_url = self.make_absolute(src.strip(), candidate.url)
                    if (
                        self.is_valid_product_image(abs_url)
                        and abs_url not in seen_images
                    ):
                        seen_images.add(abs_url)
                        collected_images.append(abs_url)
                        if len(collected_images) >= 10:
                            break

        # Metadata fallback images
        meta_images = candidate.metadata.get("official_images", [])
        for m_img in meta_images:
            abs_url = self.make_absolute(m_img, candidate.url)
            if self.is_valid_product_image(abs_url) and abs_url not in seen_images:
                seen_images.add(abs_url)
                collected_images.append(abs_url)

        evidence = None
        if collected_images:
            evidence = ExtractionEvidence(
                field=self.target_field,
                value=collected_images,
                css_selector="meta[property='og:image'], img.gallery-image",
                xpath="//meta[@property='og:image']/@content | //img",
                source_url=candidate.url,
                provider=candidate.provider,
                confidence=0.92 if len(collected_images) > 1 else 0.85,
            )

        return collected_images, evidence
