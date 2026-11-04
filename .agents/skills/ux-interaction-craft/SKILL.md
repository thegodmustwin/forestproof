---
name: ux-interaction-craft
description: Improve product flows, navigation, forms, feedback, accessibility and edge states. Use for UX work or a substantive interface change; focus on the affected flow rather than auditing unrelated screens.
---

# UX interaction craft

Start from a concrete task: what is the user trying to accomplish, what information do they need, and how will they know it worked? Inspect existing behavior before changing it.

- Give the primary action a concrete label. Keep navigation destinations, selected state and browser back behavior predictable. Preserve deep links and meaningful URL state.
- Show the next useful action in empty states. Distinguish loading, unavailable, empty, stale and completed states; missing data must not quietly become example data.
- Put validation at the point of correction, keep entered values, prevent duplicate submission where needed and state what happened after a mutation. Use undo or confirmation in proportion to real consequence.
- Let users scan summaries and open evidence/details when needed. Avoid hiding essential caveats, costs or decision authority behind tooltips.
- Use semantic HTML, real links and buttons, labels, suitable input types and autocomplete. Keep keyboard order logical, focus visible and focus restored after dialogs. Use native interactions before custom widgets.
- Check text/background and control contrast, non-color state cues, text resizing, touch use and reduced motion. WCAG 2.2 AA is a target to test, not a compliance claim made from inspection alone.
- Keep error messages actionable and free of secrets. Explain permission and source failures honestly. Do not present a satellite signal as a legal finding or an unavailable source as a healthy feed.
- Preserve authorization and privacy boundaries. Interface polish is not authentication, tenant isolation or storage security.

Verify the affected happy path plus the most important failure/empty state. Use tests where behavior matters and a browser for keyboard/mobile interactions. Do not claim these checks ran if they did not.

References for specific decisions:
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
- [W3C WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [WAI ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [GOV.UK Design System](https://design-system.service.gov.uk/)
