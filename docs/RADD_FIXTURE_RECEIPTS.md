# Offline RADD fixture receipt ledger

This development-only primitive records receipt metadata for explicitly
synthetic RADD-like JSON fixtures. It never makes a network request, receives a
provider credential, stores raw responses or rows, or activates LIVE.
Synthetic fixtures do not establish the format, health, access, coverage,
freshness, price, quota, attribution, or terms of the deployed provider.

A caller creates a local SQLite ledger and records a fixture with an explicit
synthetic attestation, a UUID receipt identity, concrete source release,
bounded research rectangle, timezone-aware receipt time, and exact JSON bytes.
The ledger stores a SHA-256 hash of those bytes and their parsed row count,
alongside normalized bounds and receipt time. It always records completeness
as UNKNOWN: an empty result does not prove there were no alerts, and a missing
row does not establish a retraction. A digest supports change detection; it
does not authenticate an upstream source.

The ledger rejects duplicate JSON keys, invalid fixtures, broad bounds,
missing timezone, and an alias release such as latest. A repeated receipt ID
with identical metadata is idempotent; the same ID with changed metadata is a
conflict. Each receipt is written transactionally. It does not link receipt
rows to cases or to the separate candidate snapshot store, and cannot by
itself reconstruct a response from the hash. All caller-supplied receipt data
is an unverified assertion, not proof of a real provider request.

Before real evidence or integration, establish source/retention terms,
transport and query semantics, legal area, authorization, identity, storage,
provenance verification and a tested recovery plan. This SQLite fixture ledger
is not a production database, evidence store, ingest adapter or backup.
