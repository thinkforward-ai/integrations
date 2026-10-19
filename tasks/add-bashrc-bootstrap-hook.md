# Add the marked bootstrap hook to Agent Hub's installer

**Decision:** [Agent Hub installer adds a marked bootstrap hook to ~/.bashrc](../decisions/20261019-0034-bootstrap-hook-in-bashrc.md).

This is a reviewed task record only. Its creation does not authorize execution.

## What

Change these files, with paths relative to `/home/madkroll/thinkforward-ai/`:

1. `agent-hub/bin/install.sh`.
2. `agent-hub/README.md`.
3. `agent-hub/skills/install-integration/SKILL.md`.

Do not run the installer against the real `HOME` or Agent Hub home, and do
not change `agent-hub/bin/install.ps1`.

## Why

Implement the accepted decision so new interactive Bash shells load Hub PATH
and integration aliases without manual sourcing.

## How

1. Add a `--no-shell-hook` argument to `install.sh` argument parsing and
   `usage`.
2. Add one shared step to `install.sh` that runs on every successful path:
   fresh install, migration, and the "already set up" path that currently
   exits early.
   1. Deploy `bootstrap.sh`. On fresh install or migration, take it from the
      downloaded snapshot at `skills/install-integration/scripts/bootstrap.sh`;
      on the "already set up" path, take it from the installed
      `$AGENT_HUB_HOME/skills/agent-hub-install-integration/scripts/bootstrap.sh`.
      Create `$AGENT_HUB_HOME/bootstrap.sh` with mode `0644` only when it is
      absent. If it exists with different content, leave it unchanged and
      print a notice.
   2. Unless `--no-shell-hook` was given or `$HOME/.bashrc` already contains
      the line `# >>> agent-hub >>>`:
      1. If `$HOME/.bashrc` exists, copy it to
         `$AGENT_HUB_HOME/backups/bashrc-<yyyymmdd-hhmmss UTC>`.
      2. If the file is non-empty and does not end with a newline, append one.
      3. Append exactly this block; if `$HOME/.bashrc` is absent, create it
         with only the block:

         ```sh
         # >>> agent-hub >>>
         [ -f "${AGENT_HUB_HOME:-$HOME/.agent-hub}/bootstrap.sh" ] && . "${AGENT_HUB_HOME:-$HOME/.agent-hub}/bootstrap.sh"
         # <<< agent-hub <<<
         ```

      4. Print the changed path and the backup path.
3. In `README.md`, under "What the installer does", describe the bootstrap
   deployment, the marked `~/.bashrc` block, its backup, and removal by
   deleting the marked block. Show the opt-out as
   `curl -fsSL https://raw.githubusercontent.com/thinkforward-ai/agent-hub/main/bin/install.sh | bash -s -- --no-shell-hook`.
4. In `skills/install-integration/SKILL.md`, make these replacements and no
   other changes:
   1. Step 6. Current: "Do not introduce `.local`/`.config` storage or edit
      shell startup files." Replacement: "Do not introduce `.local`/`.config`
      storage or edit shell startup files; Agent Hub's installer owns the
      marked `~/.bashrc` bootstrap hook."
   2. Step 7. Current: "Deploy this skill's declared bootstrap resource as
      `bootstrap.sh` in Agent Hub home when needed." Replacement: "Deploy this
      skill's declared bootstrap resource as `bootstrap.sh` in Agent Hub home
      when it is missing or outdated."
   3. Step 9. Current: "Explain how to source Hub bootstrap in the shell that
      will invoke an alias." Replacement: "New interactive Bash shells load
      Hub bootstrap through the installer's `~/.bashrc` hook; explain opening
      a new terminal, or sourcing it in the current shell, scripts, or shells
      without the hook."

## Acceptance criteria

Checked against a temporary `HOME` and `AGENT_HUB_HOME` with a local copy of
the archive:

1. A fresh install creates `bootstrap.sh` and appends the block exactly once;
   rerunning the installer adds no second block.
2. A `.bashrc` without a trailing newline keeps all original lines intact, and
   the block starts on its own line.
3. A backup exists whenever an existing `.bashrc` was changed.
4. `--no-shell-hook` leaves `.bashrc` unchanged.
5. The "already set up" path adds a missing hook and bootstrap and otherwise
   makes no changes.
6. `bash -n bin/install.sh` passes.
7. The README and skill text match the decision and the replacements above.

## Prerequisites

1. The `agent-hub` checkout is on `main` and in sync with origin.
2. The existing uncommitted `skills/manage-skills/SKILL.md` change in
   `agent-hub` is preserved.

## Dependencies

None.
