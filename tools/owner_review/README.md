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

### Encrypted portable ledger snapshot (candidate)

From the repository root on Python 3.12 or newer with SQLite serialization support, install the separate tooling dependency with `python -m pip install -r tools/owner_review/requirements-backup.txt`. Generate a long random passphrase in the owner's password manager; a character-count rule does not establish password strength. Save the passphrase in the owner's vault before use, test vault access from another device, and never pass it in arguments, environment variables, chat or Git. Run these commands interactively in a terminal; prompts hide input:

```
python -m tools.owner_review.encrypted_backup backup /private/owner-review.sqlite3 /private/new-case.enc
python -m tools.owner_review.encrypted_backup verify /private/new-case.enc
python -m tools.owner_review.encrypted_backup restore /private/new-case.enc /private/new-restored.sqlite3
```

Use native Windows paths when running on Windows. These commands require existing trusted, private directories and new destination filenames; they do not upload anything. Verify authenticates the encrypted envelope and checks SQLite, original document hashes, and review linkage in memory. Restore writes a **plaintext** database into the specified private directory, so protect its directory ACL and handle the recovered file like the original. On Windows the inherited directory ACL, not Unix mode `0600`, determines access. Atomic create-only publication requires a filesystem that supports hard links, and conflicting SQLite sidecars are rejected. A failed directory sync after publication may leave a complete destination present; never overwrite it blindly. On systems supporting directory fsync, the command syncs the directory; actual storage durability depends on the filesystem.

The explicit ForestProof v1 envelope uses a six-byte `FPOR1\x00` header, 16-byte random salt and 12-byte random nonce as AES-256-GCM authenticated header, followed by ciphertext and a 16-byte tag. The 256-bit key is derived from the exact UTF-8 passphrase using scrypt (N=32768, r=8, p=1). This is a project-specific format and not an external standard. The passphrase is not saved by the tool. Loss of the passphrase makes the backup unrecoverable. The tool has not been independently audited and is a candidate pending private restore testing. It does not cover the ten separate raster files, transfer data off-device, establish an independent recovery credential, or protect against losing the application host. Never commit the encrypted backup, real review, private receipt or passphrase.

Run the focused tests with `python -m unittest discover -s tools/owner_review -v`. The tests use deliberate fixtures. The public visibility and synthetic tester routes have no dependency on this workspace.
