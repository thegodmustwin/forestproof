# Current Status

**Last updated:** 2026-10-25  
**Milestone:** private GitHub source established; Codex Cloud onboarding next.

## Truthful snapshot

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| GitHub source control | WORKING | Private repo thegodmustwin/forestproof, default branch main. Initial commit is 71af70f81318ea98e4d1ab20bd52739aa97012c1. |
| GitHub CI | WORKING | API tests and web checks passed on the initial app commit and both context-doc commits. A successful run for the latest recorded context-verification change is https://github.com/thegodmustwin/forestproof/actions/runs/40217015885. |
| DEMO vertical slice | WORKING | Synthetic observation → case → transition/assignment → evidence hash → action/follow-up → JSON dossier/outcome graph is implemented and covered by API checks. |
| Live data | DOCUMENTED_NOT_TESTED | GFW, Copernicus, NASA FIRMS, and KFS remain candidates. No record-level live feed is active or represented as validated. |
| Legal context | PLANNED | No verified court order, permit, restriction, or qualified human legal review is loaded. |
| Persistence | PARTIAL | SQLite is the DEMO development adapter. PostGIS SQL exists as a target; production runtime is not connected to it. |
| Authentication and tenancy | PLANNED | DEMO is constrained to one seeded organization. Non-demo requests fail closed. No real identity or multi-tenant operation. |
| Codex Cloud | PLANNED | GitHub source is ready, but the owner still needs to connect/select the repo and create/test/publish a Cloud environment. |
| Production deployment | NOT DEPLOYED | Owner prefers OVH. Only a temporary hostname is known; server IP, OS, SSH, DNS/domain, firewall, backups, and deployment method remain unverified. |

## Constraints and non-claims

1. The Aberdare map area is illustrative, not an official licensed boundary.
2. DEMO observations, cases, dates, coordinates, confidence-like values, and evidence are synthetic; they are not current Kenyan incidents.
3. A remote-sensing signal cannot establish cause, authorization, illegality, or causal conservation impact by itself.
4. The original prompts mention October 2026 court reporting. No operative official order or current legal status is in the application; verify before use.
5. Real field or personal evidence must not enter the current unauthenticated demo system.
6. The old Railway guide is historical; OVH is the owner's stated preference. No website has been deployed.

## Verification evidence

- Local API tests: 8 passed with Python 3.13 on 2026-10-21.
- Local web typecheck: passed on 2026-10-21.
- Local web production build: passed and generated nine routes on 2026-10-21.
- Hosted-proxy topology check: web proxy returned HTTP 200 for API health and observations on loopback on 2026-10-21; this was not a public deployment.
- GitHub Actions for initial app commit `71af70f81318ea98e4d1ab20bd52739aa97012c1`: API and web jobs passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40185388840.
- GitHub Actions for context/onboarding commit `be4402f4f4c44f2f1ca52dc694af185164c3263e`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40216435071.
- GitHub Actions for follow-up context-verification commit `107e31f0b39067e19a47d40496a47282b35c04c5`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40216705267.
- GitHub Actions for status/map update commit `0078e91f0ce2211863aac2fb393f7b5c5cbc0ada`: API tests and web checks passed on 2026-10-25; https://github.com/thegodmustwin/forestproof/actions/runs/40217015885.

## Next checkpoint

Create and publish a Codex Cloud environment for this repo using Python 3.12 and Node 20, run the CI-equivalent checks there, and record the result. Then continue with a verified AOI/source and the production-security gaps before planning OVH deployment.
