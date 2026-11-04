---
name: ui-render-review
description: Review and finish a rendered web or product interface after design or UI implementation, including responsive layout and visual regressions. Use for polish, visual QA or pre-share UI checks; do not substitute source inspection for a rendered check.
---

# UI render review

Use the actual implementation and representative truthful content. Prefer the project's existing browser/screenshot tooling. Inspect an existing golden only after checking that it matches the current route, state and code.

Review the primary task at desktop and narrow mobile widths. Include a meaningful long-content, empty/error or selected state when it affects this change. Look for:

- Clear first reading, coherent alignment, intentional spacing and appropriate density.
- Typographic hierarchy, usable line lengths, readable metadata and contrast.
- Overflow, clipped text, obscured controls, horizontal scrolling and fixed-position collisions.
- Keyboard focus, touch-sized targets, active/disabled states, pending/error feedback and reduced motion.
- Believable content, consistent units/time labels, provenance, and distinctions between example and live information.
- Assets that load, proportions that hold, and layout shifts that disrupt the task.

Fix the highest-impact set of issues in one pass, then rerender the affected views. Avoid endless pixel churn or a mandatory screenshot after every tiny edit. A focused change does not require unrelated redesign or new visual test infrastructure.

Record the route/state/viewport and what was actually verified. If the app cannot render, report the blocker and use code review as a limited fallback; never say a screenshot or browser check passed without seeing its result. Use source/behavior tests for what they can establish and rendered review for what they cannot.

Do not capture or upload credentials, private evidence or personal data for convenience. Use safe synthetic fixtures, supported secret handling and existing authorization.

References:
- [Vercel interface guidance](https://vercel.com/design/guidelines)
- [Carbon data visualization](https://carbondesignsystem.com/data-visualization/overview/)
- [W3C accessibility evaluation guidance](https://www.w3.org/WAI/test-evaluate/)
