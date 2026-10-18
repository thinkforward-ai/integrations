#!/bin/sh
set -eu

if [ "$#" -gt 1 ]; then
    printf '%s\n' 'Usage: hello-world [NAME]' >&2
    exit 2
fi

case "${1-}" in
    -h|--help)
        printf '%s\n' 'Usage: hello-world [NAME]'
        exit 0
        ;;
esac

printf 'Hello, %s!\n' "${1-world}"
