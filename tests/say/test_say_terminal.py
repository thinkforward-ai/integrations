"""Exercise real terminal keys with synthetic audio, never the microphone."""

import fcntl
import os
from pathlib import Path
import pty
import signal
import subprocess
import tempfile
import termios
import time
import unittest


COMMAND = Path(__file__).resolve().parents[2] / "skills/say/scripts/say.py"


class SayTerminalTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix="say-terminal-tests-")
        self.addCleanup(self.work.cleanup)
        self.directory = Path(self.work.name)
        scripts = {
            "arecord": (
                "import os, time\n"
                "from pathlib import Path\n"
                "Path(os.environ['SAY_TEST_RECORDER']).write_text(str(os.getpid()))\n"
                "while True:\n"
                "    os.write(1, b'\\x01\\x00' * 1600)\n"
                "    time.sleep(0.02)\n"
            ),
            "whisper-vad-speech-segments": (
                "import os, sys\n"
                "from pathlib import Path\n"
                "sys.stdin.buffer.read()\n"
                "Path(os.environ['SAY_TEST_VAD']).touch()\n"
                "print('Detected 0 speech segments:')\n"
            ),
            "whisper-cli": (
                "import sys, wave\n"
                "with wave.open(sys.stdin.buffer, 'rb') as audio:\n"
                "    frames = audio.getnframes()\n"
                "assert frames > 0\n"
                "print(f'captured {frames} samples')\n"
            ),
        }
        for name, body in scripts.items():
            script = self.directory / name
            script.write_text("#!/usr/bin/env python3\n" + body)
            script.chmod(0o755)

    def run_terminal(self, key, start_timeout="30"):
        master, slave = pty.openpty()
        original = termios.tcgetattr(slave)
        environment = {
            **os.environ,
            "PATH": str(self.directory) + os.pathsep + os.environ["PATH"],
            "SAY_TEST_RECORDER": str(self.directory / "recorder.pid"),
            "SAY_TEST_VAD": str(self.directory / "vad-ready"),
        }
        process = None
        try:
            process = subprocess.Popen(
                [str(COMMAND), "--start-timeout", start_timeout,
                 "--silence-timeout", "30", "--max-duration", "60"],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=environment, start_new_session=True, pass_fds=(slave,),
                preexec_fn=lambda: fcntl.ioctl(slave, termios.TIOCSCTTY, 0),
            )
            if key is not None:
                deadline = time.monotonic() + 5
                while not (self.directory / "vad-ready").exists():
                    if process.poll() is not None:
                        self.fail(f"say exited before capture: {process.communicate()}")
                    if time.monotonic() >= deadline:
                        self.fail("Timed out waiting for synthetic audio.")
                    time.sleep(0.01)
                current = termios.tcgetattr(slave)
                self.assertFalse(current[3] & (termios.ICANON | termios.ECHO))
                self.assertTrue(current[3] & termios.ISIG)
                os.write(master, key)
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(termios.tcgetattr(slave), original)
            recorder = int((self.directory / "recorder.pid").read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(recorder, 0)
            return process.returncode, stdout.decode(), stderr.decode()
        finally:
            if process is not None and process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    pid_file = self.directory / "recorder.pid"
                    if pid_file.exists():
                        try:
                            os.kill(int(pid_file.read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
            os.close(master)
            os.close(slave)

    def test_escape_without_enter_transcribes_to_piped_stdout(self):
        status, stdout, stderr = self.run_terminal(b"\x1b")
        self.assertEqual(status, 0, stderr)
        self.assertRegex(stdout, r"^captured [1-9]\d* samples\n$")
        self.assertIn("[STATUS] Recording finished with Esc.", stderr)
        self.assertIn("----- SPEECH TRANSCRIPT -----", stderr)
        self.assertNotIn("Speech detected.", stderr)

    def test_control_c_cancels_without_transcribing(self):
        status, stdout, stderr = self.run_terminal(b"\x03")
        self.assertEqual(status, 130, stderr)
        self.assertEqual(stdout, "")
        self.assertIn("[STATUS] Cancelled.", stderr)

    def test_automatic_timeout_restores_terminal(self):
        status, stdout, stderr = self.run_terminal(None, start_timeout="1")
        self.assertEqual(status, 2, stderr)
        self.assertEqual(stdout, "")
        self.assertIn("No speech detected before the initial timeout.", stderr)


if __name__ == "__main__":
    unittest.main()
