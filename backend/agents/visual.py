import io
import json
import logging
import os
import urllib.request
from typing import Optional, Tuple

import numpy as np
from PIL import Image

from backend.agents.base import BaseAgent
from backend.agents.registry import AgentRegistry
from backend.constants import Thresholds
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


@AgentRegistry.register("visual")
class VisualForensicsAgent(BaseAgent):
    """
    Visual Forensics Agent.
    Computes image similarity between listing product image and verified golden reference.
    Algorithm: Normalized Perceptual Image Feature Similarity (using PIL & NumPy for fast, zero-dependency execution).
    """

    MANIFEST_PATH = "data/golden_reference/manifest.json"
    DEFAULT_REFERENCE_PATH = "data/golden_reference/sony_wh1000xm5.jpg"

    def __init__(self):
        super().__init__()

    def answer_query(self, question: str, state: InvestigationState) -> str:
        return "VisualForensicsAgent: Perceptual image similarity score generated."

    def run(self, state: InvestigationState) -> dict:
        """
        Execute visual comparison against golden reference image.
        Returns dict with visual_similarity and updated findings if mismatch is detected.
        """
        logger.info("Executing VisualForensicsAgent comparison pipeline")

        scraping_result = state.get("scraping_result")
        listing = (
            scraping_result.listing
            if scraping_result and scraping_result.listing
            else None
        )
        image_url = listing.image_url if listing else None
        product_name = listing.title if listing else "default"

        similarity_score, ref_found = self._compare_listing_image(
            product_name, image_url
        )

        findings_update = []
        if ref_found and similarity_score < Thresholds.VISUAL_SIMILARITY_MIN:
            finding_str = f"Visual Mismatch: Product image differs significantly from verified reference ({similarity_score}% similarity)"
            findings_update.append(finding_str)
            logger.warning(
                f"VisualForensicsAgent detected visual mismatch: {similarity_score}% similarity"
            )
        else:
            logger.info(
                f"VisualForensicsAgent similarity: {similarity_score}% (Threshold: {Thresholds.VISUAL_SIMILARITY_MIN}%)"
            )

        return {
            "visual_similarity": similarity_score,
            "visual_findings": findings_update,
        }

    def _compare_listing_image(
        self, product_name: str, listing_image_url: Optional[str]
    ) -> Tuple[float, bool]:
        """
        Loads golden reference image and listing image, then computes perceptual similarity score (0.0 to 100.0%).
        """
        ref_image = self._load_golden_reference(product_name)
        if ref_image is None:
            logger.warning(
                "No golden reference image found. Returning default similarity 100.0%."
            )
            return 100.0, False

        listing_image = self._load_listing_image(listing_image_url)
        if listing_image is None:
            logger.warning(
                "Could not fetch listing image. Returning default similarity 100.0%."
            )
            return 100.0, False

        similarity = self._compute_perceptual_similarity(ref_image, listing_image)
        return similarity, True

    def _load_golden_reference(self, product_name: str) -> Optional[Image.Image]:
        """Loads golden reference image from manifest mapping or default path."""
        ref_path = self.DEFAULT_REFERENCE_PATH

        if os.path.exists(self.MANIFEST_PATH):
            try:
                with open(self.MANIFEST_PATH, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                key_lower = product_name.lower()
                for k, v in manifest.items():
                    if k.lower() in key_lower or key_lower in k.lower():
                        ref_path = v
                        break
            except Exception as e:
                logger.warning(f"Failed to parse manifest.json: {e}")

        if os.path.exists(ref_path):
            try:
                return Image.open(ref_path).convert("RGB")
            except Exception as e:
                logger.warning(
                    f"Failed to open local golden reference image '{ref_path}': {e}"
                )

        # Fallback to fetching default reference URL if local file missing
        try:
            url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return Image.open(io.BytesIO(resp.read())).convert("RGB")
        except Exception as e:
            logger.warning(f"Failed to download default reference image: {e}")
            return None

    def _load_listing_image(self, image_url: Optional[str]) -> Optional[Image.Image]:
        """Loads listing image from HTTP URL or local file path."""
        if not image_url or not image_url.strip():
            return None

        if os.path.exists(image_url):
            try:
                return Image.open(image_url).convert("RGB")
            except Exception as e:
                logger.warning(f"Failed to open local listing image '{image_url}': {e}")
                return None

        if image_url.startswith("http://") or image_url.startswith("https://"):
            try:
                import ssl

                ctx = ssl._create_unverified_context()
                req = urllib.request.Request(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    return Image.open(io.BytesIO(resp.read())).convert("RGB")
            except Exception as e:
                logger.warning(f"Failed to fetch listing image from '{image_url}': {e}")
                return None

        return None

    def _compute_perceptual_similarity(
        self, img1: Image.Image, img2: Image.Image
    ) -> float:
        """
        Computes Mean Absolute Normalized Perceptual Pixel Feature Similarity (0.0 to 100.0%).
        Using PIL & NumPy for lightweight, fast, zero-dependency execution.
        """
        i1 = img1.convert("RGB").resize((64, 64))
        i2 = img2.convert("RGB").resize((64, 64))

        a1 = np.array(i1, dtype=np.float32)
        a2 = np.array(i2, dtype=np.float32)

        mean_diff = float(np.mean(np.abs(a1 - a2)))
        similarity = max(0.0, min(100.0, 100.0 - (mean_diff / 255.0 * 100.0)))
        return round(similarity, 1)
