# Generated documentation

Files here are produced by a named script. Do not hand-edit their numbers: change
the producer and refresh, so the document and the artifact cannot disagree.

| File | Producer | What it records |
| --- | --- | --- |
| [gate-measurements.md](gate-measurements.md) | `uv run --no-sync python scripts/gate_metrics.py refresh` (or `redraw` for a wording-only change) | Wall time per `./gate.sh` arm on the host that ran it, with pytest counts and coverage; prior entries sit in a trailing `gate-metrics` JSON comment (newest 10 retained) |

`./gate.sh docs` compares the current-run table in `gate-measurements.md` with
`./gate.sh list` in both directions, so an arm cannot be added or removed without the
document following; historical tables are ignored.

Scope: one run on one host. A wall time is not a benchmark, and a recorded arm
result is not a claim that CI or another machine passed.
