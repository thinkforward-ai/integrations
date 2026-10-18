# Name the project Integrations

**Date:** 2026-10-18

## Problem Description

Q1 includes the meaning and purpose of this project. Naming options discussed
included Plugins, Agent Tooling, Agent Toolkit, Capabilities, and Integrations.
The user initially liked Capabilities, then explicitly chose Integrations.

## Decision

Use **Integrations** as the project name and integration as the primary term
for an agent-facing blueprint.

## Explanation

The name should make it clear to the community that agents can integrate
through these blueprints. Integrations may cover local tools, cloud services,
image editing, video editing, speech recognition, and other capabilities.
They may combine tools, connectors, models, skills, configuration, aliases,
scripts, and guidance.

This naming choice does not approve the proposed installer architecture,
registry format, platform support, milestones, or a remote repository rename.

## Consequences

1. Update current project descriptions and proposals to use Integrations.
2. Preserve original input artifacts, including the earlier Capabilities input.
3. Keep the existing `plugins` repository and local directory unchanged.
4. Leave Q1 open for the remaining implementation conventions and Q2 open for
   milestone approval.
5. Keep this decision local until external sharing is authorized.
