# Symposium 2.2.1 verification record

Date: 2026-10-26. This patch corrects the GitHub Actions toolchain used by the
[2.2.0 feature release](release_2_2_0.md). The original tag and CI failures remain
available; no released history is rewritten.

## Correction

The original action installed an older uv that rejected `uv run --no-sync`.
The workflow now pins the [upstream-documented setup action](https://github.com/astral-sh/setup-uv)
to commit `07a047e608db84b3d8c06cd9a7c7dcc9c355c18e` (v10.3.2) and installs
uv 0.13.5, the same version used for local verification. Project configuration
requires uv 0.13.5 or newer. Both Python matrix jobs run independently so a failure
on one interpreter cannot cancel evidence collection on the other.

The only Python source change from 2.2.0 is the runtime version constant.
Participant, presenter, report, calendar, and visualization behavior is unchanged.
Version metadata, lockfile, citation, and current guide references are aligned.

## Verification scope

- The feature implementation's full local baseline remains 271 passed, 8 skipped,
  and 87.96% coverage on macOS/Python 3.12.15. Its complete evidence and initial
  failures remain in the previous record.
- The patch is checked with local focused version/config/CLI tests, lint, formatting,
  locked dependency resolution, package builds/content checks, and installed-wheel
  offline onboarding scenarios.
- Successful GitHub Python 3.10 and 3.12 jobs on Linux gate tag/release publication.
  Exact run links and outcomes are recorded in the GitHub release notes.
- Independent review covers the bounded CI/version patch as a separate review.

## Organizer readiness

The 2026 workspace still contains empty templates. Add authorized registrations,
current presenter exports, and confirmed schedule information, then run strict
preflight. No live provider requests or scientific validation are implied.

See the [2026 organizer guide](2026_setup.md).
