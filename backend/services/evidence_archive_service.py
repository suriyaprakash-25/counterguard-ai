"""
evidence_archive_service.py — Feature 4: Raw Evidence Archive Service
Hashes, compresses, and archives raw HTML/JSON response payloads with SHA-256 checksums and SQLite indexing.
"""
import gzip
import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.database.engine import get_session_maker
from backend.models.monitoring import RawEvidenceArchiveModel

logger = logging.getLogger("counterguard.evidence_archive_service")

ARCHIVE_DIR = os.path.abspath("./evidence_archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)


class EvidenceArchiveService:
    """
    Raw Evidence Archive Service.
    Cryptographically hashes (SHA-256) and stores raw HTTP response payloads for forensic evidence auditing.
    """

    def _get_session(self) -> Session:
        return get_session_maker()()

    def archive_evidence(
        self,
        evidence_id: str,
        marketplace: str,
        source_url: str,
        raw_payload: str,
        http_status: int = 200,
        content_type: str = "text/html",
    ) -> Dict[str, Any]:
        """Compress, hash, and archive raw response payload to disk and SQLite index."""
        now_iso = datetime.utcnow().isoformat()
        content_bytes = raw_payload.encode("utf-8")
        response_hash = hashlib.sha256(content_bytes).hexdigest()

        # Save compressed payload file
        file_name = f"{response_hash[:16]}_{int(datetime.utcnow().timestamp())}.json.gz"
        file_path = os.path.join(ARCHIVE_DIR, file_name)

        compressed_data = gzip.compress(content_bytes)
        with open(file_path, "wb") as f:
            f.write(compressed_data)

        session = self._get_session()
        try:
            record = RawEvidenceArchiveModel(
                id=f"arc-{response_hash[:12]}",
                evidence_id=evidence_id,
                marketplace=marketplace,
                source_url=source_url,
                http_status=http_status,
                response_hash=response_hash,
                parser_version="v1.2.0",
                retrieval_timestamp=now_iso,
                content_type=content_type,
                compressed_size_bytes=len(compressed_data),
                storage_path=file_path,
                payload_json=json.dumps(
                    {
                        "hash_algorithm": "SHA-256",
                        "size_uncompressed": len(content_bytes),
                    }
                ),
            )
            session.merge(record)
            session.commit()
            logger.info(
                f"[EvidenceArchiveService] Archived raw evidence for '{evidence_id}' (Hash: {response_hash[:10]})."
            )
            return {
                "archive_id": record.id,
                "response_hash": response_hash,
                "storage_path": file_path,
                "compressed_bytes": len(compressed_data),
                "timestamp": now_iso,
            }
        except Exception as e:
            session.rollback()
            logger.error(
                f"[EvidenceArchiveService] Failed to archive evidence '{evidence_id}': {e}"
            )
            raise
        finally:
            session.close()

    def get_archive(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """Fetch raw evidence metadata from SQLite index."""
        session = self._get_session()
        try:
            r = (
                session.query(RawEvidenceArchiveModel)
                .filter(RawEvidenceArchiveModel.id == archive_id)
                .first()
            )
            if not r:
                return None
            return {
                "archive_id": r.id,
                "evidence_id": r.evidence_id,
                "marketplace": r.marketplace,
                "source_url": r.source_url,
                "http_status": r.http_status,
                "response_hash": r.response_hash,
                "parser_version": r.parser_version,
                "retrieval_timestamp": r.retrieval_timestamp,
                "storage_path": r.storage_path,
                "compressed_size_bytes": r.compressed_size_bytes,
            }
        finally:
            session.close()

    def get_all_archives(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent raw evidence archive entries."""
        session = self._get_session()
        try:
            records = (
                session.query(RawEvidenceArchiveModel)
                .order_by(RawEvidenceArchiveModel.retrieval_timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "archive_id": r.id,
                    "evidence_id": r.evidence_id,
                    "marketplace": r.marketplace,
                    "source_url": r.source_url,
                    "http_status": r.http_status,
                    "response_hash": r.response_hash,
                    "parser_version": r.parser_version,
                    "retrieval_timestamp": r.retrieval_timestamp,
                    "compressed_size_bytes": r.compressed_size_bytes,
                }
                for r in records
            ]
        except Exception:
            return []
        finally:
            session.close()


evidence_archive_service = EvidenceArchiveService()
