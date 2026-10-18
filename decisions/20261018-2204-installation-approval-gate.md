# Installation preview, security risks, and explicit approval

**Date:** 2026-10-18

## Problem Description

Q1's shared installation workflow needs a user-visible boundary between
planning an installation and performing it. The user requires a clear
description, disclosure of major or critical security risks, and an explicit
approval gate before installation changes.

## Decision

1. The shared `install-integration` skill first describes the installation so
   the user understands what will happen.
2. It highlights and explains any major or critical security risks of running
   that installation.
3. It then asks the user to choose `Allow` or `Reject`.
4. Installation changes begin only after explicit `Allow`.

## Explanation

The preview covers dependencies, sources, commands, privileges, affected files
and configuration, verification, and rollback limits. Security disclosure
explains significant risks, impact, mitigations, and material uncertainties.
Not identifying a major or critical risk is not a guarantee of safety.

Only trusted read-only inspection may precede approval. Downloading payloads,
running installers, staging files, and changing packages, aliases, or project
configuration wait for approval. Rejection, cancellation, or no answer makes
no installation changes. Material changes to the disclosed plan or risks
require a fresh preview and approval.

Read-only listing remains non-mutating and does not need installation
approval. `Allow` covers the described installation, not later consequential
use of the installed integration.

Original input:
[installation approval requirement](../inputs/2026-10-19-installation-approval-gate.md).

## Consequences

1. Update the active requirements and shared workflow draft with the ordered
   preview, security-risk disclosure, and `Allow` / `Reject` gate.
2. Tool skills delegate to that workflow without bypassing its approval gate.
3. Validate rejection and cancellation leave installation unchanged when the
   workflow is implemented.
4. Preserve earlier decisions and installed tooling. The remaining exact
   skill wording and runtime design are still under review; no installation,
   additional executable task, or milestone change is authorized here.
5. Keep these records local until external sharing is authorized.
