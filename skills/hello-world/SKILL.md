---
name: hello-world
description: Install or use the hello-world integration.
metadata:
  integration:
    id: hello-world
    command: scripts/hello-world.sh
    dependencies:
      - sh
    resources:
      - scripts/hello-world.sh
    aliases:
      hello:
        args: []
---

# Hello World

1. When installation is requested, start the shared integration installation
   workflow using this metadata. There are no extra setup steps.

2. Usage: accepts an optional name; `--help` prints usage.

3. User-run verification: with this integration selected for `hello`,
   `hello` should print `Hello, world!`; `hello Ada` should print
   `Hello, Ada!`.
