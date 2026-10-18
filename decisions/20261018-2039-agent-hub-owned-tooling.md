# Per-tool skills and Agent Hub-owned shell tooling

**Date:** 2026-10-18

## Problem Description

Q1 requires a clear division between tool-specific integration content and
shared runtime facilities. The user corrected the proposed file layout:
Python helpers, a generic installation skill, a separate conventions document,
XDG tool storage, `.bashrc` modifications, and a project-level installed-tool
registry do not match the intended design.

## Decision

1. Rename the project from Plugins to Integrations.
2. Give each tool its own installation skill. Supporting shell scripts are
   optional. Keep conventions in skills or the overview, not a standalone
   conventions document.
3. Use shell only for implementation and testing, not Python.
4. Agent Hub owns shared bootstrap, aliases, commands on PATH, installed tool
   files, and the registry of available installed tooling.
5. Store new runtime content only within Agent Hub or project directories.
   Do not introduce `.local`/`.config` tool storage or edit `.bashrc`.
6. Introduce Hub-level bootstrap that sources its aliases file and prepares
   Hub's bin PATH entry. Ubuntu uses real shell aliases or bin commands;
   Windows alternatives are deferred.

## Explanation

The Integrations repository supplies tool-specific skills compatible with
Agent Hub's root `skills/` discovery. Agent Hub provides the shared user-level
runtime and installed-tool inventory. This refines
`20261018-2031-skill-led-installation.md` without editing that immutable record.

The requirements authorize the ownership boundaries and project rename, not
an invented activation mechanism or exact skill wording. A child process cannot
change its parent shell's PATH or aliases. The bootstrap's activation boundary
still requires clarification.

## Consequences

1. The local directory has been renamed to
   `/home/madkroll/thinkforward-ai/integrations`, preserving Git and uncommitted
   content. Remote repository renaming remains unperformed: Git SSH access
   alone cannot rename a GitHub repository, and authenticated management
   tooling is not currently available.
2. Replace the earlier unaccepted file-layout proposal with per-tool skills
   and Agent Hub-owned runtime paths.
3. Preserve existing installed Hub content, especially `bin/say`, `tools/say/`,
   and `aliases.sh`.
4. Review the Hub bootstrap activation boundary and exact skill changes before
   implementing them. Keep hello-world as the pilot and Whisper on hold.
5. Keep these records local until external sharing is authorized.
