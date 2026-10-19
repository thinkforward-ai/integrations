# Integrations

Reusable blueprints through which agents integrate with tools and services.

An integration can combine tools, connectors, models, skills, configuration,
scripts, aliases, and guidance. Examples include speech-to-text, cloud operations,
image editing, and video editing.

The pilot integration is a hello-world shell command, used to prove shared
installation, shell aliases, and project capability mapping. The `say`
integration provides local voice-to-text with Whisper. Installation is
skill-led, following shared conventions rather than a universal installer.

The installation workflow must explain planned changes, highlight major or
critical security risks, and ask **Allow / Reject** before making changes.
It leaves verification to the user rather than automatically running the tool.

Each tool has its own installation skill, a declared dependency array, and
all resources listed in metadata. Supporting scripts are optional.
Implementation and tests are not limited to shell.
Shared conventions live in skills and the project overview, not a separate
conventions file. Agent Hub supplies a sourceable bootstrap bundled with its
shared installation skill. Local aliases are generated under Agent Hub home;
custom resources retain their relative paths under `tools/<id>/`. Native tools
stay OS-managed. Project capabilities are mapped onto integrations. There is
no maintained installed-tool inventory or redundant bin command requirement.

The [design and exact skill texts are approved](decisions/20261018-2243-skill-led-integration-design.md).

Development checks are `./tests/hello-world.sh`, `./tests/say/test_say.sh`, and
`python3 -m unittest discover -s tests/say`. The say checks need the models in
the ignored `skills/say/models/`. The installation workflow does not run them
automatically.

## Project records

1. [Overview](overview.md): current understanding and unresolved scope.
2. [Roadmap](roadmap.md): milestones, once agreed.
3. [Open issues](open-issues.md): questions requiring clarification or a decision.
4. [Inputs](inputs/): original source material.
5. [Decisions](decisions/): accepted decisions.
6. [Tasks](tasks/): reviewed, decision-linked executable work.

See [AGENTS.md](AGENTS.md) for repository guidance.
