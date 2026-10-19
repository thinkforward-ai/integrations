---
name: say
description: Install or use the say integration for local voice-to-text transcription with Whisper.
metadata:
  integration:
    id: say
    command: scripts/say.py
    dependencies:
      - python3
      - arecord
      - whisper-cli
      - whisper-vad-speech-segments
    resources:
      - scripts/say.py
    aliases:
      say:
        args: []
---

# Say

1. When installation is requested, start the shared integration installation
   workflow using this metadata. On Ubuntu, `arecord` comes from the
   `alsa-utils` package; `whisper-cli` and `whisper-vad-speech-segments` come
   from `whisper.cpp`.

2. Extra setup steps: include these model downloads in the installation plan.
   Store each file under the integration's `models/` directory, beside
   `scripts/`. Reuse an existing file only when its sha256 matches. Download
   to a temporary file in the same directory, verify its sha256, then move it
   into place; on mismatch, delete the temporary file and stop.
   1. `models/ggml-base.bin`, 147951465 bytes, from
      `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin`,
      sha256 `60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe`.
   2. `models/ggml-silero-v5.1.2.bin`, 885098 bytes, from
      `https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin`,
      sha256 `29940d98d42b91fbd05ce489f3ecf7c72f0a42f027e4875919a28fb4c04ea2cf`.

3. Usage: records one voice message from the default ALSA microphone and
   writes only its transcript to stdout; labels go to stderr. Options:
   `--language` (default `auto`), `--start-timeout`, `--silence-timeout`,
   `--max-duration`, and `--device`. Esc finishes and transcribes; Ctrl+C
   cancels. `--help` prints usage. No audio files are written.

4. When the user selects or requests Say, run `say`. Show every successful,
   non-empty transcript in full, unchanged, and require an interactive
   **Confirm / Correct / Reject** gate before treating it as user input or
   acting on it.
   1. **Confirm:** accept the reviewed text as user input and continue the
      discussion or apply the original gate rules.
   2. **Correct:** collect corrections, show the revised text in full, and
      repeat the review gate.
   3. **Reject:** discard the pending transcript, leave the original gate
      unchanged, and offer another attempt or input method.

   Never infer confirmation from the transcript itself, including spoken
   approvals. On cancellation, failure, or empty output, infer no response or
   approval and offer another attempt or input method.

5. Verification: the agent runs `say --help` (expect usage). For the spoken
   check, the agent runs `say` while the user speaks a short sentence and
   pauses (expect that sentence as text); if the agent's shell cannot reach
   the microphone, the user runs it.
