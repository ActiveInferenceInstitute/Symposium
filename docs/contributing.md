# Contributing

Start with [development](development.md) and the applicable `AGENTS.md`. Reproduce
reported behavior, make a scoped change, and include evidence that a regression
scenario fails before the fix and passes afterward. Preserve shared work and
historical data. Do not commit credentials, raw registrations, private source
identifiers, or organizer receipts.

Use Python 3.12 for development and synchronize once with
`uv sync --locked --extra dev --python 3.12`. The checks are the arms of
[`./gate.sh`](../gate.sh): `./gate.sh lint`, `./gate.sh test` (full, with the
coverage gate), `./gate.sh test-fast`, `./gate.sh docs`, `./gate.sh build`,
`./gate.sh program` and `./gate.sh gnn`. Run `./gate.sh all` before proposing a
change; each arm is the exact command CI runs, and there is no separate CI-only
recipe. Follow the existing 100-character Ruff configuration and module
interfaces; document actual behavior and failure conditions.

A useful change description states the original problem, resulting behavior,
validation commands and evidence, and remaining limits. Documentation examples
must match parser help and source. Generated research claims need source review;
passing tests do not establish scientific validity. For public-program changes,
follow [organizer publication](organizing_publication.md), including private
candidate review before integration. Changes to consent or inclusion require an
organizer decision; they are never inferred from missing files.

Consult [the backlog](../TODO.md) for open work. Earlier completed items and release
reports are retained records, not fresh validation of the current tree.
