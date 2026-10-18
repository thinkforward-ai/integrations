# Agent Instructions

## Project structure

1. `README.md`: repository entry point.
2. `overview.md`: current project statement, problem, scope, structure, and status.
3. `roadmap.md`: agreed milestones and progress; no milestones are agreed yet.
4. `open-issues.md`: unresolved issues only, with stable `Q<n>` identifiers.
5. `inputs/`: original input artifacts, preserved unchanged after capture.
6. `decisions/`: immutable records of explicitly accepted decisions.
7. `tasks/`: reviewed, decision-linked executable instructions with no open design choices.

## Working with the project

The project is named **Integrations**. Use integration as the primary term for
an agent-facing blueprint. Both the local directory and GitHub repository are
named `integrations`; origin is `git@github.com:thinkforward-ai/integrations.git`.

1. Read the overview and relevant issues, decisions, and tasks before making changes.
2. Keep provisional ideas distinct from accepted decisions. Do not infer approval.
3. Keep the overview current when the project's understanding changes. Describe
   the current state, not a journal of events or conversation recaps. Keep
   historical context in decisions and original inputs.
4. The project is AI-driven. Advance investigation and routine work without unnecessary questions, but obtain stakeholder approval for design decisions. The first integration is hello-world; Whisper is on hold. Q1's design and exact skill wording are approved in `decisions/20261018-2243-skill-led-integration-design.md`; source files are implemented but uncommitted; installation has not started.
5. Keep credentials, tokens, and private configuration values out of the repository.
6. Follow the per-tool-skill and Agent Hub ownership requirements in `overview.md`.
   Each tool skill must declare a dependency array. There is no shell-only
   restriction; see `decisions/20261018-2159-dependencies-and-language-choice.md`,
   which supersedes the earlier language restriction without changing ownership.
7. Before an integration installation changes anything, describe the plan,
   highlight major or critical security risks, then ask `Allow` / `Reject`.
   Proceed only after explicit `Allow`; rejection or cancellation makes no
   installation changes. See `decisions/20261018-2204-installation-approval-gate.md`.
8. Keep shared approval rules in the installation skill, not repeated in tool
   skills. Declare all tool resources in metadata. Leave verification to the
   user; do not automatically run installed tools to check them. Describe
   project capabilities as mapped onto integrations.
9. Follow the accepted design in
   `decisions/20261018-2243-skill-led-integration-design.md` where it supersedes
   earlier proposals: sourceable bootstrap bundled with the shared skill,
   generated local shell aliases, preserved resource-relative paths, no alias
   helper, no redundant bin commands, and no maintained installed-tool inventory.
   Design approval does not authorize implementation, installation, or external
   sharing. Create executable task records only after review.
