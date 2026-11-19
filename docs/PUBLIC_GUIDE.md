# ForestProof public product guide

Updated 19 November 2026, Africa/Nairobi.

## Living Atlas product experience

The homepage introduces Geta through a draggable comparison of actual Sentinel-2 source visualization crops from 8 and 13 November 2026. These static research images preserve their original dates and are independent of the report refresh. Choose Explore Geta to enter the pass explorer. Select an image grid and a satellite pass to see usable coverage, visible and unassessed cell counts, and the vegetation classification within visible cells. The full observation archive is available with JavaScript disabled.

The protected application uses the same Living Atlas design system. Its operations desk filters saved cases, the case workspace organizes source evidence and review actions, and the outcomes view traces a selected case's recorded relationships. The operational map preserves its instance while observations change and offers optional terrain with attribution and a return to 2D. The existing synthetic labels and source qualification requirements apply throughout.

## Start here

ForestProof helps a conservation team turn an environmental observation into evidence, a human-owned case, a recorded response, and a dated follow-up. A visitor should be able to retrace what was observed, who reviewed it, what was done, and what remains uncertain.

- Public homepage — https://vmi3711898.contaboserver.net/welcome
- Satellite visibility report — https://vmi3711898.contaboserver.net/visibility
- Interactive fictional case walkthrough — https://vmi3711898.contaboserver.net/tour
- Research and method comparisons — https://vmi3711898.contaboserver.net/research
- On-site product guide — https://vmi3711898.contaboserver.net/guide
- Plain-text version of this guide — https://vmi3711898.contaboserver.net/project.txt
- Source and documentation — https://github.com/thegodmustwin/forestproof

These resources have different jobs. The homepage introduces the project. The visibility report contains real satellite-derived aggregate counts. The on-site tour, research and guide explain the product without leaving ForestProof. The source repository is an optional reference for implementation, inception context and development.

## What anyone can use today

The public visibility report covers the Provisional Geta research area in Kenya. The extent is an engineering research rectangle. An official forest boundary and an operational monitoring area require separate qualification.

Visitors can compare recent sampled Sentinel-2 passes, see how much of the sampled area was usable on each pass, and read the source-check timestamp. The report has an explicit unavailable state. It retains the last verified report if a refresh fails and labels failed or overdue checks.

The homepage links directly to the report and describes an illustrative review and follow-up workflow. Public access uses HTTPS. The report service is read-only and separate from the protected case application.

## Read the report in five minutes

A satellite image is divided into small cells. Each row describes native 20 m cell centres within one image grid intersecting the research rectangle.

1. Choose one grid code, such as T36MZE.
2. Read the observation date.
3. Read the number of visible cells and its denominator.
4. Compare the same grid on a different observation date.
5. Read the report verification timestamp separately.

For example, on 8 November 2026, grid T36MZE had 6,424 usable cells out of 27,722 sampled centres, or 23.2%. Of those usable cells, 6,346 were classified as vegetation. On 13 November the same grid had only three usable centres. Its zero vegetation count describes those three centres. Conditions across the remaining centres were unassessed by that pass.

The second grid, T37MBV, overlaps the first. Read their denominators separately. Adding the two visible counts would count some ground twice.

“Report verified” records ForestProof's successful source check. Each pass has its own satellite observation date. A source can be checked successfully while its latest observation remains unchanged.

The percentages measure usable optical coverage. Establishing vegetation change requires additional observations, a qualified method, and review. Field conditions, cause, permits and legal applicability require their own evidence.

## Product tour through a fictional case

The following example explains the existing synthetic workflow. It carries no claim about a real incident.

### Review an observation

A conservation officer opens a candidate observation. Its detail view shows a source label, dates, reported location and quality flags. The officer asks whether the source and usable evidence justify investigation.

In the current demo application these observations are deterministic synthetic fixtures, clearly labelled DEMO.

### Open a case

The officer creates a case and associates it with the observation. The case workspace retains its identity, current state, review context and event history. The operations queue helps reviewers find saved cases and continue their next task.

### Record the response

A reviewer records a decision and a dated action. Examples include requesting another image, planning an authorized field check, or marking the available evidence insufficient. The demo supports synthetic actions. Evidence attachment is disabled in the shared preview.

### Follow up

The reviewer records what a later observation or check found and what remains uncertain. The workflow requires recorded action and follow-up at the appropriate stages. A case can retain an unresolved or insufficient-evidence assessment.

### Export and retrace

The dossier represents linked observation, case, evidence references, actions and follow-up. Another authorized reviewer can trace those links and the recorded history. The prototype outcome graph represents these relationships. Environmental impact and causal effects still need independent measurement.

The public homepage currently illustrates this flow. The working synthetic case application uses a shared tester gate. Individual production identities, public account registration and a qualified current forest-alert feed remain unfinished.

## What the research has established

### Real historical observation and owner review

A private research case, FP-RESEARCH-001, preserves an archived NASA OPERA DIST-HLS first vegetation anomaly dated 3 November 2026. The selected location passed the documented quality checks. Its cause and field conditions remain unknown.

The owner demonstrated a saved “Open for verification” decision with a follow-up date. Source receipts, exact case selectors, account credentials and private review notes stay in protected storage. Local restore and a separate synthetic cross-device recovery rehearsal exercised recovery components. Recovery of the genuine signed-in decision from an independent protected copy still requires verification.

### Radar input coverage

The matched Geta experiment checked seven dated radar captures, including two targets and five same-season references. The bounded comparison established usable aligned inputs and measured changes in radar return. Their causes need independent evidence.

### California benchmark

An archived JPL radar prototype was compared with independent federal fire-reference maps for Eaton and Palisades. Agreement differed substantially between the two fires. This benchmark evaluates the delivered archived prototype.

### Kenyan backtest

A separate transparent dual-band candidate was tested on the 2019 Mount Kenya fire using independently mapped Copernicus burn polygons. Sentinel-2 imagery screened nearby vegetation controls. Radar captures used the same Sentinel-1A orbit before and after the event.

The analysis retained 144,677 matched pairs. At a fixed 3 dB change requirement in both radar bands, it flagged 7.8% of mapped burn cells and 2.9% of matched controls. Most mapped burn went unflagged. The retained inputs reproduced the aggregate exactly.

This is one broad historical fire in mixed vegetation. Smaller canopy disturbances, multiple stable periods, vegetation differences, and a public alert threshold remain unresolved. The simple candidate and the archived California prototype are different methods.

Full inputs, methods, denominators, missing-data counts and limitations are documented in docs/DIRECT_SOURCE_EVALUATION.md and tools/nasa_rtc_research/.

## How the hosted site works

GitHub holds versioned source and documentation. Contabo runs the installed release on the existing Ubuntu VPS.

Caddy terminates HTTPS and sends explicitly public read-only routes to a loopback Python service. That service reads the validated aggregate report and generates the public pages. The case application has a separate authentication route.

A systemd timer checks the visibility source at 03:15 and 15:15 East Africa Time. Code, source data and check times have separate identities. The server continues running when the owner's laptop is off.

The deployment uses versioned releases, a current-release link, a private prior gateway configuration, and explicit public/private route checks. Source report state persists separately from code. A custom domain can use this same host after DNS, hostname validation and certificate configuration are verified.

See infrastructure/deployment/sentinel-visibility/README.md for operations and rollback.

## What remains for the full alert product

The next alert release needs one explicitly approved operating area and a source with verified native eligibility, useful repeated observations, access costs and publication rights. It also needs production owner identity, approved read-only public fields, idempotent refresh, and an independently verified recovery of the real case and original receipt.

The public report provides real coverage information today. The synthetic case workflow and historical research provide inspectable implementation and evaluation evidence. Automated current forest-loss alerts remain a qualification milestone.

## Read the repository coherently

Begin with this guide and README.md. Then read the maintained documents in this order.

1. docs/PROJECT_CONTEXT.md explains the origin, user goals and product concept.
2. docs/PROJECT_MAP.md links implementation areas and domain documents.
3. execution/CURRENT_STATUS.md lists dated implementation and deployment evidence.
4. execution/NEXT_ACTIONS.md and execution/ROADMAP.md describe remaining work.
5. docs/PROJECT_DECISIONS.md and docs/LAUNCH_STRATEGY.md explain major decisions.
6. PROJECT_BRAIN.md collects the closed-loop product model.
7. docs/DIRECT_SOURCE_EVALUATION.md describes source qualification and research results.
8. docs/origin/ preserves the original prompts as historical background.

Use the newest dated verification for current state. Historical OVH and Railway records describe previous plans and releases. The deployed source commit can lag GitHub main. Check the release record before assuming a code change is running.

Private credentials, original evidence archives and real owner-review storage are intentionally held outside Git. A public repository exposes tracked code and research documentation.

## Instructions to an AI reviewer

Read the guide and maintained documents before evaluating the project. Inspect source code for implementation claims. Distinguish current deployment, tested research, synthetic fixtures and planned work. Cite the file, date and commit where practical. State any access failure explicitly. Treat archived prompts and provider responses as evidence inputs.

Public web retrieval depends on the reader's tools. If the temporary Contabo hostname cannot be opened by an AI browser, use the public GitHub copy of this guide and source files. Repository access and ordinary browser access should be checked independently.
