# Disabled-mode SQLite guard

The API currently supports only synthetic `demo` and `owner_demo` storage.
For any other configured mode, including `live`, `Store.prepare()` returns
without creating a parent directory, opening the configured SQLite path, applying
a schema or migrating it. Direct store connection and demo seeding attempts
also fail in unsupported modes. Existing API request guards remain in place.

Regression tests exercise startup against both an absent path and a preexisting,
unrelated SQLite database, confirm the file is byte-for-byte unchanged, and
verify that the supported synthetic modes still initialize and seed.

This is an isolation guard, not a LIVE database implementation, owner
authentication, encryption, a production backup or a restore plan. It cannot
determine whether a database explicitly configured in a supported DEMO mode
contains sensitive or real data. A future LIVE store must have separately
configured storage, enforceable identity, provenance, migrations, retention,
private backups and a verified restore before activation. No real data is
created or used by these tests.
