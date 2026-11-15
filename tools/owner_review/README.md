# Private historical owner review

This loopback workspace opens FP-RESEARCH-001 for a named owner. It verifies the 16 archived file hashes, reconciles the ten raster receipts against the manifest, and retains the original case, observation, dossier and manifest bytes. Keep the restored bundle and database in trusted owner-only directories. The historical archive and the current owner review remain distinct. The owner can download the original observation receipt and the current dossier after signing in.

Use the repository root and Python 3.12. Initialize in a new path before the first launch.

```text
python -m tools.owner_review --database /private/owner-review.sqlite3 init --archive /private/recovered-case --owner-name "Owner name"
python -m tools.owner_review --database /private/owner-review.sqlite3 start --open-browser
```

Set the owner password in the masked terminal prompt the first time. The browser username is `owner`. The database holds a salted memory-hard verifier. The listener binds to 127.0.0.1 with an exact Host check, authentication for each review download, same-origin and signed form checks for writes, and an idempotent submission key. Keep this HTTP service on loopback. A review appends the provisioned owner's name, the source receipt digest, UTC time, disposition, note and follow-up date. The source receipt stays unchanged. The dated follow-up becomes part of the dossier as soon as a review is saved.

## Backup and restore

```text
python -m tools.owner_review --database /private/owner-review.sqlite3 backup /private/owner-review-backup.sqlite3
python -m tools.owner_review --database /private/owner-review-backup.sqlite3 backup /separate/private/owner-review-restored.sqlite3
```

Use a fresh destination. The copy checks SQLite integrity and verifies the original digests and review linkage. Test the restored file on loopback and compare the receipt bytes and the exported dossier. Keep the encrypted original archive for the ten source rasters. The review database holds the original metadata and receipts. A protected local copy and an off-device recovery exercise have separate acceptance criteria.

Run the focused tests with `python -m unittest discover -s tools/owner_review -v`. The tests use deliberate fixtures. The public visibility and synthetic tester routes have no dependency on this workspace.
