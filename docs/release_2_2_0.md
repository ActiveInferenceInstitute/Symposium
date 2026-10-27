# Symposium 2.2.0 verification record

Date: 2026-10-26. Scope: software preparation for organizer-supplied 2026 data.

## Delivered behavior

- Explicit edition selection and separated input/output paths, defaulting to 2026.
- Offline initialization with no-overwrite publication, structural validation, and a
  `--require-data` gate for populated participant and presenter inputs.
- The prior survey's fourteen fields, canonical aliases, subsequent impact years,
  affirmative consent filtering, preserved textual identifiers, and rejection of
  malformed, ambiguous, duplicate, or colliding records.
- Shared runner/CLI configuration, explicit-config failure handling, safe credential
  redaction, selected report modes, and participant CLI incomplete-batch failures.
- Perplexity payment errors and column-summary payment errors propagate to stop work.
- A dependency lock, consistent version/citation metadata, Python 3.10/3.12 CI matrix,
  package build checks, and current organizer documentation.

Historical 2024/2025 inputs were compared against the original tree and remain
unchanged. The new 2026 registration CSV has headers only; no person or session has
been inferred from historical data. Source distributions exclude historical datasets,
archived projects, rendered outputs, and local agent logs; all are retained in the
repository or their original local evidence locations.

## Executed checks

Local runtime: Python 3.12.15 on macOS, with the interpreter, virtual environments,
cache, temporary files, builds, and installation environments on GitVault.

| Check | Observed outcome |
|---|---|
| Existing baseline after declaring the missing `httpx` test dependency | 188 passed, 8 skipped; 86.26% coverage |
| Final full test suite | 271 passed, 8 skipped; 87.96% coverage; 18 warnings |
| Ruff lint and formatting, including runner/launcher | Passed |
| `uv lock --check` and shell syntax check | Passed |
| Wheel and source distribution build | Passed |
| Noneditable wheel installed outside the checkout | Version 2.2.0 and installed-module containment verified |
| Installed CLI: empty scaffold, repeat init, strict empty rejection | Expected exit statuses 0, 0, 1; existing bytes preserved |
| Installed CLI: synthetic participant/presenter readiness | Strict preflight passed with one consenting participant and one presenter |
| Installed CLI: duplicate participant, missing config, missing subcommand | Expected nonzero statuses; no unintended edition created |
| Historical input diff | No changes |

The first broad candidate run had three failures: an API-error test used an invalid
CSV and never exercised its API boundary, and two visualization checks encountered
stale cached font paths. The test now uses valid consenting input and verifies the
provider was reached and its failure retained. Rendering passed with an isolated fresh
font cache. The original failing logs were preserved beside later passing evidence.
Earlier environment/dependency failures were also retained; they were not treated as
successful verification.

Raw local records include `symposium-baseline-fixed-deps.txt`,
`symposium-release-tests.txt`, `symposium-regressions-fixed.txt`,
`symposium-release-final-tests.txt`, build logs, and installed-wheel QA logs. These
remain outside the public source tree. Independent review findings and their resolution
are retained in the local agent evidence directory.

## Limits and remaining organizer work

- This is readiness to ingest the new edition's data. The actual 2026 roster,
  presenter exports, confirmed schedule, domain context, and credentials must be
  supplied by organizers. Strict preflight correctly rejects the shipped empty roster.
- Default tests make no paid requests. Live-provider tests remain opt-in and skipped;
  current credits, model availability, and generated research accuracy are unverified.
- macOS native no-replace initialization was exercised. Linux and Python 3.10 are
  configured in CI; their remote results are separate from the local evidence above.
  New edition initialization supports macOS/Linux; legacy APIs retain their existing
  platform behavior.
- Existing presenter/proposal APIs retain their per-item recovery behavior. The new
  incomplete-batch CLI check applies to participant processing; inspect individual
  errors and preflight presenter exports before generating reports.
- Warnings from small statistical fixtures and plotting-library deprecations remain.
  Generated profiles, recommendations, and proposals are drafts requiring review.

See the [2026 organizer guide](2026_setup.md) for the next operational steps.
