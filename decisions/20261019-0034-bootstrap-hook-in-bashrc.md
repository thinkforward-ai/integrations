# Agent Hub installer adds a marked bootstrap hook to ~/.bashrc

**Date:** 2026-10-19

## Problem Description

Q3: every new shell needed `source ~/.agent-hub/bootstrap.sh` before an
integration alias worked. The user asked that Agent Hub installation add the
bootstrap to the local user startup files
([input](../inputs/2026-10-19-bootstrap-in-startup-files.md)). This reverses
the accepted no-startup-file-edit constraint in
[Agent Hub owned tooling](20261018-2039-agent-hub-owned-tooling.md) and
[the skill-led integration design](20261018-2243-skill-led-integration-design.md).

Facts: Agent Hub's installer runs without prompts and did not deploy
`bootstrap.sh`; the `install-integration` skill did. Ubuntu's `~/.bashrc`
returns early for non-interactive shells and `~/.profile` sources it for login
Bash. The bootstrap writes no files and does nothing without `aliases.sh` or
`bin/`. A local `~/.bashrc` showed two lines joined by an earlier installer
that appended without a trailing newline.

Proposals considered: (1) the installer adds a marked hook to `~/.bashrc`;
(2) the same with per-shell hooks including `~/.zshrc`; (3) the
`install-integration` skill adds the hook at the first integration install
under its approval gate. The user chose proposal 1. The record filename and
date use UTC.

## Decision

1. Agent Hub's installer deploys `bootstrap.sh` to Agent Hub home. The
   `install-integration` skill keeps deploying or refreshing it when missing
   or outdated.
2. The installer appends this block to `~/.bashrc` when the markers are
   absent:

   ```sh
   # >>> agent-hub >>>
   [ -f "${AGENT_HUB_HOME:-$HOME/.agent-hub}/bootstrap.sh" ] && . "${AGENT_HUB_HOME:-$HOME/.agent-hub}/bootstrap.sh"
   # <<< agent-hub <<<
   ```

3. Before editing, it backs up `~/.bashrc`, adds a newline first if the file
   does not end with one, and never rewrites other lines. It creates
   `~/.bashrc` only with the block when the file is absent.
4. It skips the edit when the markers already exist, prints what it changed,
   and accepts `--no-shell-hook` to opt out.
5. Removal deletes the marked block.
6. Scope is interactive Bash. zsh, PowerShell, and non-interactive shells are
   out of scope; scripts and agent tool shells keep sourcing the bootstrap
   explicitly.

## Explanation

This supersedes the "do not edit `.bashrc`/shell startup files" rule of the
two earlier decisions for this one marked block only; other startup-file edits
remain prohibited. Ownership stays with Agent Hub. Whether agent tool shells
that snapshot an interactive profile pick up the aliases is unverified and is
left to user checking. zsh coverage can be proposed later once the bootstrap is
checked under zsh.

## Consequences

1. Update Agent Hub's `bin/install.sh` and README accordingly.
2. Update `install-integration` so step 6 permits only this marked block,
   step 7 treats an installer-deployed bootstrap as already present, and
   step 9 says new interactive Bash shells load the bootstrap automatically.
3. Update `overview.md` and `AGENTS.md` in this project.
4. Existing installations gain the hook when the installer is rerun.
