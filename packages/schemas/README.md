# Shared schemas

P0 request and workflow schemas live in `services/api/app/models.py` so the
server remains independently runnable. Move stable, versioned contracts here
only when a second consumer genuinely needs them; do not duplicate types just
to form a monorepo package.
