# Open Issues

This file contains only unresolved issues that currently require investigation or a decision.

**Next question ID:** Q4

## Q2: Project milestones

### Question

Which milestones and observable completion criteria should guide the project?

### Why It Matters

Milestones will make the first registration and later expansion reviewable without assuming an implementation plan.

### Context

The user now wants hello-world first to prove the integration process; Whisper
is on hold. No milestones have been agreed.

### Resolution Points

1. ❓ **Initial milestones**
   - **Resolution:** Pending
   - **Details:** Agree the intended sequence around the hello-world pilot.
2. ❓ **Completion criteria**
   - **Resolution:** Pending
   - **Details:** Define observable outcomes for each milestone.

### Proposals

**Problem:** Define observable progress for this first tooling blueprint without
inventing later product commitments.

1. **Prove the integration lifecycle with hello-world:**
   - M1, hello-world integration: a shell command, per-tool skill, Hub bootstrap,
     managed alias or bin command, Hub-level registration, and local installation.
   - Done when: first install, repeat install, alias execution, argument
     forwarding, Hub PATH activation, preservation of existing Hub content, and
     collision/failure handling and declared dependency checks pass. The
     installation preview and security-risk disclosure precede `Allow` /
     `Reject`; rejected or cancelled installation makes no changes.
     Installation leaves functional verification to the user and supplies
     manual steps without automatically executing the integration.
   - **Pros:** Establishes a tested minimum before real dependency management.
   - **Cons:** Whisper, dependency/model downloads, and other platforms remain
     future work.
