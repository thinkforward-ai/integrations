# Dependency arrays and unrestricted implementation languages

**Date:** 2026-10-18

## Problem Description

Q1's skill contract needs to cover dependencies beyond a tool's direct command.
Inspection of the finished `say` implementation identified a Python runtime,
native commands, and model assets. The earlier shell-only restriction conflicts
with allowing such an implementation.

## Decision

1. Each tool skill must mention an array of dependencies.
2. Shell-only implementation is no longer a limitation.

## Explanation

The language clarification supersedes item 3 of
[the earlier ownership decision](20261018-2039-agent-hub-owned-tooling.md)
and its shell-only interpretation elsewhere. It applies to shared helpers,
tool implementations, and tests. It does not change Agent Hub ownership,
storage constraints, startup-file protections, or the two-skill split.

The dependency requirement includes necessary runtimes. The current draft
places the array at `metadata.integration.dependencies`, with `[]` for no
dependencies and tool-specific instructions for installation and verification.
That metadata placement and the remaining exact skill text are still proposals.

Original input:
[dependency and language clarification](../inputs/2026-10-18-dependencies-and-language-choice.md).

## Consequences

1. Update active requirements and skill drafts to include the dependency array
   and remove the shell-only restriction.
2. Preserve existing decisions and raw inputs unchanged as history.
3. Do not rewrite the finished `say` implementation merely because it uses
   Python. This decision does not authorize tool installation or migration.
4. No additional executable tasks or milestone changes are established.
   Exact skill text and runtime design remain under review.
5. Keep these records local until external sharing is authorized.
