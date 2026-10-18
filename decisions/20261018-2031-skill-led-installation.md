# Skill-led installation without a universal installer

**Date:** 2026-10-18

## Problem Description

Q1 requires a repeatable way to install integrations, configure aliases, verify
the result, and register completed installations. A universal installer was
proposed. The user questioned its need and approved skill-led installation
through established conventions instead.

## Decision

The installation skill owns the workflow. Each integration describes its
purpose, installation, dependencies and configuration, commands and aliases,
and verification. The skill uses that definition to install, configure,
verify, and register the integration.

Do not introduce a universal installer. Focused shared helpers may manage
aliases and registration safely. Tool-specific installation scripts are
optional and used only where useful.

## Explanation

Adding another integration should be easy once the conventions and shared
operations are implemented. A skill can follow tool-native installation
instructions without forcing every tool into a common installer framework.
Hello-world proves the process with a shell script, integration definition,
alias, and verification command.

This approval concerns the installation approach, not the exact file layout,
schema, skill wording, milestones, remote repository naming, or external
sharing.

## Consequences

1. Remove the proposed root installer from the current design.
2. Describe the integration contract and agent installation workflow.
3. Keep alias management and registration reusable rather than reimplementing
   them for each integration.
4. Review the file layout next, as requested by the user.
5. Preserve the Whisper requirements for later; hello-world remains the pilot.
6. Keep this decision local until external sharing is authorized.
