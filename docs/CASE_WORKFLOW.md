# Case Workflow

## Goal

Turn a reviewable observation into a human-governed evidence trail and outcome record.

## P0 state machine

    NEW
      -> UNDER_REVIEW
      -> FIELD_VERIFICATION
      -> ACTION_RECORDED
      -> FOLLOW_UP
      -> CLOSED

`REOPENED` returns a case to review or verification when new evidence warrants it.
The API enforces this P0 state machine. It does not determine a legal conclusion;
follow-up assessment values separately record `VERIFIED_INCIDENT`,
`FALSE_POSITIVE`, `INSUFFICIENT_EVIDENCE`, or `UNRESOLVED`.

In the current SQLite demo, advancing to `ACTION_RECORDED` or `FOLLOW_UP` requires a saved action; closing requires both an action and a saved follow-up. A follow-up cannot be added merely by setting an action-looking state. The demo case screen can record synthetic action and follow-up descriptions, and the dashboard and operations queue read saved API cases. Existing inconsistent demo records remain visible, but cannot pass a new guarded transition until the required records exist. This is a workflow integrity control, not production authentication or a legal determination.

An isolated browser test exercises observation → saved case → queue → synthetic action → synthetic follow-up → closure through the owner-demo gateway. The deployed shared preview has not been updated or reverified by this change. It remains synthetic-only and is not suitable for personal or real field information.

## Transition record

Every P0 state transition appends:

    actor
    timestamp
    previous_state
    new_state
    reason
    note

Actor role, explicit supporting-evidence links, due dates, and escalation
records are planned additions, not current claims.

## Human ownership

Case owners can specify responsible organization, assigned investigator, priority, due date, required evidence, follow-up date, and escalation status. Automatic notification or external escalation never substitutes for authorized human approval.

## P0 case review prompts

- What did the source actually observe?
- What alternative explanations remain plausible?
- What land/forest and management context is known?
- What legal or authorization information is sourced, missing, or time-uncertain?
- What evidence is required before a conclusion or response?
- What action was actually recorded?
- What follow-up observation exists, and what does it not prove?

## Field report

A mobile-friendly report captures case, authorized investigator, time, access-controlled location, category, forest type, photos, notes, observed activity, safety concerns, uncertainty, and suggested next action. Offline synchronization is deferred until implemented and tested.
