# Synthetic preview upload guard

The API and the storage adapter deny evidence uploads by default, independently
of the HTTPS preview gateway's path rule. The shared preview explicitly sets
`FORESTPROOF_DEMO_EVIDENCE_UPLOADS_ENABLED=false` in its Compose file. A
missing, misspelled or non-`true` value is disabled. The gateway's existing
deny remains a separate layer.

For an isolated local `demo` only, developers may explicitly set
`FORESTPROOF_DEMO_EVIDENCE_UPLOADS_ENABLED=true` to test synthetic evidence.
Even an enabled flag does not permit evidence uploads in `owner_demo` or
unsupported modes. Do not use the demo for real, personal or private evidence.

These guards do not authenticate people, secure an exposed API, replace gateway
access controls, provide production storage or guarantee that a user has not
entered sensitive information in other fields. They are source-code changes,
not proof that the deployed preview has been updated. Real owner identity,
authorization, private storage, scanning, retention and tested recovery remain
requirements before accepting real evidence.
