# Say integration with pinned model downloads

**Date:** 2026-10-18

## Problem Description

The local Agent Hub home contains a manually installed `say` voice-to-text
tool: a Python program in `bin/`, Whisper models and tests under `tools/say/`,
and an alias in `aliases.sh`. Before cleaning it up, the user wants `say`
captured as an integration in this project with the skill needed to install it.
Whisper had been on hold, and the approved design defines resources only as
files within a skill directory. The multilingual model (148 MB) exceeds
GitHub's 100 MB per-file limit. Original response:
[say integration request](../inputs/2026-10-19-say-integration-request.md).
The record filename and date use UTC.

## Decision

1. Add the `say` integration with id `say` and the optional alias `say`.
2. Lift the Whisper hold for `say` only: the multilingual `ggml-base.bin`
   transcription model and the `ggml-silero-v5.1.2.bin` speech-detection model.
   English-only and other Whisper models remain on hold.
3. Do not store models in Git. Installation downloads each model from its
   pinned Hugging Face URL and verifies its sha256 before use.
4. Declare the model downloads as extra setup steps in the `say` skill body.
   The approved shared installation skill and metadata schema remain unchanged.
5. Native dependencies remain OS-managed: `python3`, `alsa-utils` for
   `arecord`, and `whisper.cpp` for `whisper-cli` and
   `whisper-vad-speech-segments`.

## Explanation

The shared skill already reads a tool skill's additional instructions, so
body-level download steps fit the accepted design without amending it.
Pinned URLs with sha256 values keep installation reproducible and avoid Git LFS.

### Source layout

```text
integrations/
├── skills/say/
│   ├── SKILL.md
│   └── scripts/say.py
└── tests/say/
    ├── test_say.py
    ├── test_say.sh
    └── test_say_terminal.py
```

### Installed layout

```text
~/.agent-hub/tools/say/
├── scripts/say.py
└── models/
    ├── ggml-base.bin
    └── ggml-silero-v5.1.2.bin
```

The program resolves models from `models/` beside its `scripts/` directory,
so the source and installed layouts share the same relative paths.

### Pinned models

1. `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin`,
   147951465 bytes, sha256
   `60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe`.
2. `https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin`,
   885098 bytes, sha256
   `29940d98d42b91fbd05ce489f3ecf7c72f0a42f027e4875919a28fb4c04ea2cf`.

## Consequences

1. Add the `say` skill, program, and development tests to this repository.
   Ignore development model copies under `skills/say/models/`.
2. Cleanup of the existing Hub `say` installation and any later installation
   remain separate actions; installation requires its own preview and
   `Allow` / `Reject`.
3. English-only and other Whisper models remain on hold.
