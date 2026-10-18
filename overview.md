# Overview

## Name and purpose

**Integrations** provides reusable blueprints through which agents integrate
with tools and services. An integration can combine tools, connectors, models,
skills, configuration, scripts, aliases, and guidance.

The user approved the project name and local rename from `plugins` to
`integrations`. The repository is at
`/home/madkroll/thinkforward-ai/integrations`; its origin still points to
`git@github.com:thinkforward-ai/plugins.git`. The GitHub rename remains pending.

## Accepted design

Q1 is resolved by the
[approved design and exact skill texts](decisions/20261018-2243-skill-led-integration-design.md).
That decision supersedes earlier proposals where they conflict. Earlier
decisions and raw inputs remain unchanged as history.

1. Agent Hub supplies the generic installation skill and reusable Bash
   bootstrap. The bootstrap is bundled under the shared skill's `scripts/`
   directory and copied to Agent Hub home when needed.
2. Integrations supplies per-tool skills, dependencies, resources, aliases,
   usage, and additional instructions. Tool skills do not choose installation
   roots or repeat shared approval policies. There is no universal installer.
3. Each tool skill declares dependency and resource arrays in metadata,
   using `[]` when empty. All source resources belong in metadata.
   For native tools, `command` names an OS executable; for custom tools, it
   identifies an executable resource relative to the resource root.
4. Native tools remain OS-managed. Custom resources retain their relative
   paths under `${AGENT_HUB_HOME:-$HOME/.agent-hub}/tools/<id>/`.
   Do not create redundant bin links or wrappers merely to expose a tool.
5. Optional aliases are real shell aliases. Store selected bindings in local
   `aliases.sh`; do not create an empty default file or a separate alias helper.
   Preserve existing selections, unmanaged names, and unrelated content.
   Quote paths and default arguments safely; never evaluate metadata as code.
6. Bootstrap resolves Hub home, adds an existing Hub bin directory to PATH
   without duplication, enables Bash alias expansion, and loads local aliases
   when present. It performs no installation, file writes, or tool verification.
   It must be sourced in the invoking shell. Aliases do not propagate to child
   processes and must be loaded before commands using them are parsed.
7. Before any installation changes, describe the plan, highlight major or
   critical security risks and material uncertainties, then ask `Allow` /
   `Reject`. Proceed only on explicit `Allow`. Rejection, cancellation, or no
   answer makes no installation changes. Material changes require another
   preview and approval.
8. Verification belongs to the user. Provide manual steps and expected results;
   do not automatically run tools, aliases, smoke tests, or self-tests after
   installation. Report functional readiness as unverified until confirmed.
9. Discover known integrations from metadata, command locations, and files,
   without executing integration commands. Listing does not install,
   authenticate, download, activate configuration, or change preferences.
   There is no maintained installed-tool inventory or duplicate alias registry.
10. Project capabilities are mapped onto integrations in the project's
    `capabilities.md`, created only when mapping is requested. Preserve
    unrelated mappings, omit machine-specific installation state, and do not
    create aliases merely because a capability mapping exists.
11. No new `.local`/`.config` storage or shell-startup edits. Implementation
    languages are unrestricted. Preserve existing Hub content, including
    `bin/say`, `tools/say/`, and `aliases.sh`. Ubuntu/Bash comes first; Windows
    alternatives remain deferred.

## Pilot and implementation status

1. Hello-world is the first integration; Whisper remains on hold.
2. `skills/hello-world/scripts/hello-world.sh` is the existing standalone
   program. It prints `Hello, world!`, accepts an optional name, and supports
   help. Ten development checks passed earlier; no tests were run as part of
   accepting the design.
3. The shared skill, its bootstrap resource, and the hello-world `SKILL.md`
   have not been created. No new tool, alias, or project capability mapping
   has been installed.
4. The approved sample preserves `scripts/hello-world.sh` under the installed
   tool root and declares the optional alias `hello`. No `bin/hello` or
   `bin/hello-world` is required.
5. Design approval does not authorize implementation or installation.
   Implementation tasks must be reviewed before task records are created.
   Each installation later requires its own preview and `Allow` / `Reject`.
6. Agent Hub source is `/home/madkroll/thinkforward-ai/agent-hub`; its installed
   home is `/home/madkroll/.agent-hub`. Existing Hub content is preserved.
   No bootstrap has been deployed or activated by this work.
7. Model-installation requirements for Whisper still include English-only
   and multilingual models. Earlier downloads and checks are evidence, not
   microphone or Russian-speech verification.

## Collaboration and milestones

1. **Mode:** Solo, explicitly confirmed by the user.
2. **Driving:** AI-driven, with stakeholder approval for design decisions.
3. No milestones have been agreed. [Q2](open-issues.md#q2-project-milestones)
   remains open, and [the roadmap](roadmap.md) is unchanged.
4. The reviewed [source-only implementation task](tasks/implement-approved-integration-sources.md)
   is recorded. Task execution and installation remain unauthorized. The user
   has authorized committing and pushing the project records and pilot source.

## Original inputs

1. [Initial idea](inputs/2026-10-18-initial-idea.md).
2. [Whisper blueprint request](inputs/2026-10-18-whisper-blueprint-request.md).
3. [Earlier Capabilities concept](inputs/2026-10-18-capabilities-concept.md).
4. [Integrations name](inputs/2026-10-18-integrations-name.md).
5. [Hello-world request](inputs/2026-10-18-hello-world-request.md).
6. [Agent Hub requirements](inputs/2026-10-18-agent-hub-tooling-requirements.md).
7. [Two-skill split](inputs/2026-10-18-two-skill-installation.md).
8. [Optional aliases](inputs/2026-10-18-optional-alias-providers.md).
9. [System-managed tools](inputs/2026-10-18-system-installed-tooling.md).
10. [Discovery discussion](inputs/2026-10-18-capability-discovery-discussion.md).
11. [Project capabilities](inputs/2026-10-18-project-capabilities.md).
12. [Dependencies and language choice](inputs/2026-10-18-dependencies-and-language-choice.md).
13. [Installation approval gate](inputs/2026-10-19-installation-approval-gate.md).
14. [Resources and user verification](inputs/2026-10-19-skill-resources-and-user-verification.md).
15. [Proposal approval](inputs/2026-10-19-proposal-approval.md).
