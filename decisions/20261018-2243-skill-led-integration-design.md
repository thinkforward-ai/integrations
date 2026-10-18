# Skill-led integrations, sourceable bootstrap, and shell aliases

**Date:** 2026-10-18

## Problem Description

Q1 concerns the Integrations project's purpose, scope, and working mode.
Its remaining design questions were the shared/tool-skill split, runtime
layout, metadata, aliases, discovery, project capabilities, approval, and
verification. Earlier alternatives included a universal installer, shell-only
implementation, executable bin bindings, duplicate command wrappers, and
installed-tool inventories.

The user approved the complete proposal after clarifying that bootstrap is
reusable source deployed into Agent Hub home, aliases can be actual shell
aliases, all resources belong in metadata, and verification is user-run.
The approval covers design and exact skill wording, not implementation or
installation. Original response: [Approve proposal](../inputs/2026-10-19-proposal-approval.md).
The record filename and date use UTC.

## Decision

1. Agent Hub supplies the shared installation skill and reusable bootstrap.
2. Integrations supplies tool skills and their resources.
3. Installed aliases are real shell aliases generated locally from selected
   integrations. Do not create a separate alias-management script, redundant
   bin commands, maintained installed-tool inventory, or empty configuration
   files.
4. Tool skills declare dependency arrays, all resources in metadata, optional
   aliases with default argument arrays, usage, and extra instructions.
5. Native tools remain OS-managed. Custom resources preserve relative paths
   beneath Agent Hub's `tools/<id>/`.
6. Installation requires preview, major/critical security-risk disclosure,
   and an explicit `Allow` / `Reject` gate. Verification remains user-run.
7. Project capabilities are mapped onto integrations, separate from aliases.
8. Existing Hub content is preserved. No new `.local`/`.config` storage or
   shell-startup edits are introduced. Implementation languages are unrestricted.
9. Hello-world remains the pilot; Whisper is on hold. Collaboration remains
   solo and AI-driven, with the stakeholder approving design decisions.

## Explanation

This resolves Q1. The accepted design supersedes conflicting earlier proposals,
including bin-wrapper bindings and the alias helper, while leaving earlier
immutable decisions and raw inputs unchanged. The prior
[naming](20261018-2021-integrations-name.md),
[skill-led installation](20261018-2031-skill-led-installation.md),
[ownership](20261018-2039-agent-hub-owned-tooling.md),
[dependency/language](20261018-2159-dependencies-and-language-choice.md), and
[approval-gate](20261018-2204-installation-approval-gate.md) records remain history.

### Relevant source layout

```text
agent-hub/
└── skills/
    └── install-integration/
        ├── SKILL.md
        └── scripts/
            └── bootstrap.sh

integrations/
└── skills/
    └── hello-world/
        ├── SKILL.md
        └── scripts/
            └── hello-world.sh
```

### Installed artifacts

```text
~/.agent-hub/
├── bootstrap.sh
├── aliases.sh
└── tools/
    └── hello-world/
        └── scripts/
            └── hello-world.sh

<project>/
└── capabilities.md
```

1. Bootstrap is bundled with the shared skill so it is available independently
   of the source repository.
2. Resources retain their relative directory structure beneath `tools/<id>/`.
3. Local `aliases.sh` stores actual selections; do not create an empty default
   when none exist.
4. Create project `capabilities.md` only when mapping is requested.
5. Existing files, including `say`, remain untouched except for explicitly
   approved, non-conflicting additions.

### Approved shared skill

Source: `agent-hub/skills/install-integration/SKILL.md`.

```md
---
name: install-integration
description: Discover or install integrations, configure optional shell aliases, provide user-run verification steps, and map project capabilities.
source: https://github.com/thinkforward-ai/agent-hub
metadata:
  resources:
    - scripts/bootstrap.sh
---

# Install an Integration

1. Read the tool skill's `metadata.integration` and additional instructions.
   Require dependency and resource arrays; use `[]` when empty. All source
   resources belong in metadata. For native tooling, `command` names an OS
   executable. For bundled tooling, it identifies an executable resource
   relative to the resource root.

2. For discovery, inspect metadata, command locations, and files without
   invoking integration commands. Report detected installation separately
   from user-confirmed readiness. Do not install, download, authenticate,
   activate shell configuration, or change preferences during discovery.
   Do not maintain a separate installed-tool inventory.

3. Before installation changes, describe the complete plan: dependencies
   to reuse or install, sources, commands, privileges, affected files,
   alias selections, project mappings, activation, user-run verification,
   and rollback limits. Use only trusted read-only inspection beforehand.

4. Highlight any major or critical security risks, including their cause,
   possible impact, and available mitigation. Disclose material uncertainties.
   If none are identified, say so without claiming the installation is
   risk-free.

5. After the preview and risk disclosure, ask with exactly two options:
   `Allow` and `Reject`. Proceed only after explicit `Allow`. Rejection,
   cancellation, or no answer means no installation changes. Material
   changes to the plan or risks require another preview and approval.

6. Reuse suitable native dependencies or follow the approved OS installation
   process. Keep OS-managed tools in their normal locations. Install custom
   resources under `${AGENT_HUB_HOME:-$HOME/.agent-hub}/tools/<id>/`,
   preserving relative paths. Do not create redundant bin links or wrappers.
   Implementation languages are unrestricted. Preserve existing files;
   stop on unmanaged collisions and retain prior managed content for recovery.
   Do not introduce `.local`/`.config` storage or edit shell startup files.

7. Deploy this skill's declared bootstrap resource as `bootstrap.sh` in
   Agent Hub home when needed. Preserve unrelated content and disclose
   updates in the installation plan.

8. Optional `metadata.integration.aliases` declares shell alias names and
   default argument arrays. Store selected bindings in Hub's `aliases.sh`.
   Bind unclaimed names; preserve existing selections when another provider
   is installed. Do not silently shadow unmanaged names. Quote executable
   paths and default arguments safely; never evaluate metadata as shell code.
   No declared aliases means no alias configuration.

9. Explain how to source Hub bootstrap in the shell that will invoke an alias.
   Aliases are not inherited by child processes. Noninteractive Bash requires
   alias expansion, and alias definitions must be loaded before the command
   using them is parsed.

10. Leave verification to the user. Provide manual steps and expected results.
    Do not automatically run the installed tool, its aliases, smoke tests,
    or self-tests. Report functional readiness as unverified until the user
    confirms it.

11. When project mapping is requested, identify the project, capability,
    chosen integrations, and purpose. Ask only for missing information.
    Record the approved mapping in the project's `capabilities.md`.
    Preserve unrelated mappings and omit machine-specific installation state.
    Capability mapping does not automatically create an alias.

12. On failure, restore prior managed content where safe and report changes
    that cannot safely be reversed. Do not automatically uninstall OS packages.
    Report installation status, alias selections, activation instructions,
    project mappings, and user verification steps. Installation permission
    does not authorize later tool execution.
```

### Approved hello-world skill

Source: `integrations/skills/hello-world/SKILL.md`.

```md
---
name: hello-world
description: Install or use the hello-world integration.
metadata:
  integration:
    id: hello-world
    command: scripts/hello-world.sh
    dependencies:
      - sh
    resources:
      - scripts/hello-world.sh
    aliases:
      hello:
        args: []
---

# Hello World

1. When installation is requested, start the shared integration installation
   workflow using this metadata. There are no extra setup steps.

2. Usage: accepts an optional name; `--help` prints usage.

3. User-run verification: with this integration selected for `hello`,
   `hello` should print `Hello, world!`; `hello Ada` should print
   `Hello, Ada!`.
```

### Bootstrap and local alias behavior

1. Resolve Agent Hub home using `AGENT_HUB_HOME`, defaulting to
   `~/.agent-hub`.
2. Add Hub's existing `bin/` directory to PATH when present, without duplication.
3. Enable Bash alias expansion.
4. Source local `aliases.sh` when present.
5. Perform no installation, file writes, or tool verification.

The sample generated alias uses the actual resolved Hub location, not a
repository default:

```bash
alias hello='"/home/madkroll/.agent-hub/tools/hello-world/scripts/hello-world.sh"'
```

User activation and verification are separate parsed commands:

```bash
source ~/.agent-hub/bootstrap.sh
hello
```

Sourcing bootstrap does not activate aliases in unrelated shells.

### Benefits and limitations

1. Minimal runtime files, no duplicate commands, native tools remain native,
   and shared installation rules stay out of tool skills.
2. Aliases require shell activation and are not standalone commands inherited
   by arbitrary child processes. Discovery cannot prove functional readiness.
3. Sourceable configuration is executable shell code; installation previews
   must disclose material risks of the actual sources, privileges, and changes.

## Consequences

1. Remove resolved Q1 from the open-issue register and align current project
   understanding and instructions with this record.
2. The approved skills and bootstrap source still need implementation.
   Only the standalone hello-world program and existing development tests
   are present.
3. Draft implementation tasks for review; do not create executable task
   records or start implementation without the user's confirmation.
4. No installation, new alias, project mapping, or tool execution is authorized.
   Each later installation requires its own preview and `Allow` / `Reject`.
5. Q2 remains open; no milestones are accepted by this decision. The GitHub
   rename remains pending and existing Git changes are preserved.
6. Keep records local. External sharing, commits, and pushes are not authorized.
