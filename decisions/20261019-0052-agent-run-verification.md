# Agent-run verification

**Date:** 2026-10-19

## Problem Description

The shared installation skill and each integration skill made functional
verification user-run and forbade the agent from running installed tools.
When the user asked to test hello-world, the agent handed over shell steps
instead of running `hello`. The user corrected this: integrations exist so the
agent can use them, so the agent must run them and show they work; user-run
verification is a fallback and a bonus for use outside the agent. Original
input: [agent-run verification](../inputs/2026-10-19-agent-run-verification.md).
The record filename and date use UTC.

## Decision

1. After installation, the agent runs the integration's declared verification
   itself and reports the output against the expected result.
2. User-run steps are a fallback, one at a time with expected results, only
   for steps the agent cannot perform, such as privileged installation,
   microphone or other interactive input, or activation in the user's own
   shell. The agent also gives the alias command for use outside the agent.
3. Installation finishes when verification passes; if it could not run,
   readiness is reported as unverified.
4. Installation approval covers the declared verification, not later
   consequential tool use.
5. In an agent's noninteractive Bash, bootstrap is sourced on its own line
   before the line that calls the alias.

## Explanation

This supersedes the user-run verification parts of
[guided installation until working](20261019-0014-guided-installation-until-working.md)
and the verification wording in the
[skill resources and user verification input](../inputs/2026-10-19-skill-resources-and-user-verification.md).
That input asked not to run the tool "silently" after installation; agent-run
verification is never silent, because the agent reports what it ran and what
it got. The approval gate is unchanged.

## Consequences

1. Update steps 9, 10, and 12 of `agent-hub/skills/install-integration/SKILL.md`.
2. Rename each integration skill's "User-run verification" to "Verification"
   and describe agent-run checks with a user fallback.
3. Update `AGENTS.md`, `README.md`, and `overview.md` to match.
4. Deployed copies change only through Agent Hub's normal skill update.
