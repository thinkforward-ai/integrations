#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
SAY=${1:-$root/skills/say/scripts/say.py}
work=$(mktemp -d /tmp/say-tests.XXXXXX)
cleanup() {
    rm -f -- "$work/bin/arecord" "$work/bin/whisper-cli" "$work/pids/recorder" "$work/pids/backend"
    rmdir -- "$work/bin" "$work/pids" "$work/tmp" "$work"
}
trap cleanup EXIT
mkdir "$work/bin" "$work/pids" "$work/tmp"
export SAY_TEST_PID_DIR="$work/pids"
export TMPDIR="$work/tmp"
export PATH="$work/bin:$PATH"

cat >"$work/bin/arecord" <<'RECORDER'
#!/usr/bin/env bash
printf '%s\n' "$$" >"$SAY_TEST_PID_DIR/recorder"
if [[ ${SAY_TEST_AUDIO:-silence} == failed ]]; then
    exit 7
fi
if [[ ${SAY_TEST_AUDIO:-silence} == voice-with-music ]]; then
    exec /usr/bin/ffmpeg -nostdin -loglevel error -re \
        -f lavfi -i 'amovie=/usr/share/sounds/debian/samples/en-Wikipedia-Ignore_All_Rules.wav,atrim=duration=3,apad=pad_dur=10[voice];aevalsrc=0.03*(sin(2*PI*220*t)+0.5*sin(2*PI*330*t)+0.25*sin(2*PI*440*t)):s=16000:d=13[music];[voice][music]amix=inputs=2:duration=longest:normalize=0' \
        -ar 16000 -ac 1 -f s16le pipe:1
fi
if [[ ${SAY_TEST_AUDIO:-silence} == sample || ${SAY_TEST_AUDIO:-silence} == voice ]]; then
    exec /usr/bin/ffmpeg -nostdin -loglevel error -re \
        -f lavfi -i 'amovie=/usr/share/sounds/debian/samples/en-Wikipedia-Ignore_All_Rules.wav,atrim=duration=3,apad=pad_dur=10' \
        -ar 16000 -ac 1 -f s16le pipe:1
fi
if [[ ${SAY_TEST_AUDIO:-silence} == voice-continuous ]]; then
    exec /usr/bin/ffmpeg -nostdin -loglevel error -re \
        -f lavfi -i 'amovie=/usr/share/sounds/debian/samples/en-Wikipedia-Ignore_All_Rules.wav' \
        -ar 16000 -ac 1 -f s16le pipe:1
fi
case ${SAY_TEST_AUDIO:-silence} in
    silence) source='anullsrc=r=16000:cl=mono:d=10' ;;
    continuous) source='sine=frequency=440:sample_rate=16000:duration=10' ;;
    music) source='aevalsrc=0.08*(sin(2*PI*220*t)+0.5*sin(2*PI*330*t)+0.25*sin(2*PI*440*t)):s=16000:d=10' ;;
esac
exec /usr/bin/ffmpeg -nostdin -loglevel error -re -f lavfi -i "$source" \
    -ar 16000 -ac 1 -f s16le pipe:1
RECORDER

cat >"$work/bin/whisper-cli" <<'BACKEND'
#!/usr/bin/env bash
printf '%s\n' "$$" >"$SAY_TEST_PID_DIR/backend"
if [[ ${SAY_TEST_REAL:-0} == 1 ]]; then
    exec /usr/bin/whisper-cli "$@"
fi
dd of=/dev/null status=none
if [[ ${SAY_TEST_FAIL:-0} == 1 ]]; then
    printf 'Simulated backend failure.\n' >&2
    exit 7
fi
printf 'test transcript\n'
BACKEND
chmod 0755 "$work/bin/arecord" "$work/bin/whisper-cli"

assert_clean() {
    if [[ -n $(find "$work/tmp" -mindepth 1 -print -quit) ]]; then
        printf 'FAIL: temporary pipes remain.\n' >&2
        exit 1
    fi
    for name in recorder backend; do
        if [[ -r $work/pids/$name ]]; then
            pid=$(<"$work/pids/$name")
            state=$(ps -o stat= -p "$pid" || :)
            if [[ -n $state && $state != Z* ]]; then
                printf 'FAIL: %s process remains (%s).\n' "$name" "$pid" >&2
                exit 1
            fi
        fi
    done
}

run_case() {
    local label=$1 expected_status=$2 expected_output=$3
    shift 3
    local status=0 output
    output=$("$SAY" "$@") || status=$?
    if [[ $status != "$expected_status" || $output != "$expected_output" ]]; then
        printf 'FAIL: %s (exit %s, output %q).\n' "$label" "$status" "$output" >&2
        exit 1
    fi
    assert_clean
    printf 'PASS: %s\n' "$label"
}

run_case 'help needs no microphone' 0 "$("$SAY" --help)" --help
run_case 'invalid timeout rejected' 1 '' --start-timeout 0
SAY_TEST_AUDIO=silence run_case 'initial silence timeout' 2 '' --start-timeout 1
before=$SECONDS
SAY_TEST_AUDIO=music run_case 'loud instrumental background does not reset initial timer' 2 '' \
    --start-timeout 2 --max-duration 8
if ((SECONDS - before >= 5)); then
    printf 'FAIL: instrumental background delayed the initial timeout.\n' >&2
    exit 1
fi
before=$SECONDS
SAY_TEST_AUDIO=voice-with-music run_case 'speech ends while instrumental background continues' 0 'test transcript' \
    --start-timeout 3 --silence-timeout 1 --max-duration 8
if ((SECONDS - before >= 7)); then
    printf 'FAIL: instrumental background delayed the post-speech timeout.\n' >&2
    exit 1
fi
SAY_TEST_AUDIO=voice run_case 'speech followed by silence' 0 'test transcript' \
    --start-timeout 3 --silence-timeout 1 --max-duration 8
SAY_TEST_AUDIO=voice-continuous run_case 'maximum duration' 0 'test transcript' \
    --start-timeout 3 --max-duration 2
SAY_TEST_AUDIO=voice SAY_TEST_FAIL=1 run_case 'backend failure emits no transcript' 1 '' \
    --start-timeout 3 --silence-timeout 1 --max-duration 8
SAY_TEST_AUDIO=failed run_case 'capture failure emits no transcript' 1 '' --start-timeout 1

status=0
output=$(SAY_TEST_AUDIO=continuous env --default-signal=INT \
    timeout --foreground --preserve-status --signal=INT --kill-after=3 1 "$SAY") || status=$?
if [[ $status != 130 || -n $output ]]; then
    printf 'FAIL: cancellation (exit %s, output %q).\n' "$status" "$output" >&2
    exit 1
fi
assert_clean
printf 'PASS: cancellation stops child processes\n'

output=$(SAY_TEST_AUDIO=sample SAY_TEST_REAL=1 "$SAY" \
    --language en --start-timeout 5 --silence-timeout 1 --max-duration 12)
if [[ -z $output ]]; then
    printf 'FAIL: real transcription returned no text.\n' >&2
    exit 1
fi
assert_clean
printf 'PASS: real Whisper transcription through pipes\n'
