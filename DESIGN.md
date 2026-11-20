# ForestProof design direction

## Living Atlas 2 geographic continuity — 20 November 2026

The owner explicitly authorized replacing any interface that does not serve the supplied planetary-observatory and scientific-evidence direction. The first spatial release connects planet → Kenya → provisional Geta landscape → selected observation → fictional investigation. The historical NASA Earth artwork gives planetary orientation; a separate Natural Earth country locator identifies Kenya and the research location accurately. The public atlas uses real bounded elevation and georeferenced source imagery, with a functional 2D relief fallback when WebGL is unavailable. The laboratory retains precise 2D evidence reading. Case lineage resolves actual recorded fictional steps rather than decorative connections.

Canonical palette is orbital black `#071511`, deep forest `#102B23`, terrain slate `#203B34`, mint `#8CE4BD`, cyan `#65D5E5`, ivory `#F2F0E5` and amber `#E8B86A`. Geographic data, historical imagery and synthetic records retain separate dates, sources and meanings. The full supplied brief is preserved in docs/origin/LIVING_ATLAS_2_ASSESSMENT_20261120.txt as historical design input; current user direction and verified implementation remain authoritative.


## Living Atlas — adopted 19 November 2026

ForestProof connects planetary observation, geographic context and the evidence behind a human decision. The public observatory introduces a place and its real observation coverage. The working application helps a reviewer understand a source, own a case, record a response and return to its evidence.

The owner selected Living Atlas from a supplied design assessment. This replaces the earlier field-journal direction while preserving the source, uncertainty and workflow contracts.

## Shared visual system

Canonical tokens live in packages/ui/living-atlas.css. The public Python service and React application use the same palette and type roles.

- Orbital black and deep forest support the public Earth view and application navigation.
- Cyan identifies sensor observations. Mint and emerald establish identity and primary action.
- Amber indicates uncertainty or review. Coral is reserved for explicit errors.
- Ivory is the reading surface for source evidence, reports and case history.
- Georgia and system serif fallbacks provide editorial display. System sans supports controls and text. System monospace carries technical identifiers and measurements.

Use at least 16 px body text, 14 px important controls and labels, and 12 px secondary metadata. Maintain visible focus, adequate contrast, touch-sized targets, readable narrow layouts and reduced-motion behavior. Native controls should perform real actions.

## Scale and reading order

The visitor journey begins with an understandable Geta observation, then connects real coverage, an interactive fictional practice case, research and explanations. All main destinations stay on-site. External references are optional source citations or developer material. Actual observation dates and coverage remain visible with the source report.

The pass explorer lets visitors choose a grid and observation date, compare visible and unassessed cells, and interpret the vegetation count within the visible subset. Its aggregate bar describes a share. Source quality masks have their own geographic interpretation and publication requirements.

Private pages prioritize saved records, case ownership, review state, source quality and next action. The evidence lineage follows a selected case and its recorded attachments, actions and follow-ups.

## Public workbench depth

The observation explorer and fictional case walkthrough share dark layered surfaces, mint action, cyan source information and amber uncertainty. Depth belongs to evidence layers, image framing and a connected dossier. Image pixels retain their source identity; fabricated terrain, measured-looking traces or alert polygons must not decorate a real observation. The centre image, timeline and interpretation should communicate one task. The fictional dossier may be downloaded or printed after its steps are complete, with its teaching status and absence of signature visible.

## Spatial implementation

The homepage uses two locally served, unchanged native-pixel Sentinel-2 true-colour visualization crops from the same research window on 8 and 13 November 2026. A straight observation panel opens with the clearer 8 November image. Native date choices pair each crop with its verified classification share, denominator, plain-language meaning and an observation link. The controls work without JavaScript. A numbered See → Understand → Review path gives first-time visitors a concrete route into the product. Their static dates, source identities and hashes are retained; the visual is context, not a change-classification map. The initial public view requires no WebGL engine. The earlier historical NASA composite remains an archived asset.

The operational map uses the existing MapLibre renderer. Create its instance once and update records, markers and selection independently. Functional 2D controls and an accessible observation list provide a fallback. Optional terrain is loaded on request with its source attribution, failure feedback and a direct return to 2D.

## Evidence semantics

Keep real source-derived aggregates, synthetic case fixtures and historical research visibly identified. Preserve source-check time independently of each acquisition date. Missing data has an explicit unavailable state. Failed refreshes preserve the last verified report and mark its age.

Earth artwork, terrain context and graph layout are visual representations. Recorded source evidence determines the scientific claim. Human review determines the documented action and remaining uncertainty.

## Verification

Inspect the rendered public flow at desktop and mobile widths. Exercise grid and date selection, keyboard and touch, no-script fallback and reduced motion. Check source failures and unavailable reports.

For the working application, verify map lifecycle stability, saved-case selection, evidence lineage and the existing complete synthetic case flow. Preserve authentication and protected storage through deployment. Record exact tests, rendered views, release commits and verification limits in execution/CURRENT_STATUS.md.
