# Forest Intervention Outcome Graph

## Purpose

The Forest Intervention Outcome Graph is ForestProof long-term learning asset: traceable relationships between environmental observations, decisions, interventions, and evidence-backed follow-up. It is not a claim that the platform caused a conservation outcome.

## P0 representation

Use ordinary relational tables and PostGIS first. A dedicated graph database is not required.

    monitored_area
      -> environmental_observation
      -> corroboration/context
      -> investigation_case
      -> evidence and assignment
      -> field_report/intervention_action
      -> follow_up_observation
      -> outcome_assessment

Each edge must carry source, actor, time, confidence/evidence level, and where applicable a processing or document version.

## Outcome statuses

Examples include:

- NO_DISTURBANCE_CONFIRMED
- DISTURBANCE_CONFIRMED_CAUSE_UNKNOWN
- AUTHORIZED_MANAGEMENT_CONFIRMED
- UNAUTHORIZED_ACTIVITY_CONFIRMED_BY_AUTHORITY
- RESPONSE_COMPLETED
- RESPONSE_IN_PROGRESS
- FOLLOW_UP_SHOWS_CONTINUED_DISTURBANCE
- FOLLOW_UP_SHOWS_NO_NEW_DETECTED_DISTURBANCE
- INSUFFICIENT_EVIDENCE

No new disturbance detected does not establish that an intervention caused activity to stop.

## Future learning questions

When real, authorized usage produces sufficient records, the graph may help identify repeat locations, false-positive patterns, long investigation times, evidence gaps, response/follow-up associations, and detection coverage gaps. It must not make causal or predictive claims without validated evidence.
