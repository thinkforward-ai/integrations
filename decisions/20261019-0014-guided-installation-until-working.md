# Guided installation until the integration works

**Date:** 2026-10-19

## Problem Description

The approved shared installation skill ended after file changes with manual
verification steps and readiness reported as unverified. During the first
installation of hello-world and say, a required native dependency
(`whisper.cpp`) still needed a user-run privileged install, and the skill gave
no direction to follow through. The user requires the installation skill to
guide them until the integration is fully installed and works, and approved
exact replacement wording. Original input:
[guided installation requirement](../inputs/2026-10-19-guided-installation-until-working.md).
The record filename and date use UTC.

## Decision

1. Replace step 10 of `install-integration` with guided completion: one
   remaining user-run step at a time, each with its expected result, waiting
   for the outcome before continuing.
2. The agent still does not automatically run the installed tool, its
   aliases, smoke tests, or self-tests.
3. On failure, the agent diagnoses with read-only inspection and proposes the
   next step. Changes beyond the approved plan need a new preview and
   `Allow` / `Reject`.
4. Installation finishes when the user confirms the integration works; if the
   user stops earlier, readiness is reported as unverified.
5. The skill description says it guides the user until the integration works.

## Explanation

This supersedes step 10 and the description wording in
[the skill-led integration design](20261018-2243-skill-led-integration-design.md).
Verification stays user-run and the approval gate in
[the installation approval decision](20261018-2204-installation-approval-gate.md)
is unchanged; the change is that the agent stays with the user through the
remaining steps instead of handing them a list.

## Consequences

1. Update `agent-hub/skills/install-integration/SKILL.md` with the approved
   wording.
2. Deployed copies change only through Agent Hub's normal skill update.
3. External sharing requires a separate request.
