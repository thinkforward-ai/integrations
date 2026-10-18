#!/usr/bin/env python3
"""Record one voice message and return its transcript, without recording files."""

import argparse
from contextlib import contextmanager
import io
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import sys
import termios
import time
import tty
import wave


RATE = 16000
CHUNK_BYTES = 6400  # Analyze every 200 ms, using up to two seconds of context.
WINDOW_BYTES = 64000
MODEL = Path(__file__).resolve().parents[1] / "models/ggml-base.bin"
VAD_MODEL = MODEL.with_name("ggml-silero-v5.1.2.bin")


class NoSpeech(Exception):
    pass


def log(label, message):
    for line in str(message).splitlines():
        print(f"[{label}] {line}", file=sys.stderr, flush=True)


def output_transcript(transcript):
    print("\n----- SPEECH TRANSCRIPT -----", file=sys.stderr, flush=True)
    print(transcript, flush=True)
    print("----- END TRANSCRIPT -----", file=sys.stderr, flush=True)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        log("ERROR", message)
        log("USAGE", self.format_usage().strip())
        self.exit(1)


def positive_seconds(value):
    if not value.isascii() or not value.isdecimal() or not 0 < int(value) < 100000:
        raise argparse.ArgumentTypeError("Use a positive integer below 100000.")
    return int(value)


def wav_bytes(pcm):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(RATE)
        audio.writeframes(pcm)
    return buffer.getvalue()


def speech_end(pcm):
    result = subprocess.run(
        ["whisper-vad-speech-segments", "-f", "-", "-vm", str(VAD_MODEL),
         "-np", "-t", "1", "-vt", "0.6"],
        input=wav_bytes(pcm), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=3, start_new_session=True, env={**os.environ, "LC_ALL": "C"},
    )
    output = result.stdout.decode("utf-8", errors="replace")
    count = re.search(r"Detected (\d+) speech segments:", output)
    ends = re.findall(r"Speech segment \d+: start = [\d.]+, end = ([\d.]+)", output)
    if result.returncode or count is None or int(count[1]) != len(ends):
        diagnostic = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Speech detection failed: {diagnostic[-1000:]}")
    if not ends:
        return None
    # This native tool reports segment timestamps in centiseconds.
    return min(len(pcm) / (RATE * 2), max(float(end) / 100 for end in ends))


@contextmanager
def finish_key():
    try:
        keyboard = os.open("/dev/tty", os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY)
    except OSError:
        yield None
        return
    original, enabled = None, False
    try:
        try:
            if os.tcgetpgrp(keyboard) == os.getpgrp():
                original = termios.tcgetattr(keyboard)
                # Keep Ctrl+C signals and queued input; do not wait for Enter.
                tty.setcbreak(keyboard, termios.TCSANOW)
                enabled = True
        except (OSError, termios.error):
            pass
        yield keyboard if enabled else None
    finally:
        try:
            if original is not None:
                termios.tcsetattr(keyboard, termios.TCSANOW, original)
        finally:
            os.close(keyboard)


def stop(process, *, drain=False):
    try:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if drain:
            os.set_blocking(process.stdout.fileno(), False)
            return process.stdout.read() or b""
        return b""
    finally:
        process.stdout.close()


def record(args):
    audio, pending, window = bytearray(), bytearray(), bytearray()
    last_speech = None
    finished = False
    recorder = subprocess.Popen(
        ["arecord", "-q", "-D", args.device, "-t", "raw", "-f", "S16_LE",
         "-r", str(RATE), "-c", "1", "-B", "100000", "-F", "20000"],
        stdout=subprocess.PIPE, stderr=sys.stderr, bufsize=0, start_new_session=True,
    )
    started = time.monotonic()
    try:
        with finish_key() as keyboard, selectors.DefaultSelector() as selector:
            log(
                "INSTRUCTION",
                f"Speak now. No speech for {args.start_timeout}s cancels; "
                f"pause {args.silence_timeout}s after speaking to finish. "
                + ("Esc finishes and transcribes. " if keyboard is not None
                   else "Esc unavailable without a foreground terminal. ")
                + "Ctrl+C cancels.",
            )
            selector.register(recorder.stdout, selectors.EVENT_READ, "audio")
            if keyboard is not None:
                selector.register(keyboard, selectors.EVENT_READ, "keyboard")
            while True:
                deadline = min(
                    started + args.max_duration,
                    last_speech + args.silence_timeout if last_speech is not None
                    else started + args.start_timeout,
                )
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                ready = selector.select(timeout=min(0.1, remaining))
                if not ready:
                    if recorder.poll() is not None:
                        raise RuntimeError("Microphone capture failed.")
                    continue
                if any(key.data == "keyboard" for key, _ in ready):
                    keys = os.read(keyboard, 1024)
                    if b"\x1b" in keys:
                        finished = True
                        log("STATUS", "Recording finished with Esc.")
                        break
                    if not keys:
                        selector.unregister(keyboard)
                if not any(key.data == "audio" for key, _ in ready):
                    continue
                chunk = recorder.stdout.read(CHUNK_BYTES)
                if not chunk:
                    raise RuntimeError("Microphone capture stopped unexpectedly.")
                pending.extend(chunk)
                while len(pending) >= CHUNK_BYTES:
                    frame = bytes(pending[:CHUNK_BYTES])
                    del pending[:CHUNK_BYTES]
                    audio.extend(frame)
                    window.extend(frame)
                    del window[:-WINDOW_BYTES]
                    capture_time = time.monotonic()
                    end = speech_end(window)
                    if end is not None:
                        if last_speech is None:
                            log("STATUS", "Speech detected.")
                        detected_at = capture_time - (len(window) / (RATE * 2) - end)
                        last_speech = max(last_speech or detected_at, detected_at)
    finally:
        pending.extend(stop(recorder, drain=finished))
    audio.extend(pending[: len(pending) // 2 * 2])
    if finished and not audio:
        raise NoSpeech("No audio recorded.")
    if not finished and last_speech is None:
        raise NoSpeech("No speech detected before the initial timeout.")
    return bytes(audio)


def transcribe(pcm, language):
    log("STATUS", "Transcribing locally...")
    result = subprocess.run(
        ["whisper-cli", "-m", str(MODEL), "-f", "-", "-l", language,
         "-nt", "-np", "-ng", "-t", "4", "-otxt", "-of", "-"],
        input=wav_bytes(pcm), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=180, start_new_session=True,
    )
    if result.returncode:
        diagnostic = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Transcription failed: {diagnostic[-1000:]}")
    transcript = result.stdout.decode("utf-8", errors="replace").strip()
    if transcript.lower() in ("", "[music]", "[blank_audio]", "[silence]", "[no speech]"):
        raise NoSpeech("No usable speech was transcribed.")
    return transcript


def main(argv=None):
    parser = Parser(
        description="Capture one voice message; write only its transcript to stdout.",
        epilog="Recording starts immediately. Native speech detection controls stopping, "
               "not audio volume. Vocals or other voices can still count as speech. "
               "Press Esc while recording to finish and transcribe captured audio; "
               "Ctrl+C cancels without a transcript. Esc requires a foreground terminal "
               "and also works when stdout is piped. "
               "Labels and transcript markers go to stderr; stdout stays transcript-only. "
               "No audio files or pip packages.",
    )
    parser.add_argument("--language", default="auto", help="Language code, e.g. en or ru (default: auto).")
    parser.add_argument("--start-timeout", type=positive_seconds, default=5, metavar="SECONDS")
    parser.add_argument("--silence-timeout", type=positive_seconds, default=5, metavar="SECONDS")
    parser.add_argument("--max-duration", type=positive_seconds, default=120, metavar="SECONDS")
    parser.add_argument("--device", default="default", help="ALSA microphone device (default: default).")
    args = parser.parse_args(argv)
    try:
        for command in ("arecord", "whisper-cli", "whisper-vad-speech-segments"):
            if shutil.which(command) is None:
                raise RuntimeError(f"Required command unavailable: {command}")
        if not MODEL.is_file():
            raise RuntimeError("The transcription model is missing.")
        if not VAD_MODEL.is_file():
            raise RuntimeError("The speech-detection model is missing.")
        output_transcript(transcribe(record(args), args.language))
        return 0
    except NoSpeech as error:
        log("STATUS", error)
        return 2
    except KeyboardInterrupt:
        log("STATUS", "Cancelled.")
        return 130
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        log("ERROR", error)
        return 1


def terminate(signum, _frame):
    raise SystemExit(128 + signum)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminate)
    sys.exit(main())
