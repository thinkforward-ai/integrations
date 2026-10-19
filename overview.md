# Overview

## Project statement

**Integrations** provides reusable blueprints through which agents integrate
with tools and services. An integration can combine tools, connectors, models,
skills, configuration, scripts, aliases, and guidance.

Repository: `git@github.com:thinkforward-ai/integrations.git`.

## Problem

Agents need a consistent way to discover, install, configure, and use
integrations without duplicating installation rules in every tool skill or
maintaining an inventory that can become stale. Users need clear installation
plans, security-risk disclosure, explicit approval, and control over verification.

## Scope and responsibilities

1. **Agent Hub:** shared installation skill, reusable sourceable Bash bootstrap,
   installation destinations, and local alias configuration.
2. **Integrations:** per-tool skills with metadata describing dependencies,
   all resources, commands, and optional aliases; usage and additional
   instructions remain in the skill body.
3. **Projects:** capabilities mapped onto integrations in `capabilities.md`,
   created only when mapping is requested. Capability mapping does not
   automatically create a command alias.
4. **Operating system:** native package installation and native command
   locations. Hub management does not require copying or wrapping OS tools.

## Structure

Approved source structure:

```text
agent-hub/
└── skills/install-integration/
    ├── SKILL.md
    └── scripts/bootstrap.sh

integrations/
└── skills/
    ├── hello-world/
    │   ├── SKILL.md
    │   └── scripts/hello-world.sh
    └── say/
        ├── SKILL.md
        └── scripts/say.py
```

1. Custom resources retain their relative paths under
   `${AGENT_HUB_HOME:-$HOME/.agent-hub}/tools/<id>/`.
2. The reusable bootstrap is deployed as `bootstrap.sh` in Agent Hub home.
   It prepares PATH and alias expansion, then sources local `aliases.sh`
   when present. It must be sourced in the shell that invokes the alias.
3. Selected shell aliases are local artifacts in `aliases.sh`, not separate
   command files. No empty default alias file or alias-management helper is
   required. Aliases are not inherited by child processes.
4. Detailed metadata and exact skill text are specified in the
   [approved design](decisions/20261018-2243-skill-led-integration-design.md).
5. Large downloaded artifacts, such as models, are not stored in Git. A tool
   skill declares them as extra setup steps with pinned URLs and sha256 values;
   see the [say design](decisions/20261018-2322-say-integration.md).

## Operating constraints

1. Installation is skill-led, without a universal installer. Shared policies
   belong in the installation skill, not repeated in each tool skill.
2. Dependency and resource arrays are required metadata; use `[]` when empty.
   A native command is an OS executable name; a bundled command is an
   executable path relative to its resource root.
3. Installation requires a clear plan, disclosure of major or critical
   security risks, and an explicit `Allow` / `Reject` gate before changes.
   Material changes to the plan or risks require fresh approval.
4. Functional verification is user-run. Installation and discovery do not
   automatically execute tools, aliases, smoke tests, or self-tests.
   Command/file presence is not proof of functional readiness. Installation
   guides the user one step at a time until the user confirms the integration
   works; see the
   [guided installation decision](decisions/20261019-0014-guided-installation-until-working.md).
5. Discovery uses metadata, command locations, and files without executing
   integration commands or changing configuration. There is no maintained
   installed-tool inventory or duplicate alias registry.
6. Preserve existing tools, aliases, user selections, and unrelated files.
   No redundant bin links or wrappers, new `.local`/`.config` storage, or shell
   startup-file edits. Managed content stays within Hub or project directories;
   native packages use OS locations.
7. Implementation languages are unrestricted. The initial environment is
   Ubuntu/Bash; Windows support is deferred.

## Current status and open work

1. **Pilot:** hello-world. Its standalone program and development tests exist.
   The sample declares the optional alias `hello`.
2. **Say:** local voice-to-text with Whisper. Its program, development tests,
   and skill exist; the skill downloads the multilingual base and Silero
   speech-detection models. It declares the optional alias `say`.
3. **Implementation:** the shared skill, bootstrap resource, and both tool
   skills exist in their repositories.
4. **Deployment:** hello-world and say, the bootstrap, and the `hello` and
   `say` aliases are installed in the local Agent Hub home, with say's native
   `whisper.cpp` dependency. The user confirmed both work. No project capability mapping exists.
5. **Other Whisper models:** on hold, including English-only models.
6. **Milestones:** unresolved in
   [Q2](open-issues.md#q2-project-milestones); no milestones are agreed in the
   [roadmap](roadmap.md).

## Collaboration

1. **Mode:** Solo.
2. **Driving:** AI-driven, with stakeholder approval for design decisions,
   explicit requests for task execution, and separate installation approval.
