# Worker boundary

P0 uses a bounded, on-demand demo-ingestion endpoint so the evidence workflow
can be tested without a queue. This directory is reserved for scheduled source
adapters after a provider passes the activation checklist in
`docs/DATA_SOURCES.md`.

Do not add a live polling job here until its source credential, rate-limit
handling, idempotency strategy, and preservation of raw source provenance have
been tested.
