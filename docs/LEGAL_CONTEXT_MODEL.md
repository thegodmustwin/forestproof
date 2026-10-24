# Legal Context Model

## Scope and status

**PLANNED P0 reference model.** ForestProof provides source-grounded context for qualified human review. It does not provide legal advice, make enforcement decisions, or determine that any activity is illegal.

## LegalContextService inputs

    location
    observation_date
    forest_classification
    management_area
    available_legal_documents
    authorization_evidence

## Outputs

    relevant_documents
    potential_restrictions
    source_provenance
    effective_date_intervals
    verified_status
    unresolved_questions
    human_review_required

## Source hierarchy

1. Official issued document or reliable official record.
2. Official secondary reference.
3. Reputable secondary reporting, labelled as secondary.
4. Human-entered claim, labelled unverified until reviewed.

Press reporting is never a substitute for the operative court order, permit, or official decision.

## Time-aware applicability

Every legal document version should preserve issuing authority, identifier, publication/decision date, effective-from and effective-until dates where known, geographic scope, activity scope, operative provisions, limitations, amendments/stays, source URL, and human-review status.

Queries use the observation historical date. Current rules must not be silently applied to a past observation. Unknown dates, scope, and authorization status remain explicit uncertainties.

## Permitted classifications

The system can represent states such as FOREST_DISTURBANCE_OBSERVED, POSSIBLE_HARVESTING, POSSIBLE_FIRE_DAMAGE, PLANTATION_MANAGEMENT_POSSIBLE, AUTHORIZATION_UNKNOWN, DOCUMENTED_AUTHORIZATION, POTENTIAL_POLICY_CONFLICT, VERIFIED_RESTRICTION_APPLIES, REQUIRES_HUMAN_REVIEW, VERIFIED_INCIDENT, FALSE_POSITIVE, and INSUFFICIENT_EVIDENCE.

It must not derive illegal logging solely from vegetation change or absent online permit records.
