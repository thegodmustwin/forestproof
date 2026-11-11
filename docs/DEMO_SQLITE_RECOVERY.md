# Synthetic demo SQLite copy and recovery drill

This is an offline development candidate. It copies **only the SQLite database**
using SQLite's online backup API, including committed WAL data. It does not copy
evidence objects, configuration, passwords, API keys, or PostgreSQL volumes; it
is not encryption, an off-host backup, a production storage design, or proof
that the November 1 recovery archive can be restored. Do not use it to make
claims about real evidence or production readiness.

Work only with synthetic data in private, trusted directories. Create the
destination directory yourself with permissions restricted to the operating
account before using the tool; do not use a shared or untrusted directory. On
Unix the tool creates the destination with owner-only file mode (0600);
Windows access depends on the destination directory's ACL. No file-level
encryption is provided.

From `services/api`, make a new copy and then a **separate test restore**:

    python -m app.demo_db_copy /private/demo.db /private/backups/demo-copy.db
    python -m app.demo_db_copy /private/backups/demo-copy.db /private/drills/demo-restored.db

The destination and its SQLite sidecars must not already exist; the utility
does not overwrite them. It validates SQLite integrity and checks for the
expected ForestProof demo tables. A successful copy is still only a point-in-time
database snapshot. Verify the intended synthetic records and application
compatibility separately in an isolated environment; never replace an active
database as a routine drill.

Before handling the private OVH recovery archive, independently inventory and
reconcile its contents with current GitHub work and the intended host. The
archive may include private credentials. Treat real backup/restore planning,
encrypted off-host storage, separate evidence objects, retention, operator
authorization, and a documented production restore test as outstanding work.
