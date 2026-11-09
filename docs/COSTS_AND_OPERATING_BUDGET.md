# ForestProof — costs and operating budget

**Hosting update, 2026-11-10:** The user has an existing Contabo VPS and selected it as the target. Its plan, recurring charges, traffic and backup costs have not been independently inspected. Previous OVH amounts or preview history must not be assumed to describe Contabo. Do not add paid services without the owner's cost approval.

**Status:** initial ledger; a password-protected synthetic preview is deployed, but no production pilot or live feed is active.

## Current spend and commitments

| Item | Current evidence | Project action/status |
| --- | --- | --- |
| OVH VPS | The owner says the OVH account is already paid. The plan, renewal date, and exact monthly/annual cost have not been inspected. | A prior task records a password-protected synthetic preview on the existing VPS. This task has not rechecked it or ordered additional hosting. |
| Codex Cloud | The owner reports that Codex usage is within the current allocation. This agent cannot inspect the account meter or billing settings. | Development continues within the owner's account. No separate data-service or hosting subscription was started here. |
| GitHub Actions | The private repository runs automated checks on pushes. This session cannot inspect the owner's included minutes, usage, spending limit or billing configuration. | Checks consume GitHub-hosted runner time; charges, if any, depend on the account's plan, remaining allowance and spending settings. No additional CI service was ordered. |
| GFW Integrated Alerts | Dataset metadata labels the data CC BY 4.0. The query API has authenticated routes; the published terms, rate limits, and any API fee have not been verified. | No credential has been added and no alert records queried. Treat service cost as **unknown**, not $0. |
| Copernicus scene context | Official Copernicus documentation describes free worldwide access and free-tier quotas. A handful of bounded anonymous catalog metadata requests succeeded without an account or billing. Full service terms, any extended-tier charges, and the owner's OVH traffic/compute cost remain unverified. | An opt-in owner-demo scene lookup is implemented and tested locally; it is off by default and is not an alert feed or a deployed service. No imagery or paid account was obtained. |
| Other candidate data | NASA FIRMS and DIST-ALERT have different access requirements and scopes. Their exact service terms/costs are not verified for ForestProof. | No paid account, alert query integration, or recurring data service has been activated. |
| New third-party services | No production database, object storage, monitoring, email/SMS, or external hosting service has been provisioned by this work. | Any such service needs a cost/need review before activation. |

This ledger records project setup facts, not the owner's complete invoices. Public documentation/catalog requests made during research do not establish the price of a future production API service.

## Feed cost decision

For GFW, the dataset license and the API service are separate questions. The catalog record reports CC BY 4.0, while the OpenAPI describes API-key/OAuth-protected query operations. The OpenAPI and catalog inspected on 2026-10-26 do not state a price or rate limit. The official Terms of Service page is linked from the dataset page. The owner published the GFW documentation domains to Cloud egress, but the Terms page still fails with an outbound tunnel 403 from this environment. Consequently, ForestProof must not describe GFW access as free until the applicable service terms, account access, quotas, and billing are confirmed.

On 2026-10-27, the legacy GFW terms URL was confirmed to return a 301 redirect to `https://globalnaturewatch.org/terms`; the redirected host is blocked by this workspace proxy. The owner subsequently supplied copied terms text from that page. It states account/API-key and attribution obligations, with dataset-specific licenses, but does not state an API price, quota or rate limit. The referenced attribution requirements could not be retrieved here. The copied terms' $100 liability cap is not a price. Cost therefore remains UNKNOWN; no alert records have been queried.

The same check applies to any alternative feed: confirm the exact product license, API/service charges and limits, permitted commercial use and redistribution, attribution, expected query volume, and any processing or storage costs. A free-to-use source can still have operational costs on the OVH host.

## Approval gate

Before enabling a source in LIVE mode, record a bounded first-year cost estimate (including the existing host share where known), confirm the source's fees and quota, and make the estimate visible to the owner. Do not create a paid source account, enable billing, exceed a quota, or add a recurring service without explicit owner approval. If service terms or prices cannot be confirmed, keep the source disabled and label the cost unknown.


## 2026-10-28 dataset-versus-service clarification

WUR describes its RADD dataset as CC BY 4.0 and royalty-free with attribution: https://www.wur.nl/en/research/products-services/radd-forest-disturbance-alert. This does not quote a GFW Data API service price, quota, future processing cost, or OVH cost. The API service cost remains UNKNOWN, and no paid service or alert-record query is authorized without the applicable cost review. WUR's published Earth Engine production-compute estimate is a different cost and must not be treated as a GFW API price.

On 2026-10-29, only public API documentation and field metadata were fetched. The standalone research transport has a default-false, explicit no-additional-service-fees attestation; it is not wired to the app, and the attestation is not proof of pricing. All transport tests used synthetic or loopback-only responses. No API key, paid account, or live alert query was used.

The later 2026-10-29 Copernicus check requested a small number of public satellite scene metadata records and tested the opt-in owner-demo lookup. The source's free-tier documentation and limitations are recorded in `docs/DATA_SOURCES.md`; a scene acquisition is not an alert. No paid service was ordered, and we cannot inspect the owner's OVH or GitHub billing balances.
