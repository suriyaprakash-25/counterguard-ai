import logging
import threading
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RetrievalCache:
    """
    Thread-safe in-memory cache for product retrieval results with TTL expiration.
    Prevents redundant web searches for identical brand/model queries.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RetrievalCache, cls).__new__(cls)
                cls._instance._init_cache()
            return cls._instance

    def _init_cache(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 1800  # 30 Minutes default TTL

    def _make_key(self, brand: str, model: str, region: str = "Global") -> str:
        clean_brand = (brand or "").strip().lower()
        clean_model = (model or "").strip().lower()
        clean_region = (region or "Global").strip().lower()
        return f"cache:{clean_brand}:{clean_model}:{clean_region}"

    def get(self, brand: str, model: str, region: str = "Global") -> Optional[Dict[str, Any]]:
        """
        Retrieve cached product search result if valid and unexpired.
        """
        key = self._make_key(brand, model, region)
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None

            now = time.time()
            if now > entry["expires_at"]:
                logger.info(f"[RetrievalCache] Expired entry for key: {key}")
                del self._cache[key]
                return None

            logger.info(f"[RetrievalCache] CACHE HIT for key: {key}")
            return entry["data"]

    def set(self, brand: str, model: str, data: Dict[str, Any], region: str = "Global", ttl: Optional[int] = None):
        """
        Store product search result in cache with specified TTL.
        """
        key = self._make_key(brand, model, region)
        expire_seconds = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + expire_seconds

        with self._lock:
            self._cache[key] = {
                "data": data,
                "created_at": time.time(),
                "expires_at": expires_at
            }
            logger.info(f"[RetrievalCache] Stored key: {key} (TTL: {expire_seconds}s)")

    def clear(self):
        """
        Clear all cache entries.
        """
        with self._lock:
            self._cache.clear()
