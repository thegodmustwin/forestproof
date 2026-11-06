# Reusable UI/UX skills

Three original, automatically discoverable skills are packaged under .agents/skills/ and installed locally at C:/Users/Owner/.codex/skills/. They are available for future local Codex turns; another machine or Cloud environment must use the repository copies or install them into its own user skill directory.

- ui-art-direction: decide and implement a product-specific visual direction.
- ux-interaction-craft: clear tasks, interactions, feedback and accessibility.
- ui-render-review: inspect rendered desktop/mobile views and refine the result.

Invoke a skill explicitly with its dollar-name when useful, or let normal skill discovery select it. Their descriptions are scoped to UI tasks, not backend work or universal restyling. No hooks, MCP permission changes, third-party launchers, paid subscriptions or model settings are installed. Existing skills were preserved.

The reference library at .agents/skills/ui-art-direction/references/design-library.md records original/public sources, licensing context and the distinction between inspiration and copying. Sources include Anthropic frontend-design, Impeccable, Vercel Web Interface Guidelines, W3C, GOV.UK, Carbon and public design galleries. This is a considered selection, not a ranking of all online UI resources or a guarantee of quality.

Start ForestProof UI work with DESIGN.md, current product context and the affected live code. A small bug should remain a small fix. Skills do not establish production security or permission to publish.


## Cross-project use, 2026-11-06

The owner's Windows Codex user directory also has a concise `~/.codex/AGENTS.md` design preference. It asks local sessions to use these skills when relevant while respecting each project's identity and scope. The preference was observed in the current desktop conversation. It does not transfer the Windows file to remote environments or guarantee a skill is selected on every turn.

A ForestProof Cloud checkout has the three portable skill folders under `.agents/skills/`, and the root `AGENTS.md` points agents to them. For other Cloud projects, make the same three folders available in that Cloud environment's user skills directory (or the other project's `.agents/skills/`) with appropriate access to this private repository. Preserve existing skills and avoid replacing conflicting names. Environment persistence and setup publication vary; verify in a new Cloud session rather than assuming the files sync across all environments. A supported reusable environment setup may automate the copy where available, but no Cloud environment configuration was modified by this handoff.

### Verified runtime copy, 2026-11-06

In the current Cloud runtime, the three repository folders were installed at `/home/agent/.codex/skills/` and their file hashes were compared with the repository originals. Concise UI-scoped guidance was added to the previously absent user `AGENTS.md`; existing skills/instructions were preserved, with no hooks or model/network changes. The executor skill catalog still returned no entries, so automatic discovery was not verified. Files are available to read in this runtime; persistence after replacement or a fresh session and account-wide sync remain unverified. The repository copies and `AGENTS.md` remain the portable fallback. No reusable environment draft was published by this installation.
