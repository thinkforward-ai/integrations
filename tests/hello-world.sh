#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command="$root/skills/hello-world/scripts/hello-world.sh"
count=0

assert_output() {
    expected=$1
    shift
    actual=$("$command" "$@")
    if [ "$actual" != "$expected" ]; then
        printf 'FAIL: expected <%s>, got <%s>\n' "$expected" "$actual" >&2
        exit 1
    fi
    count=$((count + 1))
}

[ -x "$command" ] || {
    printf 'FAIL: command is not executable: %s\n' "$command" >&2
    exit 1
}

assert_output 'Hello, world!'
assert_output 'Hello, Ada!' 'Ada'
assert_output 'Hello, Ada Lovelace!' 'Ada Lovelace'
assert_output 'Hello, !' ''
assert_output 'Hello, %s!' '%s'
assert_output 'Hello, -n!' '-n'
assert_output 'Hello, $(printf injected); * "quotes"!' '$(printf injected); * "quotes"'
assert_output 'Usage: hello-world [NAME]' --help
assert_output 'Usage: hello-world [NAME]' -h

if output=$("$command" too many 2>&1); then
    printf '%s\n' 'FAIL: multiple names unexpectedly succeeded' >&2
    exit 1
else
    status=$?
    [ "$status" -eq 2 ] && [ "$output" = 'Usage: hello-world [NAME]' ] || {
        printf 'FAIL: unexpected error result (%s): %s\n' "$status" "$output" >&2
        exit 1
    }
    count=$((count + 1))
fi

printf 'PASS: %s hello-world checks\n' "$count"
