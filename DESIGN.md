# ForestProof design direction

## Product and task
ForestProof helps a responsible person review a sourced observation, retain evidence, assign and record a response, then document follow-up. The working app is synthetic. Prioritize the actual next review action and source confidence over decorative telemetry.

## Visual direction: field atlas and evidence ledger
Use warm paper, forest ink, sharp rules, an expressive serif heading and compact legible operational text. Original contour linework is abstract decoration, never geographic evidence. A strong opening and quieter working surfaces should create a clear reading order; maintain the case queue's real data and failure states.

- Roles: forest for identity/action, amber for demo/review caution, muted ink for secondary information. Never use color alone.
- Layout: deliberate hierarchy instead of uniform metric cards; prioritize the saved case queue and useful context.
- Typography: Georgia for editorial display; system sans for controls, monospace for identifiers/dates where useful. Avoid new hosted-font dependencies.
- Interaction: visible focus, real SVG icons, skip link, touch-sized primary actions, responsive navigation, restrained reveal/hover motion and reduced-motion support.
- Truth: DEMO visible, missing data remains unavailable, outcomes unmeasured, no invented source health, live status, legal conclusion or impact.
- Preserve existing deep links, API state, workflow labels and test selectors.

## Reusable workflow
The original skills in .agents/skills/ cover art direction, UX behavior and rendered review. Copies are installed in the owner's local Codex user skill directory. They improve task guidance; they do not change the model, Codex's own application UI or every remote environment automatically. New Cloud work should use this repository's skill copies and context. See docs/UI_SKILLS.md for usage and sources.

## Verification
The design branch captures desktop (1440px) and narrow mobile (390px) views of a synthetic case queue during the owner-demo browser smoke. Inspect the resulting images; screenshots and automated tests alone are not an accessibility certification. Never capture private evidence or real credentials.
