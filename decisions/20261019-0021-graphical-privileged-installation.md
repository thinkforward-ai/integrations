# Graphical approval for privileged installation

**Date:** 2026-10-19

## Problem Description

Installing say's native `whisper.cpp` dependency needed root. The agent's
shell cannot answer a `sudo` password prompt (`sudo -n true` reports that
interactive authentication is required), and the user wants installation to
be usable by people who are not comfortable with the command line. In the
local graphical session, `pkexec /usr/bin/apt-get install -y whisper.cpp`
showed the desktop password dialog and the install succeeded. The user
adopted this as a reviewed learning with exact wording. The record filename
and date use UTC.

## Decision

Add to step 6 of `install-integration`, after "follow the approved OS
installation process":

> When privileged installation is needed and `sudo` cannot prompt, use
> `pkexec` in a local active graphical session so the user approves in the
> desktop password dialog; otherwise give the user the command to run.

## Explanation

The privileged command still appears in the installation plan and requires
`Allow` before it runs; the desktop dialog is the OS-level authentication,
not a replacement for the approval gate. Without a local active graphical
session, the user runs the command themselves, as in the
[guided installation decision](20261019-0014-guided-installation-until-working.md).

## Consequences

1. Update `agent-hub/skills/install-integration/SKILL.md` step 6.
2. Deployed copies change only through Agent Hub's normal skill update.
