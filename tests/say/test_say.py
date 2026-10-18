import argparse
from contextlib import nullcontext, redirect_stderr, redirect_stdout
import io
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import Mock, patch
import wave


COMMAND = Path(__file__).resolve().parents[2] / "skills/say/scripts/say.py"
say = runpy.run_path(str(COMMAND))


class SayTests(unittest.TestCase):
    def test_transcript_markers_do_not_pollute_piped_output(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            say["output_transcript"]("Hello!\nПривет!")
        self.assertEqual(stdout.getvalue(), "Hello!\nПривет!\n")
        self.assertEqual(
            stderr.getvalue(),
            "\n----- SPEECH TRANSCRIPT -----\n----- END TRANSCRIPT -----\n",
        )

    def test_each_log_line_is_labeled(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            say["log"]("ERROR", "First diagnostic.\nSecond diagnostic.")
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            stderr.getvalue(),
            "[ERROR] First diagnostic.\n[ERROR] Second diagnostic.\n",
        )

    def test_success_returns_only_speech_and_shows_markers(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(
            say["main"].__globals__,
            record=lambda args: b"",
            transcribe=lambda pcm, language: "My spoken request.",
        ), patch("shutil.which", return_value="/command"), \
             patch.object(Path, "is_file", return_value=True), \
             redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(say["main"]([]), 0)
        self.assertEqual(stdout.getvalue(), "My spoken request.\n")
        self.assertIn("----- SPEECH TRANSCRIPT -----", stderr.getvalue())
        self.assertIn("----- END TRANSCRIPT -----", stderr.getvalue())

    def test_invalid_options_are_labeled_errors(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
            say["main"](["--start-timeout", "0"])
        self.assertEqual(error.exception.code, 1)
        self.assertTrue(all(
            line.startswith(("[ERROR]", "[USAGE]"))
            for line in stderr.getvalue().splitlines()
        ))

    def test_non_speech_does_not_reset_the_timer(self):
        result = subprocess.CompletedProcess([], 0, b"Detected 0 speech segments:\n", b"")
        with patch("subprocess.run", return_value=result):
            self.assertIsNone(say["speech_end"](bytes(64000)))

    def test_speech_timestamps_use_actual_end_not_analysis_time(self):
        result = subprocess.CompletedProcess(
            [], 0, b"Detected 1 speech segments:\nSpeech segment 0: start = 58.00, end = 160.00\n", b""
        )
        with patch("subprocess.run", return_value=result):
            self.assertEqual(say["speech_end"](bytes(64000)), 1.6)

    def test_native_detector_failure_does_not_fall_back_to_volume(self):
        result = subprocess.CompletedProcess([], 1, b"", b"bad VAD model")
        with patch("subprocess.run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "bad VAD model"):
                say["speech_end"](bytes(6400))

    def test_invalid_native_output_is_an_error_even_with_exit_zero(self):
        result = subprocess.CompletedProcess([], 0, b"", b"unknown option")
        with patch("subprocess.run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "unknown option"):
                say["speech_end"](bytes(6400))

    def test_microphone_starts_before_speech_detection(self):
        recorder = Mock()
        recorder.stdout.read.return_value = bytes(6400)
        recorder.poll.return_value = None
        selector = Mock()
        selector.select.return_value = [(Mock(data="audio"), 1)]
        events = []
        args = argparse.Namespace(
            device="default", start_timeout=5, silence_timeout=5, max_duration=120
        )
        def start(*args, **kwargs):
            events.append("record")
            return recorder
        def detect(_pcm):
            events.append("detect")
            raise KeyboardInterrupt
        with patch("subprocess.Popen", side_effect=start) as popen, \
             patch.object(say["selectors"], "DefaultSelector") as factory, \
             patch.dict(say["record"].__globals__, speech_end=detect,
                        finish_key=lambda: nullcontext(None)), \
             redirect_stderr(io.StringIO()):
            factory.return_value.__enter__.return_value = selector
            with self.assertRaises(KeyboardInterrupt):
                say["record"](args)
        self.assertEqual(events, ["record", "detect"])
        self.assertIn("-B", popen.call_args.args[0])
        recorder.terminate.assert_called_once()

    def test_timeout_validation(self):
        for value in ("0", "-1", "nan", "inf", "1.5", "100000", "٥"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                say["positive_seconds"](value)
        self.assertEqual(say["positive_seconds"]("5"), 5)

    def finish_recording(self, chunks, tail=b""):
        recorder, selector = Mock(), Mock()
        recorder.stdout.read.side_effect = chunks
        selector.select.side_effect = [
            [(Mock(data="audio"), 1)] for _ in chunks
        ] + [[(Mock(data="keyboard"), 1), (Mock(data="audio"), 1)]]
        stopped = Mock(return_value=tail)
        args = argparse.Namespace(
            device="default", start_timeout=5, silence_timeout=5, max_duration=120
        )
        with patch("subprocess.Popen", return_value=recorder), \
             patch.object(say["selectors"], "DefaultSelector") as factory, \
             patch.object(say["os"], "read", return_value=b"\x1b"), \
             patch.dict(
                 say["record"].__globals__,
                 finish_key=lambda: nullcontext(17),
                 speech_end=lambda pcm: None,
                 stop=stopped,
             ), redirect_stderr(io.StringIO()):
            factory.return_value.__enter__.return_value = selector
            try:
                return say["record"](args)
            finally:
                stopped.assert_called_once_with(recorder, drain=True)

    def test_escape_keeps_full_partial_and_buffered_audio(self):
        frame = b"\x10\x20" * 3200
        partial, buffered = b"\x30\x40" * 91, b"\x50\x60" * 7
        self.assertEqual(
            self.finish_recording([frame, partial], buffered + b"\xff"),
            frame + partial + buffered,
        )

    def test_escape_keeps_speech_shorter_than_a_vad_frame(self):
        self.assertEqual(self.finish_recording([b"\x10\x20" * 10]), b"\x10\x20" * 10)

    def test_escape_keeps_audio_still_in_the_capture_pipe(self):
        self.assertEqual(self.finish_recording([], b"\x10\x20"), b"\x10\x20")

    def test_escape_without_audio_returns_no_speech(self):
        with self.assertRaisesRegex(say["NoSpeech"], "No audio recorded"):
            self.finish_recording([])

    def test_draining_stops_capture_before_reading_and_closes_the_pipe(self):
        process = Mock()
        process.poll.return_value = None
        process.stdout.fileno.return_value = 23
        process.stdout.read.return_value = b"buffered audio"
        with patch.object(say["os"], "set_blocking") as blocking:
            self.assertEqual(say["stop"](process, drain=True), b"buffered audio")
        blocking.assert_called_once_with(23, False)
        process.assert_has_calls([
            unittest.mock.call.poll(),
            unittest.mock.call.terminate(),
            unittest.mock.call.wait(timeout=2),
            unittest.mock.call.stdout.fileno(),
            unittest.mock.call.stdout.read(),
            unittest.mock.call.stdout.close(),
        ])

    def test_no_controlling_terminal_keeps_automatic_recording_available(self):
        with patch.object(say["os"], "open", side_effect=OSError):
            with say["finish_key"]() as keyboard:
                self.assertIsNone(keyboard)

    def test_background_job_does_not_change_terminal_settings(self):
        with patch.object(say["os"], "open", return_value=17), \
             patch.object(say["os"], "tcgetpgrp", return_value=2), \
             patch.object(say["os"], "getpgrp", return_value=3), \
             patch.object(say["termios"], "tcgetattr") as attributes, \
             patch.object(say["os"], "close") as close:
            with say["finish_key"]() as keyboard:
                self.assertIsNone(keyboard)
        attributes.assert_not_called()
        close.assert_called_once_with(17)

    def test_terminal_is_restored_after_success_interrupt_and_setup_failure(self):
        for outcome in ("success", "interrupt", "setup failure"):
            with self.subTest(outcome=outcome):
                original = object()
                with patch.object(say["os"], "open", return_value=17), \
                     patch.object(say["os"], "tcgetpgrp", return_value=2), \
                     patch.object(say["os"], "getpgrp", return_value=2), \
                     patch.object(say["termios"], "tcgetattr", return_value=original), \
                     patch.object(say["tty"], "setcbreak") as cbreak, \
                     patch.object(say["termios"], "tcsetattr") as restore, \
                     patch.object(say["os"], "close") as close:
                    if outcome == "setup failure":
                        cbreak.side_effect = say["termios"].error("terminal unavailable")
                    try:
                        with say["finish_key"]() as keyboard:
                            self.assertEqual(keyboard, None if outcome == "setup failure" else 17)
                            if outcome == "interrupt":
                                raise KeyboardInterrupt
                    except KeyboardInterrupt:
                        self.assertEqual(outcome, "interrupt")
                    cbreak.assert_called_once_with(17, say["termios"].TCSANOW)
                    restore.assert_called_once_with(17, say["termios"].TCSANOW, original)
                    close.assert_called_once_with(17)

    def test_audio_is_sent_as_wav_bytes_and_russian_text_is_preserved(self):
        result = subprocess.CompletedProcess([], 0, "Привет, мир!\n".encode(), b"")
        with patch("subprocess.run", return_value=result) as run, redirect_stderr(io.StringIO()):
            self.assertEqual(say["transcribe"](bytes(960), "ru"), "Привет, мир!")
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("-f") + 1], "-")
        self.assertEqual(command[command.index("-l") + 1], "ru")
        self.assertIn("-otxt", command)
        with wave.open(io.BytesIO(run.call_args.kwargs["input"]), "rb") as audio:
            self.assertEqual(audio.getframerate(), 16000)
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.readframes(480), bytes(960))

    def test_backend_errors_do_not_return_partial_text(self):
        result = subprocess.CompletedProcess([], 1, b"partial text", b"bad model")
        with patch("subprocess.run", return_value=result), redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "bad model"):
                say["transcribe"](bytes(960), "auto")

    def test_music_is_not_a_command(self):
        result = subprocess.CompletedProcess([], 0, b"[Music]", b"")
        with patch("subprocess.run", return_value=result), redirect_stderr(io.StringIO()):
            with self.assertRaises(say["NoSpeech"]):
                say["transcribe"](bytes(960), "auto")

    def test_stuck_recorder_is_killed_and_pipe_is_closed(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("arecord", 2), 0]
        say["stop"](process)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()
        process.stdout.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
