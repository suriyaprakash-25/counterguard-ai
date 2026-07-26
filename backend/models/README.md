# Models Layer (SQLAlchemy 2.0 ORM Entities)

This package defines the relational database models for CounterGuard using **SQLAlchemy 2.0** Declarative Mapped attributes (`Mapped` and `mapped_column`).

## Entities

1. **`InvestigationModel` (`investigations` table)**
   - Tracks each investigation execution, target listing URL, marketplace, execution status, and timestamps.
   - Serves as the primary parent entity in relational cascades.

2. **`EvidenceModel` (`evidence` table)**
   - Stores granular multi-agent findings, cross-query logs, and timeline events generated during an investigation.
   - Linked via foreign key to `investigations.id` with cascading deletions.

3. **`ReportModel` (`reports` table)**
   - Stores the complete synthesized assessment findings, risk score, and AI reasoning.
   - Features helper methods (`to_pydantic()` and `from_pydantic()`) for seamless translation to/from domain Pydantic schemas without leaking DB primitives into service layers.

## Compatibility Notice

These entities are designed to work across SQLite and PostgreSQL natively, utilizing standard database data types (`String`, `Text`, `Float`, `Integer`, `DateTime`) and serializing complex dictionaries/lists into standardized JSON text fields.